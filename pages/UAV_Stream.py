from ultralytics import YOLO
import streamlit as st
import cv2
import math
from threading import Thread
import time

# Create session state variables to control the detection loop
if 'stop_detection' not in st.session_state:
    st.session_state.stop_detection = False

def detect_fire():
    # Reset stop flag when starting detection
    st.session_state.stop_detection = False
    
    # Running real time from webcam
    cap = cv2.VideoCapture(r'yolo\fire5.mp4')
    model = YOLO(r'yolo\fire1.pt')
    
    # Reading the classes
    classnames = ['fire']
    
    # Create a placeholder for the video frame in Streamlit
    frame_placeholder = st.empty()
    
    while cap.isOpened() and not st.session_state.stop_detection:
        ret, frame = cap.read()
        if not ret:
            st.write("The video capture has ended.")
            break
        
        frame = cv2.resize(frame, (640, 480))
        result = model(frame, stream=True)
        
        # Getting bbox, confidence, and class names information to work with
        for info in result:
            boxes = info.boxes
            for box in boxes:
                confidence = box.conf[0]
                confidence = math.ceil(confidence * 100)
                Class = int(box.cls[0])
                if confidence > 50:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                    cv2.putText(frame, f'{classnames[Class]} {confidence}%', 
                              (x1 + 8, y1 + 100),
                              cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
        
        # Convert the frame from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Display the frame in Streamlit
        frame_placeholder.image(frame_rgb, channels="RGB")
        
        # Add a small delay to prevent the UI from becoming unresponsive
        time.sleep(0.01)
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    frame_placeholder.empty()

st.title("FIRE DETECTION FROM UAV FOOTAGE")

# Create two columns for the buttons
col1, col2 = st.columns([4,1])

# Streamlit button to start fire detection
with col1:
    if st.button("Start Detection"):
        st.write("Starting fire detection...")
        detect_fire()

# Stop button
with col2:
    if st.button("Stop Detection"):
        st.session_state.stop_detection = True
        st.write("Stopping fire detection...")