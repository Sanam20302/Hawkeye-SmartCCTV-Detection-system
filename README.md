# Hawkeye: AI-Powered Real-Time Surveillance System

## Description

Hawkeye is an advanced real-time video surveillance system designed to automatically detect, analyze, and respond to suspicious activities from live camera feeds. It combines state-of-the-art computer vision and deep learning techniques to provide intelligent monitoring and alerting.

Built using modern technologies, the system integrates object detection, tracking, and facial recognition to deliver a comprehensive and scalable security solution.

---

## Key Capabilities

Hawkeye is capable of identifying and responding to multiple types of anomalies:

- **Loitering Detection**  
  Detects individuals who remain in a monitored area beyond a defined time threshold.

- **Crowd Formation Detection**  
  Triggers alerts when the number of people exceeds a specified limit.

- **Trespassing Detection**  
  Flags individuals entering restricted or predefined zones.

- **Missing / Wanted Person Detection** 
  Compares detected faces against a database of missing or wanted individuals and triggers alerts upon a match.

---

## Face Recognition System

The system includes an intelligent facial recognition pipeline:

- Detects faces in real-time video streams  
- Generates facial embeddings for each detected face  
- Compares against:
  - **Trusted individuals database**
  - **Missing/Wanted persons database**

### Outcomes:
-  **Trusted Person** → No action required  
-  **Unknown Person (Loitering)** → Face logged for review  
-  **Match Found (Missing/Wanted Person)** → Immediate alert triggered  

---

## Real-Time Alert System

Hawkeye integrates with Telegram to send instant notifications:

-  Alerts for loitering, crowd, and trespassing events  
-  High-priority alerts when a missing or wanted person is detected  
-  Sends captured image frames along with alert messages  

This ensures authorities or monitoring personnel are notified in real time.

---

## Core Features

- **Real-Time Anomaly Detection**  
  Simultaneously monitors multiple surveillance conditions.

- **Persistent Object Tracking**  
  Uses YOLOv8 and DeepSORT to assign unique IDs and track individuals across frames.

- **Face Recognition & Verification**
  - Face detection using MTCNN  
  - Embedding generation using FaceNet (InceptionResnetV1)  
  - Identity verification against multiple databases  

- **Unknown Face Logging**  
  Saves images of unidentified individuals for further investigation.

- **Interactive Web Interface**
  - Built with Streamlit for ease of use  
  - Live video feed monitoring  
  - Alert dashboard  
  - Review panel for logged faces  

- **Dynamic Configuration**
  - Adjustable parameters:
    - Loitering time threshold  
    - Crowd count limit  
    - Restricted zone coordinates  

---

## Technologies Used

- **Application Framework:** Next.js  
- **Object Detection:** YOLOv8 (Ultralytics)  
- **Object Tracking:** DeepSORT (`deep_sort_realtime`)  
- **Face Detection:** MTCNN  
- **Face Recognition:** FaceNet (`facenet-pytorch`)  
- **Alert System:** Telegram Bot API  
- **Core Libraries:** OpenCV, PyTorch, NumPy, PIL  

---

## Future Enhancements

- Multi-camera synchronization  
- Cloud-based alert storage  
- Mobile app integration  
- Advanced behavior prediction models  

---

## Use Case

Hawkeye can be deployed in:

- Smart cities 
- Public surveillance systems  
- Airports & railway stations  
- Campus security  
- Restricted industrial zones  

---

## Author

Developed by **Sanam20302**
