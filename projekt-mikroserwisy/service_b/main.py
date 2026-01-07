from fastapi import FastAPI
from pydantic import BaseModel
import pika
import os

app = FastAPI()

class ImageRequest(BaseModel):
    url: str

def send_to_rabbit(message: str):
    rabbit_host = os.getenv('RABBIT_HOST', 'localhost') 
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
    channel = connection.channel()
    
    channel.queue_declare(queue='ai_queue', durable=True)
    
    channel.basic_publish(
        exchange='',
        routing_key='ai_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        ))
    
    connection.close()

@app.post("/count-people")
def count_people(request: ImageRequest):
    send_to_rabbit(request.url)
    
    return {"message": "Zadanie przyjęte do realizacji", "url": request.url}