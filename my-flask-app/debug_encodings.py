#!/usr/bin/env python3
"""
Script para debug dos encodings no banco de dados
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def debug_encodings():
    """Investiga os encodings armazenados no banco"""
    print("=" * 80)
    print("DEBUG DE ENCODINGS NO BANCO DE DADOS")
    print("=" * 80)
    
    try:
        # Conecta ao banco
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE')
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Busca usuários com rosto
        cursor.execute("""
            SELECT id, nome, email, rosto, LENGTH(rosto) as tamanho
            FROM usuario 
            WHERE rosto IS NOT NULL AND rosto != ''
            ORDER BY id
        """)
        
        usuarios = cursor.fetchall()
        print(f"\nUsuários encontrados: {len(usuarios)}")
        
        for usuario in usuarios:
            print(f"\n--- Usuário: {usuario['nome']} (ID: {usuario['id']}) ---")
            print(f"Email: {usuario['email']}")
            print(f"Tamanho do rosto: {usuario['tamanho']} bytes")
            
            rosto_data = usuario['rosto']
            
            # Analisa o tipo de dado
            print(f"Tipo do dado: {type(rosto_data)}")
            
            if isinstance(rosto_data, bytes):
                print(f"Primeiros 20 bytes: {rosto_data[:20]}")
                print(f"Últimos 20 bytes: {rosto_data[-20:]}")
                
                # Tenta identificar o formato
                if rosto_data.startswith(b'\x80'):
                    print("Possivelmente pickle (começa com \\x80)")
                elif rosto_data.startswith(b'{') or rosto_data.startswith(b'['):
                    print("Possivelmente JSON")
                else:
                    # Tenta como base64
                    try:
                        import base64
                        decoded = base64.b64decode(rosto_data)
                        print(f"Decodificado como base64: {len(decoded)} bytes")
                        print(f"Primeiros 20 bytes decodificados: {decoded[:20]}")
                    except:
                        print("Não é base64 válido")
                        
                        # Tenta como string direta
                        try:
                            as_str = rosto_data.decode('utf-8')
                            print(f"Como string: {as_str[:50]}...")
                        except:
                            print("Não é string UTF-8 válida")
            
            # Verifica se há algum padrão
            print(f"Hex dos primeiros 10 bytes: {rosto_data[:10].hex()}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_encodings()
