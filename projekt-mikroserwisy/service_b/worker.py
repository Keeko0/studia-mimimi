import pika
import time
import requests
import json
import os
import cv2
import numpy as np
from ultralytics import YOLO


SERVICE_A_URL = os.getenv('SERVICE_A_URL', "http://localhost:8000/results")

print("ładowanie AI")
model = YOLO('yolov8n.pt') 

def people_counter(image_url):
    #liczenie osob poprzez yolov8
    print(f"analiza zdjęcia {image_url}")
    
    try:
        #pobieranie zdjęcia
        response = requests.get(image_url, stream=True, timeout=10)
        
        #konwersja zdjęcia
        image_bytes = np.asarray(bytearray(response.content), dtype="uint8")
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if image is None:
            print("zly format")
            return 0

        #analiza yolo - w bazie COCO wyszukiwanie człowieka ma ID 0, a próg pewności ustawiłem na 25%
        results = model.predict(image, classes=[0], conf=0.25, verbose=False)
        
        #zliczanie wyników, każdy box to znaleziony obiekt
        count = len(results[0].boxes)
        
        print(f"YOLO wykryło {count} osób")
        return count

    except Exception as e:
        print(e)
        return 0

def callback(ch, method, properties, body):
    image_url = body.decode()
    print(f"odebrano {image_url}")

    person_count = people_counter(image_url)
    
    result_data = {
        "image_url": image_url,
        "person_count": person_count
    }

    try:
        response = requests.post(SERVICE_A_URL, json=result_data, timeout=5)
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"sukces, ID: {response.json().get('id')}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(f"błąd API serwisu A, {response.status_code}, reloading")
            time.sleep(5)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    except Exception as e:
        print(f"{e}, reloading")
        time.sleep(5)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_worker():
    rabbit_host = os.getenv('RABBIT_HOST', 'localhost')
    
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
            break
        except pika.exceptions.AMQPConnectionError:
            print("rabbitmq nie gotowy, 5s cd")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue='ai_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='ai_queue', on_message_callback=callback)

    print('YOLO gotowe')
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()