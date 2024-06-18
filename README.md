**Video to Audio Conversion Microservice**

![image](https://github.com/Siddhartha-19/Video_to_audio_microservices/assets/68334395/1dcc8aa2-acef-41c6-a533-12e52e60e740)

Overview

This project implements a microservice-based application for converting video files to audio files. It leverages a scalable architecture with separate services for authentication, video processing, and notifications, ensuring modularity and flexibility in handling multimedia conversions.
Key Features

    Microservices Architecture: Modular design using Python Flask for backend services.
    Database Per Service: MySQL databases for data isolation and scalability.
    JWT Authentication: Secure API Gateway with JWT tokens for user authentication and authorization.
    Firebase Storage: Efficient storage and retrieval of video and audio files.
    RabbitMQ Message Queues: Asynchronous communication between services (video_mp4 for Gateway <-> Converter Service, audio_mp3 for Converter Service <-> Notification Service).
    Real-time Notifications: Notification Service for delivering download URLs to users after conversion completion.
    
<img width="1023" alt="Screenshot 2024-06-17 at 10 34 30 PM" src="https://github.com/Siddhartha-19/Video_to_audio_microservices/assets/68334395/af97d2b0-cbf9-43f0-b767-cf450c93e17d">

<img width="1080" alt="Screenshot 2024-06-17 at 10 35 01 PM" src="https://github.com/Siddhartha-19/Video_to_audio_microservices/assets/68334395/91dcc8fb-29a2-43a5-af3a-35d2c451277b">
<img width="1089" alt="Screenshot 2024-06-17 at 10 35 11 PM" src="https://github.com/Siddhartha-19/Video_to_audio_microservices/assets/68334395/312bcd61-487d-471e-b1b7-fa17389ee2ce">

Technology Stack

    Backend: Python Flask
    Authentication: JWT Tokens, MySQL
    Storage: Firebase Storage
    Message Queue: RabbitMQ

Workflow

    User Authentication: Users log in through the API Gateway, which verifies credentials using JWT tokens.
    Video Upload: Authenticated users upload videos to Firebase Storage via the Gateway Service.
    Conversion Process: The Converter Service reads video files from Firebase Storage (video_mp4), converts them to audio files, and stores them back in Firebase        Storage. It then sends the audio download URLs to the Notification Service via RabbitMQ (audio_mp3).
    Notification: Upon successful conversion, the Notification Service sends real-time notifications containing download URLs to users.

