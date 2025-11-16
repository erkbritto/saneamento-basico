#!/usr/bin/env python3
import cv2
import numpy as np
from app.utils.face_utils import FaceRecognitionUtils
from app.controllers.controller import UsuarioController

def test_ultra_permissive():
    """Testa o sistema ultra permissivo de reconhecimento facial"""
    print('=== TESTE DO SISTEMA ULTRA PERMISSIVO ===')
    
    # Inicia a webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('ERRO: Webcam não encontrada')
        return
    
    print('Webcam encontrada! Pressione ESPAÇO para capturar ou ESC para sair...')
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print('ERRO: Falha ao capturar frame')
            break
        
        # Mostra o frame
        cv2.imshow('FaceID Ultra Permissivo - Pressione ESPAÇO para testar', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            print('\n=== TESTANDO RECONHECIMENTO ===')
            
            # Testa com o sistema ultra permissivo
            face_utils = FaceRecognitionUtils()
            result = face_utils.authenticate_any_face(frame)
            
            print(f'Resultado: {result}')
            
            if result.get('success'):
                print('✅ ROSTO RECONHECIDO!')
                print(f'Usuário: {result["user"]["nome"]}')
                print(f'Confiança: {result.get("confidence", 0):.2f}')
                print(f'Distância: {result.get("distance", 0):.6f}')
                
                # Teste adicional: verificação de liveness (simples)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                edges = cv2.Canny(blur, 50, 150)
                edge_count = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                liveness_result = "vivo" if edge_count > 0.01 else "possível spoof"
                print(f'Verificação de liveness simples: {liveness_result} (edge density: {edge_count:.4f})')
                
            else:
                print(f'❌ Rosto não reconhecido: {result.get("message", "Erro desconhecido")}')
            
            # Continua testando
            print('\nPressione ESPAÇO para testar novamente ou ESC para sair...')
            
        elif key == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print('\n=== FIM DO TESTE ===')

if __name__ == '__main__':
    test_ultra_permissive()
