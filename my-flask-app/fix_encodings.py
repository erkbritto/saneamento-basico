#!/usr/bin/env python3
"""
Script para corrigir os encodings no banco de dados
"""

import mysql.connector
import os
import numpy as np
import pickle
import base64
from dotenv import load_dotenv

load_dotenv()

def fix_encodings():
    """Corrige os encodings armazenados incorretamente no banco"""
    print("=" * 80)
    print("CORRIGINDO ENCODINGS NO BANCO DE DADOS")
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
            SELECT id, nome, email, rosto
            FROM usuario 
            WHERE rosto IS NOT NULL AND rosto != ''
            ORDER BY id
        """)
        
        usuarios = cursor.fetchall()
        print(f"\nUsuários encontrados: {len(usuarios)}")
        
        for usuario in usuarios:
            print(f"\n--- Processando usuário: {usuario['nome']} (ID: {usuario['id']}) ---")
            
            rosto_data = usuario['rosto']
            
            # Tenta decodificar o encoding atual
            try:
                # O dado está como base64 no banco
                if isinstance(rosto_data, bytes):
                    # Decodifica de base64 para bytes
                    decoded_bytes = base64.b64decode(rosto_data)
                    print(f"Decodificado {len(decoded_bytes)} bytes")
                    
                    # Converte para numpy array
                    encoding = np.frombuffer(decoded_bytes, dtype=np.float64)
                    print(f"Encoding com {len(encoding)} características")
                    
                    # Salva de volta como pickle
                    encoding_pickle = pickle.dumps(encoding)
                    print(f"Pickle size: {len(encoding_pickle)} bytes")
                    
                    # Atualiza no banco
                    cursor.execute("""
                        UPDATE usuario 
                        SET rosto = %s 
                        WHERE id = %s
                    """, (encoding_pickle, usuario['id']))
                    
                    print(f"✓ Usuário {usuario['nome']} atualizado com sucesso!")
                    
            except Exception as e:
                print(f"✗ Erro ao processar usuário {usuario['nome']}: {e}")
                continue
        
        # Confirma as alterações
        conn.commit()
        print("\n✓ Todas as alterações foram salvas no banco!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_encodings()
