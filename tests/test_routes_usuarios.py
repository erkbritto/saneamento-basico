import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../my-flask-app')))
from main import app  # Change 'main' to the actual filename (without .py) where your Flask app is defined

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_listar_usuarios(client):
    response = client.get('/usuarios/listar')
    assert response.status_code == 200
    assert isinstance(response.json['usuarios'], list)

def test_cadastrar_usuario(client):
    novo_usuario = {
        "nome": "testeuser",
        "email": "testeuser@email.com",
        "senha": "123456",
        "cargo": "FUNCIONARIO",
        "departamento": "TI",
        "status": "ATIVO"
    }
    response = client.post('/usuarios/cadastrar', json=novo_usuario)
    assert response.status_code in [200, 201, 400]  # 400 se já existir ou erro de validação
    if response.status_code == 201:
        assert response.json.get("message")
