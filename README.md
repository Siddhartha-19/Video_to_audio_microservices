**Video to Audio Conversion Microservice**

![image](https://github.com/Siddhartha-19/Video_to_audio_microservices/assets/68334395/1dcc8aa2-acef-41c6-a533-12e52e60e740)

Overview

This project implements a microservice-based application for converting video files to audio files. It leverages a scalable architecture with separate services for authentication, video processing, and notifications, ensuring modularity and flexibility in handling multimedia conversions.
Key Features

    Microservices Architecture: Modular design using Python Flask for backend services.
    Database Per Service: MySQL databases for data isolation and scalability.
    JWT Authentication: Secure API Gateway with JWT tokens for user authentication and authorization.
    Firebase Storage: Efficient storage and retrieval of video and audio files.
    RabbitMQ Message Queues: Asynchronous communication between microservices ('video_mp4' and 'audio_mp4').
    Real-time Notifications: Notification Service for delivering download URLs to users after conversion completion.

Technology Stack

    Backend: Python Flask
    Authentication: JWT Tokens, MySQL
    Storage: Firebase Storage
    Message Queue: RabbitMQ

Workflow

    User Authentication: Users log in through the API Gateway, which verifies credentials using JWT tokens.
    Video Upload: Authenticated users upload videos to Firebase Storage via the Gateway Service.
    Conversion Process: The Converter Service reads video files from Firebase Storage, converts them to audio files, and stores them back in Firebase Storage.
    Notification: Upon successful conversion, the Notification Service sends real-time notifications containing download URLs to users.
