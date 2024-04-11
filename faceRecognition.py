import cv2
import os
from PIL import Image
import numpy as np

faceCascade = cv2.CascadeClassifier("assets/models/haarcascade_frontalface_default.xml")
scaleFactor, minNeighbors = 1.3, 6
if not os.path.exists("assets/models/classifier.xml"):
    data_dir = "assets/storedFaces"
    path = [os.path.join(data_dir, f) for f in os.listdir(data_dir)] 
    faces = []
    ids = []
        
    for image in path:
        img = Image.open(image).convert('L')
        imageNp = np.array(img, 'uint8')
        id = int(os.path.split(image)[1].split(".")[1])

        faces.append(imageNp)
        ids.append(id)
            
    ids = np.array(ids)
        
    # Train and save classifier
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces,ids)
    clf.write("assets/models/classifier.xml")
clf = cv2.face.LBPHFaceRecognizer_create()
clf.read("assets/models/classifier.xml")

def recognize(frame):
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    features = faceCascade.detectMultiScale(gray_img, scaleFactor, minNeighbors)
     
    for (x,y,w,h) in features:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,255,255), 2 )
        id, pred = clf.predict(gray_img[y:y+h,x:x+w])
        confidence = int(100*(1-pred/300))
         
        if confidence>70:
            if id==1:
                cv2.putText(frame, "NISHAN", (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 1, cv2.LINE_AA)
            

        else: 
            cv2.putText(frame, "UNKNOWN", (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 1, cv2.LINE_AA)
     
    return frame
 
def main():
    # Open the default camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Couldn't open camera.")
        return

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Couldn't capture frame.")
            break

        # Perform fire detection on the frame
        frame = recognize(frame)

        # Display the frame with fire detection
        cv2.imshow("Detection", frame)

        # Check for user input to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

