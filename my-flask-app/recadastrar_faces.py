#!/usr/bin/env python3
"""
Script para recadastrar os encodings faciais com o novo formato
"""

import cv2
import numpy as np
import base64
from app.utils.face_utils import FaceRecognitionUtils
from app.controllers.controller import UsuarioController
import pickle

def recadastrar_faces():
    """Recadastra todas as faces com o novo formato de encoding"""
    print("=" * 80)
    print("RECADAstrando FACES COM NOVO FORMATO")
    print("=" * 80)
    
    # Inicializa
    face_utils = FaceRecognitionUtils()
    
    # Lista usuários com rosto
    usuarios = UsuarioController.listar_usuarios_com_rosto()
    print(f"\nUsuários com rosto: {len(usuarios)}")
    
    # Para cada usuário, vamos capturar uma nova foto e atualizar
    for usuario in usuarios:
        print(f"\n--- Recadastrando: {usuario['nome']} ---")
        
        # Tenta capturar da webcam
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("Webcam encontrada! Posicione-se...")
            
            # Espera 3 segundos
            import time
            time.sleep(3)
            
            # Captura
            ret, frame = cap.read()
            if ret:
                # Detecta rosto
                faces = face_utils.detect_faces(frame)
                if faces:
                    # Usa o primeiro rosto
                    face = faces[0]
                    
                    # Extrai encoding com o novo formato
                    encoding = face_utils.extract_face_encoding(frame, face)
                    
                    if encoding is not None:
                        print(f"Novo encoding: {len(encoding)} características")
                        
                        # Converte para pickle
                        encoding_pickle = pickle.dumps(encoding)
                        
                        # Atualiza no banco
                        from app.models.models import get_db
                        conn = get_db()
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE usuario 
                            SET rosto = %s 
                            WHERE id = %s
                        """, (encoding_pickle, usuario['id']))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        print(f"✓ {usuario['nome']} atualizado com sucesso!")
                        
                        # Salva a foto capturada
                        cv2.imwrite(f"recadastro_{usuario['id']}.jpg", frame)
                    else:
                        print(f"✗ Falha ao extrair encoding de {usuario['nome']}")
                else:
                    print(f"✗ Nenhum rosto detectado para {usuario['nome']}")
            else:
                print(f"✗ Falha ao capturar imagem para {usuario['nome']}")
            
            cap.release()
        else:
            print("Webcam não encontrada")
            break
    
    print("\n✓ Recadastro concluído!")

if __name__ == "__main__":
    recadastrar_faces()
