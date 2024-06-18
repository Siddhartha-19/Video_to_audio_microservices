from flask import Flask, request, json
import firebase_admin
from firebase_admin import credentials, firestore, storage
import google.cloud.storage
import pika
import requests
from moviepy.editor import *

import os
# os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"


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




RMQ_connection_params=pika.ConnectionParameters(host="localhost",port=5672)
RMQ_connection=pika.BlockingConnection(RMQ_connection_params)
# Creating the channel
channel=RMQ_connection.channel()
quename='video_mp4'
channel.queue_declare(queue=quename)

queuname_return='audio_mp3'
channel.queue_declare(queue=queuname_return)



def convert_file(body):
    message=json.loads(body)
    file_name=download_file(message["video_url"])
    if not file_name:
        return None
    try:
        video_file=VideoFileClip(file_name)
        video_file.audio.write_audiofile("Audio_file_"+message['username']+".mp3")
        try:
            blob = bucket.blob(f'mp3_downlaods/audio_upload_{message['username']}')
            blob.upload_from_filename("Audio_file_"+message['username']+".mp3")
            download_url = blob.generate_signed_url(version='v4', expiration=86400)
            return download_url
        except Exception as e:
            print("uploading the file failed")
            return None

    except Exception as e:
        print("Unable to convert the file")
        return None

    

def download_file(video_url):
    response=requests.get(video_url)
    if response.status_code==200:
        output_filename="downloaded_file.mp4"
        with open(output_filename,'wb') as f:
            f.write(response.content)
        return output_filename
    else:
        return None


#  ch means channel
def callback(ch,method,properties,body):
    print("called")
    converted_url=convert_file(body)
    if converted_url:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        message_we_got=json.loads(body)
        message={
            "download_audio_url":converted_url,
            "username":message_we_got['username'],
            "token":message_we_got['token']
        }
        try:
            channel.basic_publish(
            exchange='',
            routing_key=queuname_return,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
            )
        except Exception as e:
            print("unable to return the audio url")
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)




channel.basic_consume(
    queue=quename,
    # The callback function is called whenever we read the message.
    on_message_callback=callback,
    # if we keep auto_ack as True then whenever we read the message it will be removed from queue so we have to process first and then remove it
    auto_ack=False
    )


channel.start_consuming()