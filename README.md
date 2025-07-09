A real-time hand gesture recognition system that controls system volume and Spotify playback using computer vision.


Controls:
Volume:
            - Thumbs up to increase
            - Thumbs down to decrease
        Music:
            - Open palm to play/pause
            - Pointing up for next track
            - Closed fist for previous track
        'q' to quit

Prerequisites
- macOS (AppleScript used for system control)
- Python 3.7+
- Webcam
- Spotify application

Installation:
1. Clone repo
   
    git clone https://github.com/voodless/hand-gesture-control.git
    cd hand-gesture-control

3. Install required packages:
    pip install opencv-python mediapipe

4. Download a MediaPipe gesture recognition model and place it in assets/ directory

Usage
    1. Make sure spotify is running
    
    2. run the application:
    
        python main.py







