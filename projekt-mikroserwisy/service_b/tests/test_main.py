import sys
import os
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#endpoint POST /count-people
@patch("main.pika.BlockingConnection")
def test_send_to_rabbit(mock_connection):
    #przygotowanie atrapy + false object
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    #zapytanie API
    payload = {"url": "https://media.istockphoto.com/id/1977329451/photo/diverse-businesspeople-smiling-while-standing-arm-in-arm-in-an-office.jpg?s=612x612&w=0&k=20&c=FvQFfKBc7iAUPz48tdU_hzvTPCdGSntmdlceDeUuKRs="}
    response = client.post("/count-people", json=payload)

    #check
    assert response.status_code == 200
    assert response.json() == {
        "message": "zadanie przyjęte",
        "url": "https://media.istockphoto.com/id/1977329451/photo/diverse-businesspeople-smiling-while-standing-arm-in-arm-in-an-office.jpg?s=612x612&w=0&k=20&c=FvQFfKBc7iAUPz48tdU_hzvTPCdGSntmdlceDeUuKRs="
    }

    #api rabbit check
    #basic_publish check
    mock_channel.basic_publish.assert_called_once()
    
    #body url
    args, kwargs = mock_channel.basic_publish.call_args
    assert kwargs['body'] == "https://media.istockphoto.com/id/1977329451/photo/diverse-businesspeople-smiling-while-standing-arm-in-arm-in-an-office.jpg?s=612x612&w=0&k=20&c=FvQFfKBc7iAUPz48tdU_hzvTPCdGSntmdlceDeUuKRs="
    assert kwargs['routing_key'] == 'ai_queue'