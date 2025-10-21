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

def test_historico_ponto(client):
    response = client.get('/api/ponto/historico?usuario_id=1')
    assert response.status_code == 200
    assert isinstance(response.json['historico'], list)
