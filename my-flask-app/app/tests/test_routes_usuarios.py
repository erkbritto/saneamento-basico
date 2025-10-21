import pytest
from routes.routes import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_listar_usuarios(client):
    response = client.get('/usuarios/listar')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_cadastrar_usuario(client):
    novo_usuario = {
        "usuario": "testeuser",
        "cargo": "funcionario",
        "departamento": "TI",
        "status": "ativo"
    }
    response = client.post('/usuarios/cadastrar', json=novo_usuario)
    assert response.status_code in [200, 201, 400]  # 400 se já existir ou erro de validação
    if response.status_code == 201:
        assert response.json.get("message")
