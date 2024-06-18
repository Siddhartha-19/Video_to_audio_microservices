import os
from flask import Flask, request, jsonify
from access import auth_access, validator
import firebase_admin
from firebase_admin import credentials, firestore, storage
import google.cloud.storage
import pika
import json
import requests

# Path to your service account key file
service_account_path = '/Users/siddharthaneerukonda/Desktop/projects/python_projects/python_kube_system_design/gateway/firebase_storage/video-to-audio-converter-f46e4-firebase-adminsdk-3aoja-1865c0cd8d.json'

# Initialize Firebase Admin SDK with credentials
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'video-to-audio-converter-f46e4.appspot.com'
})

# Initialize Cloud Storage client with the same credentials
storage_client = google.cloud.storage.Client.from_service_account_json(service_account_path)
bucket = storage_client.bucket('video-to-audio-converter-f46e4.appspot.com')

upload_folder_path = 'upload_mp4/'

gateway_server = Flask(__name__)

@gateway_server.route("/login", methods=["POST"])
def login():
    token, err = auth_access.login(request)
    if not err:
        return jsonify(token=token), 200
    else:
        return jsonify(error=err), 401

#  localhost and port 5672 are used as default ones
RMQ_connection_params=pika.ConnectionParameters(host="localhost",port=5672)

# 'pika.BlockingConnection' for synchronous operations, 'pika.SelectConnection' for asynchronous operations
RMQ_connection = pika.BlockingConnection(RMQ_connection_params)
# Create the connection channel
channel = RMQ_connection.channel()
queue_name = 'video_mp4'
channel.queue_declare(queue=queue_name)


@gateway_server.route("/upload", methods=["POST"])
def upload():
    auth = request.headers.get('Authorization')
    access, err = validator.validate_token(request)
    if err:
        return jsonify(error=err), 401
    
    if access["admin"]:
        files = request.files
        if len(files) != 1:
            return jsonify(error="Please upload exactly one file"), 400
        
        file = list(files.values())[0]
        try:
            blob = bucket.blob("upload_folder_path/video_"+access['username'])
            blob.upload_from_file(file, content_type=file.content_type)
            download_url = blob.generate_signed_url(version='v4', expiration=86400)  # 1 hour expiration
            # publishing the download url to the RabbitMQ channel
            try:
                message={
                    "video_url":download_url,
                    "username":access["username"],   
                    "token":auth
                }
                # to serialize the dictionary into a JSON string we can use dict.json.dumps(), beacause we can only send a string as body parameter while publishing
                channel.basic_publish(
                    exchange='',
                    # Here we are using the direct exchange where the messages are routed to binding_key=routing_key
                    routing_key=queue_name,
                    body=json.dumps(message),
                    # Here in properties the delivery_mode=2 means it is persistent so, when the server restarts then the messages are saved to disk
                    properties=pika.BasicProperties(delivery_mode=2)
                    )

            
            except Exception as e:
                return jsonify(error="publishing the message failed", details=str(e)), 500


            return jsonify(message="Successful", download_url=download_url), 200
        except Exception as e:
            return jsonify(error="Upload failed, try again", details=str(e)), 500
    else:
        return jsonify(error="Not authorized"), 403

@gateway_server.route("/download", methods=["GET"])
def download():
    auth = request.headers.get('Authorization')
    access, err = validator.validate_token(request)
    if err:
        return str(err), 401

    if access["admin"]:
        audio_url = request.args.get("download_url")
        if audio_url:
            response = requests.get(audio_url)
            if response.status_code == 200:
                output_filename = "downloaded_file_" + request.args.get("username") + ".mp4"
                with open(output_filename, 'wb') as f:
                    f.write(response.content)
                return jsonify({"message": output_filename + " downloaded"}), 200
            else:
                return "Unable to download file", 401
        else:
            return "No audio url provided", 400
    else:
        return "Unauthorized user", 401


if __name__ == "__main__":
    gateway_server.run(host="0.0.0.0", port=8080)
