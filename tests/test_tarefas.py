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

def test_listar_tarefas_funcionario(client):
    response = client.get('/api/tarefas?usuario_id=1')
    assert response.status_code == 200
    assert isinstance(response.json['tarefas'], list)
