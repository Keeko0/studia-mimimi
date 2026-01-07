import sys
import os
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Testujemy endpoint POST /count-people
# Używamy @patch, żeby podmienić 'pika.BlockingConnection' na naszą atrapę
@patch("main.pika.BlockingConnection")
def test_send_to_rabbit(mock_connection):
    # 1. Przygotowanie atrapy
    # Kiedy kod poprosi o kanał (connection.channel()), dajemy mu fałszywy obiekt
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # 2. Wykonanie zapytania do API
    payload = {"url": "http://test-image.com/img.jpg"}
    response = client.post("/count-people", json=payload)

    # 3. Sprawdzenia (Asercje)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Zadanie przyjęte do realizacji",
        "url": "http://test-image.com/img.jpg"
    }

    # 4. Sprawdzamy, czy API faktycznie próbowało wysłać coś do Rabbita
    # Czy funkcja basic_publish została wywołana?
    mock_channel.basic_publish.assert_called_once()
    
    # Możemy nawet sprawdzić, czy wysłano dobry URL w body
    args, kwargs = mock_channel.basic_publish.call_args
    assert kwargs['body'] == "http://test-image.com/img.jpg"
    assert kwargs['routing_key'] == 'ai_queue'