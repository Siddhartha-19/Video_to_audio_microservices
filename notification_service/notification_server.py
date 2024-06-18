import os
import pika
import json
import requests

rmq_connection_params = pika.ConnectionParameters(host="localhost", port=5672)
rmq_connection = pika.BlockingConnection(rmq_connection_params)
rmq_channel = rmq_connection.channel()

audio_queue_name = 'audio_mp3'
rmq_channel.queue_declare(queue=audio_queue_name)

def send_notification(body):
    message = json.loads(body)
    response = requests.get(url='http://127.0.0.1:8080/download', params={
        "download_url": message["download_audio_url"],
        "username": message["username"],
    }, headers={
        "Authorization": message["token"]
    })
    if response.status_code == 200:
        print(response.json()["message"])
        return None, response.json()["message"]
    else:
        print(response.text)
        return response.text, None

def callback(ch, method, properties, body):
    # Instead of sending an email I am just doing an HTTP request to the gateway.
    err, message = send_notification(body)
    if err:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    else:
        ch.basic_ack(delivery_tag=method.delivery_tag)

rmq_channel.basic_consume(
    queue=audio_queue_name,
    on_message_callback=callback,
    auto_ack=False,
)

rmq_channel.start_consuming()
