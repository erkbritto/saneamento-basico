#!/usr/bin/env python3
"""
Script de teste para debug do reconhecimento facial
"""

import cv2
import numpy as np
import base64
from app.utils.face_utils import FaceRecognitionUtils
from app.controllers.controller import UsuarioController

def test_face_recognition():
    """Testa o reconhecimento facial com logs detalhados"""
    print("=" * 80)
    print("TESTE DE RECONHECIMENTO FACIAL - DEBUG DETALHADO")
    print("=" * 80)
    
    # Inicializa o utilitário
    face_utils = FaceRecognitionUtils()
    
    # Lista usuários com rosto cadastrado
    print("\n1. VERIFICANDO USUÁRIOS CADASTRADOS...")
    usuarios = UsuarioController.listar_usuarios_com_rosto()
    print(f"Total de usuários com rosto: {len(usuarios)}")
    
    for usuario in usuarios:
        print(f"\n--- Usuário: {usuario['nome']} (ID: {usuario['id']}) ---")
        print(f"Email: {usuario['email']}")
        print(f"Rosto tem dados: {'Sim' if usuario['rosto'] else 'Não'}")
        
        if usuario['rosto']:
            try:
                # Tenta decodificar o encoding
                stored_encoding = face_utils.decode_face_encoding(usuario['rosto'])
                if stored_encoding is not None:
                    print(f"Encoding decodificado: {len(stored_encoding)} características")
                    print(f"Tipo: {type(stored_encoding)}")
                    print(f"Primeiros 10 valores: {stored_encoding[:10]}")
                    print(f"Min/Max: {np.min(stored_encoding):.6f} / {np.max(stored_encoding):.6f}")
                    print(f"Mean/Std: {np.mean(stored_encoding):.6f} / {np.std(stored_encoding):.6f}")
                else:
                    print("ERRO: Falha ao decodificar encoding")
            except Exception as e:
                print(f"ERRO ao decodificar encoding: {e}")
    
    # Testa com uma imagem de exemplo (se existir)
    print("\n2. TESTANDO COM IMAGEM DE EXEMPLO...")
    
    # Verifica se há webcam disponível
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("Webcam encontrada! Capturando imagem para teste...")
        ret, frame = cap.read()
        if ret:
            # Salva a imagem capturada
            cv2.imwrite("test_capture.jpg", frame)
            print("Imagem salva como 'test_capture.jpg'")
            
            # Converte para base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Testa detecção
            print("\n3. TESTANDO DETECÇÃO DE ROSTO...")
            faces = face_utils.detect_faces(frame)
            print(f"Rostos detectados: {len(faces)}")
            
            if faces:
                for i, (x, y, w, h) in enumerate(faces):
                    print(f"Rosto {i+1}: ({x}, {y}, {w}, {h})")
                    # Desenha retângulo na imagem
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Salva imagem com rostos marcados
                cv2.imwrite("test_faces_detected.jpg", frame)
                print("Imagem com rostos detectados salva como 'test_faces_detected.jpg'")
                
                # Testa extração de encoding
                print("\n4. TESTANDO EXTRAÇÃO DE ENCODING...")
                encoding = face_utils.extract_face_encoding(frame, faces[0])
                if encoding is not None:
                    print(f"Encoding extraído: {len(encoding)} características")
                    print(f"Primeiros 10 valores: {encoding[:10]}")
                    print(f"Min/Max: {np.min(encoding):.6f} / {np.max(encoding):.6f}")
                    print(f"Mean/Std: {np.mean(encoding):.6f} / {np.std(encoding):.6f}")
                    
                    # Compara com usuários cadastrados
                    print("\n5. TESTANDO COMPARAÇÃO COM USUÁRIOS...")
                    for usuario in usuarios:
                        if usuario['rosto']:
                            try:
                                stored_encoding = face_utils.decode_face_encoding(usuario['rosto'])
                                if stored_encoding is not None:
                                    # Verifica se têm o mesmo tamanho
                                    if len(encoding) == len(stored_encoding):
                                        distance = np.linalg.norm(encoding - stored_encoding)
                                        print(f"Distância com {usuario['nome']}: {distance:.6f}")
                                        
                                        # Thresholds
                                        thresholds = [0.6, 1.0, 2.0, 5.0]
                                        for threshold in thresholds:
                                            if distance < threshold:
                                                print(f"  ✓ RECONHECIDO com threshold {threshold}")
                                                break
                                        else:
                                            print(f"  ✗ Não reconhecido (thresholds testados)")
                                    else:
                                        print(f"Tamanhos diferentes: encoding={len(encoding)}, stored={len(stored_encoding)}")
                            except Exception as e:
                                print(f"Erro ao comparar com {usuario['nome']}: {e}")
                else:
                    print("ERRO: Falha ao extrair encoding")
            else:
                print("Nenhum rosto detectado na imagem")
        else:
            print("ERRO: Falha ao capturar imagem da webcam")
        
        cap.release()
    else:
        print("Webcam não encontrada")
    
    print("\n" + "=" * 80)
    print("FIM DO TESTE")
    print("=" * 80)

if __name__ == "__main__":
    test_face_recognition()
