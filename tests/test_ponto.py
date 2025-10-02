import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../my-flask-app')))
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_registrar_ponto(client):
    ponto = {
        "usuario_id": 1,
        "data": "2025-09-26",
        "hora_entrada": "08:00:00",
        "localizacao": "-23.5505,-46.6333"
    }
    response = client.post('/api/ponto/registrar', json=ponto)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert "Ponto registrado" in response.json["message"]
