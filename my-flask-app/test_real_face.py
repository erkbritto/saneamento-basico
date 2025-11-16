#!/usr/bin/env python3
import cv2
import numpy as np
import base64
import requests
import json

def capture_and_test_faceid():
    """Captura imagem da webcam e testa FaceID API"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('ERRO: Webcam não encontrada')
        return
    
    print('=== TESTE FACEID COM WEBCAM ===')
    print('Pressione ESPAÇO para capturar e testar ou ESC para sair...')
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print('ERRO: Falha ao capturar frame')
            break
        
        cv2.imshow('Teste FaceID - Pressione ESPAÇO', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            # Converte frame para base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            img_data_url = f"data:image/jpeg;base64,{img_base64}"
            
            print('\n=== TESTANDO API ===')
            print('Capturando imagem...')
            
            # Envia para API
            url = "http://localhost:5000/api/faceid/login"
            payload = {"image": img_data_url}
            
            try:
                response = requests.post(url, json=payload)
                print(f'Status Code: {response.status_code}')
                
                if response.status_code == 200:
                    result = response.json()
                    print('✅ SUCESSO!')
                    print(f'Mensagem: {result.get("message", "")}')
                    if 'user' in result:
                        user = result['user']
                        print(f'Usuário: {user.get("nome", "N/A")}')
                        print(f'Email: {user.get("email", "N/A")}')
                        print(f'Cargo: {user.get("cargo", "N/A")}')
                else:
                    result = response.json()
                    print('❌ Falha na autenticação')
                    print(f'Mensagem: {result.get("message", "Erro desconhecido")}')
                    
            except Exception as e:
                print(f'❌ Erro na requisição: {e}')
            
            print('\nPressione ESPAÇO para testar novamente ou ESC para sair...')
            
        elif key == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print('\n=== FIM DO TESTE ===')

if __name__ == '__main__':
    capture_and_test_faceid()
