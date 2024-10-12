# PRJ300
## Facial Recognition Security Application
### Project Overview
This project implements a facial recognition-based security system using Python scripts and AWS services. The system runs on a Raspberry Pi 4 with a connected face detection screen, a button, and an electronic lock. AWS Rekognition is used to verify faces, and the electronic lock is activated only when an authorized face is recognized. The facial data is stored securely using Amazon S3, and the system interacts with AWS services through API Gateway.

# Team Members

- Craig Lawson (S00209542)
- Jack McElroy (S00209393)
- Sean Dowdall (S00210945)
- Gatis Berzins (S00209875)

# Programme of Study
Degree: BSc Hons Computing (Level 8)
Year: 3
Project Proposal
Context
Cybersecurity continues to grow in importance as organizations look for stronger ways to protect user data. In this project, we explore the integration of facial recognition technology into security systems, with a focus on utilizing cloud-based services for facial verification. This solution can be used to control physical access by locking or unlocking doors based on facial recognition.

# Solution
We developed a system that:

- Utilizes AWS Rekognition to detect and verify faces based on a pre-configured list of authorized individuals.
- Controls an electronic lock that activates when an authorized face is verified.
- Uses a Raspberry Pi 4, wired with a face detection screen, button, and electronic lock for local execution.
- Stores reference images in Amazon S3 for cloud-based facial recognition.
- Integrates AWS API Gateway to facilitate communication between the Raspberry Pi and AWS Rekognition.

# Key Features
- Facial Verification: The system uses AWS Rekognition to detect and verify faces against authorized face profiles stored in Amazon S3.
- Physical Security: Upon successful verification, the Raspberry Pi triggers the electronic lock to grant access.
- User-Friendly Interface: The system uses a face detection screen connected to the Raspberry Pi for real-time monitoring.
- Secure Storage: Facial images are securely stored in Amazon S3, ensuring scalability and safety.

# Technology Stack
The application is developed using:

Language: Python (for Raspberry Pi control scripts and AWS integration)
Cloud Services:
- AWS Rekognition (for facial recognition)
- Amazon S3 (for storing reference images)
- AWS API Gateway (for API communication between the Pi and AWS services)
- Hardware: Raspberry Pi 4, face detection screen, electronic lock, and button.
