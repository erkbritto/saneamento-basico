# Testa se a imagem original do cadastro está disponível
import sys
sys.path.insert(0, '.')

from app.models.models import get_db

try:
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nome FROM usuario WHERE rosto IS NOT NULL AND rosto != ""')
    usuarios = cursor.fetchall()
    
    print(f'Usuários com rosto cadastrado: {len(usuarios)}')
    for u in usuarios:
        print(f'- ID: {u["id"]}, Nome: {u["nome"]}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Erro: {e}')
