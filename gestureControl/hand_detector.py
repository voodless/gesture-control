import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from utilities.CvFpsCalc import CvFpsCalc
import time
import os
import subprocess

def get_volume_mac():
    try:
        output = subprocess.check_output(['osascript','-e','output volume of (get volume settings)'])
        return int(output.decode("utf-8").strip())
    except:
        return 50  # fallback volume

class HandDetector():
    def __init__(self, gesture_path):
        self.gesture_path = gesture_path
        self.BaseOptions = mp.tasks.BaseOptions
        self.GestureRecognizer = mp.tasks.vision.GestureRecognizer
        self.GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        
        self.HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]

    def run(self):
        # asynchronous setup
        options = self.GestureRecognizerOptions(
            base_options=self.BaseOptions(model_asset_path=self.gesture_path),
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )

        with self.GestureRecognizer.create_from_options(options) as recognizer:
            cap = cv.VideoCapture(1)
            fps_calc = CvFpsCalc(buffer_len=10)
            volume = get_volume_mac()
            last_volume_update = 0
            last_gesture_action = 0
            volume_delay = 0.1
            gesture_delay = 0.5

            if not cap.isOpened():
                print("Error: Could not open camera")
                return

            while True:
                now = time.time()
                fps = fps_calc.get()
                success, frame = cap.read()
                if not success:
                    print("Failed to read from camera")
                    break

                frame = cv.flip(frame, 1)
                rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                try:
                    result = recognizer.recognize(mp_image)
                except:
                    result = None

                # gesture handling
                if result and result.gestures:
                    top_gesture = result.gestures[0][0].category_name

                    if top_gesture == "Thumb_Up":
                        if now - last_volume_update > volume_delay and volume < 100:
                            volume = min(100, volume + 2)
                            last_volume_update = now                            
                            os.system(f"osascript -e 'set volume output volume {volume}'")
                            
                    elif top_gesture == "Thumb_Down":
                        if now - last_volume_update > volume_delay and volume > 0:
                            volume = max(0, volume - 2)
                            last_volume_update = now
                            os.system(f"osascript -e 'set volume output volume {volume}'")
                            
                    elif top_gesture == "Open_Palm":
                        if now - last_gesture_action > gesture_delay:
                            last_gesture_action = now
                            os.system("osascript -e 'tell application \"Spotify\" to playpause'")

                    elif top_gesture == "Pointing_Up":
                        if now - last_gesture_action > gesture_delay:
                            last_gesture_action = now
                            os.system("osascript -e 'tell application \"Spotify\" to next track'")
                    elif top_gesture == "Closed_Fist":
                        if now - last_gesture_action > gesture_delay:
                            last_gesture_action = now
                            os.system("osascript -e 'tell application \"Spotify\" to previous track'")



                # landmarks
                if result:
                    for hand_landmarks in result.hand_landmarks:
                        landmark_points = [
                            (int(l.x * frame.shape[1]), int(l.y * frame.shape[0]))
                            for l in hand_landmarks
                        ]
                        
                        # connections
                        for idx_start, idx_end in self.HAND_CONNECTIONS:
                            if idx_start < len(landmark_points) and idx_end < len(landmark_points):
                                cv.line(frame, landmark_points[idx_start], landmark_points[idx_end], (255, 255, 255), 2)
                        
                        # landmark drawing
                        for x, y in landmark_points:
                            cv.circle(frame, (x, y), 5, (0, 255, 0), -1)
                            
                    # gesture names
                    if result.gestures:
                        gesture_name = result.gestures[0][0].category_name
                        cv.putText(frame, f'Gesture: {gesture_name}', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                # simple ui
                cv.rectangle(frame, (10, 580), (10 + volume * 3, 600), (0, 255, 0), -1)
                cv.putText(frame, f'FPS: {fps:.1f}', (10, 500), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv.putText(frame, f'Volume: {volume}', (10, 530), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv.imshow("Gesture Recognizer", frame)

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv.destroyAllWindows()
