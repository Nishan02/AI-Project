import cv2
from ultralytics import YOLO
import datetime
import os
import threading
# import send_email
import flags
import winsound
import smtplib
import ssl
from email.message import EmailMessage
import imghdr
import fireDetection

model = YOLO("assets/models/fireModel.pt")
classnames = ["fire"]

output_path = "_"

def reset_fire_flag():
    flags.fire_email = False
    
def beep_alarm():
    for _ in range(3):
        print("ALARM: Fire Detected!")
        winsound.Beep(2500, 1000)  # Beep alarm sound (2500 Hz for 1 second)

def fire_detection(frame):
    output_folder = "Captured"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    result = model(frame, stream=True)

    for info in result:
        for box in info.boxes:
            confidence = box.conf[0] * 100
            class_id = int(box.cls[0])
            if confidence > 50 and class_id == 0:  # Adjust threshold and class index as needed
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)
                cv2.putText(frame, f"Fire: {confidence:.2f}%", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                if not flags.fire_email:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    global output_path
                    output_path = "_"
                    output_path = os.path.join(output_folder, f"fire_{timestamp}.jpg")
                    cv2.imwrite(output_path, frame)
                    flags.fire_email = True
                    message = "Fire Alert"
                    # read(target=send_email, args=[message, output_path]).start()
                    threading.Thread(target=beep_alarm).start()  # Start alarm sound in a new thread
                    
                    flags.gen_report()
                    
                    # Sending the email
                    time = datetime.datetime.now().strftime("%H:%M  %a,  %b%y")
                    email_sender = "dailydiscovery678@gmail.com"
                    # email_password = os.environ.get('PY_PASS')
                    email_password = "ygdxmbrzfakreasx"
                    email_receiver = flags.email
                    
                    # Set the subject and body of the email
                    subject = 'Alert: Fire Detected'
                    body = f"""
                    Name: {flags.name}  
                    Time : {time}
                                
                    Detected Events : ->
                    Fire was detected!!
                    """

                    em = EmailMessage()
                    em['From'] = email_sender
                    em['To'] = email_receiver
                    em['Subject'] = subject
                    em.set_content(body)

                    with open(fireDetection.output_path, 'rb') as f:
                        file_data = f.read()
                        file_type = imghdr.what(f.name)
                        file_name = f.name
                                
                    em.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)
                                
                    # Add SSL (layer of security)
                    context = ssl.create_default_context()

                    # Log in and send the email
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                        smtp.login(email_sender, email_password)
                        smtp.send_message(em)
                    
                    threading.Thread(target=reset_fire_flag).start()  # Reset fire_email flag after some delay


    return frame

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Couldn't open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't capture frame.")
            break

        frame_with_fire = fire_detection(frame)

        cv2.imshow("Fire Detection", frame_with_fire)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
