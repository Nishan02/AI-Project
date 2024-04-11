import threading
import winsound
import cv2

alarm = False
alarm_count = 0

def beep_alarm():
    global alarm_count, alarm
    for _ in range(3):
        print("Motion detected")
        winsound.Beep(2500, 1000)
    alarm_count = 0
    alarm = False

def motionDetector(frame, bg_subtractor):
    global alarm_count, alarm

    # Apply background subtraction
    fg_mask = bg_subtractor.apply(frame)

    # Thresholding
    threshold = cv2.threshold(fg_mask, 25, 255, cv2.THRESH_BINARY)[1]

    # Count white pixels (motion)
    motion_pixels = cv2.countNonZero(threshold)

    if motion_pixels > 500:  # Adjust threshold as needed
        alarm_count += 1
    else:
        alarm_count = max(0, alarm_count - 1)

    if alarm_count > 20 and not alarm:
        alarm = True
        threading.Thread(target=beep_alarm).start()

def main():
    cam = cv2.VideoCapture(0)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    while True:
        ret, frame = cam.read()

        # Resize frame
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        cv2.imshow("Video", frame)

        # Process frame for motion detection
        motionDetector(frame, bg_subtractor)

        if cv2.waitKey(20) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
