# Testa decodificacao do encoding
import pickle
import base64
import numpy as np
import sys
sys.path.insert(0, '.')

from app.models.models import get_db

try:
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nome, rosto FROM usuario WHERE rosto IS NOT NULL AND rosto != ""')
    usuarios = cursor.fetchall()
    
    for usuario in usuarios:
        print(f'Usuário: {usuario["nome"]} (ID: {usuario["id"]})')
        rosto_data = usuario['rosto']
        
        if isinstance(rosto_data, bytes):
            print(f'Tipo: bytes, Tamanho: {len(rosto_data)}')
            
            # Testa pickle
            try:
                encoding = pickle.loads(rosto_data)
                print(f'✅ Pickle funcionou: {len(encoding)} características')
                print(f'Tipo: {type(encoding)}, Shape: {encoding.shape if hasattr(encoding, "shape") else "N/A"}')
            except Exception as e:
                print(f'❌ Pickle falhou: {e}')
                
                # Testa direto como numpy
                try:
                    encoding = np.frombuffer(rosto_data, dtype=np.float64)
                    print(f'✅ Numpy direto: {len(encoding)} características')
                except Exception as e2:
                    print(f'❌ Numpy falhou: {e2}')
                    
                    # Testa base64
                    try:
                        encoding_str = base64.b64encode(rosto_data).decode('utf-8')
                        encoding_bytes = base64.b64decode(encoding_str)
                        encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                        print(f'✅ Base64 funcionou: {len(encoding)} características')
                    except Exception as e3:
                        print(f'❌ Base64 falhou: {e3}')
        else:
            print(f'Tipo: {type(rosto_data)}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Erro: {e}')
    import traceback
    traceback.print_exc()
