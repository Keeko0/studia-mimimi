import pika
import time
import requests
import json
import os
import cv2
import numpy as np
from ultralytics import YOLO

# Pobieramy adres Serwisu A
SERVICE_A_URL = os.getenv('SERVICE_A_URL', "http://localhost:8000/results")

# Ładujemy model globalnie, żeby nie wczytywał się przy każdym zdjęciu od nowa
# 'yolov8n.pt' to wersja Nano (najszybsza)
print(" [!] Ładowanie modelu AI (może chwilę potrwać przy 1. uruchomieniu)...")
model = YOLO('yolov8n.pt') 

def people_counter(image_url):
    """
    Używa sieci neuronowej YOLOv8 do liczenia osób.
    """
    print(f" [x] Pobieram i analizuję zdjęcie: {image_url}")
    
    try:
        # 1. Pobranie zdjęcia (tak jak wcześniej)
        response = requests.get(image_url, stream=True, timeout=10)
        if response.status_code != 200:
            print(" [!] Błąd: Nie udało się pobrać zdjęcia.")
            return 0
        
        # 2. Konwersja na format obrazu
        image_bytes = np.asarray(bytearray(response.content), dtype="uint8")
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if image is None:
            print(" [!] Błąd: Niepoprawny plik obrazu.")
            return 0

        # 3. Analiza YOLO
        # classes=[0] oznacza, że szukamy tylko klasy "person" (w bazie COCO to ID 0)
        # conf=0.25 to próg pewności (25%)
        # verbose=False wyłącza spamowanie logami przez bibliotekę
        results = model.predict(image, classes=[0], conf=0.25, verbose=False)
        
        # 4. Zliczanie wyników
        # results[0].boxes to lista znalezionych obiektów
        count = len(results[0].boxes)
        
        print(f" [v] YOLO znalazło {count} osób.")
        return count

    except Exception as e:
        print(f" [!] Błąd podczas analizy AI: {e}")
        return 0

def callback(ch, method, properties, body):
    image_url = body.decode()
    print(f" [x] Odebrano zadanie dla: {image_url}")

    # Wywołanie funkcji AI
    person_count = people_counter(image_url)
    
    result_data = {
        "image_url": image_url,
        "person_count": person_count
    }

    try:
        response = requests.post(SERVICE_A_URL, json=result_data, timeout=5)
        
        if response.status_code == 200 or response.status_code == 201:
            print(f" [v] SUKCES: Wynik zapisany w Serwisie A! ID: {response.json().get('id')}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(f" [!] BŁĄD API Serwisu A: {response.status_code}. Ponawiam...")
            time.sleep(5)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    except Exception as e:
        print(f" [!] AWARIA POŁĄCZENIA z Serwisem A: {e}. Ponawiam...")
        time.sleep(5)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_worker():
    rabbit_host = os.getenv('RABBIT_HOST', 'localhost')
    
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
            break
        except pika.exceptions.AMQPConnectionError:
            print(" [!] RabbitMQ nie gotowy, czekam 5s...")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue='ai_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='ai_queue', on_message_callback=callback)

    print(' [*] Czekam na wiadomości. Model YOLO gotowy.')
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()