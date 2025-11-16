#!/usr/bin/env python3
import cv2
import numpy as np
from app.utils.face_utils import FaceRecognitionUtils

def debug_encoding_shapes():
    """Debug para verificar o shape dos encodings extraídos"""
    print('=== DEBUG DE ENCODING SHAPES ===')
    
    # Inicia a webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('ERRO: Webcam não encontrada')
        return
    
    print('Webcam encontrada! Pressione ESPAÇO para capturar...')
    
    face_utils = FaceRecognitionUtils()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print('ERRO: Falha ao capturar frame')
            break
        
        cv2.imshow('Debug Encoding Shapes - Pressione ESPAÇO', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            print('\n=== ANALISANDE ENCODINGS ===')
            
            # Detecta rostos
            faces = face_utils.detect_faces(frame)
            print(f'Rostos detectados: {len(faces)}')
            
            if faces:
                # Pega o maior rosto
                largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                print(f'Maior rosto: {largest_face}')
                
                # Testa extract_face_encoding
                print('\n--- Testando extract_face_encoding ---')
                encoding_single = face_utils.extract_face_encoding(frame, largest_face)
                if encoding_single is not None:
                    print(f'extract_face_encoding shape: {encoding_single.shape}')
                else:
                    print('extract_face_encoding retornou None')
                
                # Testa extract_multiple_encodings
                print('\n--- Testando extract_multiple_encodings ---')
                encodings_multiple = face_utils.extract_multiple_encodings(frame, largest_face)
                if encodings_multiple:
                    for i, enc in enumerate(encodings_multiple):
                        print(f'Encoding {i+1} shape: {enc.shape}')
                else:
                    print('extract_multiple_encodings retornou lista vazia')
                
                # Verifica componentes individuais
                print('\n--- Analisando componentes ---')
                x, y, w, h = largest_face
                x1 = max(0, x - 20)
                y1 = max(0, y - 20)
                x2 = min(frame.shape[1], x + w + 20)
                y2 = min(frame.shape[0], y + h + 20)
                
                face_roi = frame[y1:y2, x1:x2]
                face_roi = cv2.resize(face_roi, (100, 100))
                
                gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
                hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
                
                # Verifica histogramas
                hist_gray = cv2.calcHist([gray], [0], None, [101], [0, 256])
                hist_h = cv2.calcHist([hsv], [0], None, [1], [0, 180])
                hist_s = cv2.calcHist([hsv], [1], None, [1], [0, 256])
                
                print(f'hist_gray shape: {hist_gray.shape}')
                print(f'hist_h shape: {hist_h.shape}')
                print(f'hist_s shape: {hist_s.shape}')
                print(f'gray.mean(): {gray.mean()}, gray.std(): {gray.std()}')
                
                # Verifica concatenação
                features = np.concatenate([
                    hist_gray.flatten(),
                    hist_h.flatten(),
                    hist_s.flatten(),
                    [gray.mean(), gray.std()]
                ])
                print(f'Features concatenadas shape: {features.shape}')
            
            print('\nPressione ESPAÇO para analisar novamente ou ESC para sair...')
            
        elif key == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print('\n=== FIM DO DEBUG ===')

if __name__ == '__main__':
    debug_encoding_shapes()
