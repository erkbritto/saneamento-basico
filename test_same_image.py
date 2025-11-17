# Testa com a mesma imagem usada no cadastro
import sys
import numpy as np
import cv2
import base64

# Remove cache
modules_to_remove = [key for key in sys.modules.keys() if key.startswith('app')]
for module in modules_to_remove:
    del sys.modules[module]

sys.path.insert(0, '.')

try:
    from app.controllers.face_recognition_controller import face_controller
    from app.models.models import get_db
    from app.utils.face_utils import FaceRecognitionUtils
    
    # Busca a imagem original do cadastro
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT rosto FROM usuario WHERE id = 1')
    usuario = cursor.fetchone()
    
    # Tenta encontrar a imagem original em algum lugar
    # Se não, vamos criar uma imagem exatamente igual à usada no cadastro
    
    # Cria uma imagem idêntica à usada no cadastro
    img = np.full((300, 300, 3), 128, dtype=np.uint8)
    center = (150, 150)
    axes = (80, 100)
    cv2.ellipse(img, center, axes, 0, 0, 360, (200, 160, 120), -1)
    cv2.circle(img, (120, 130), 12, (80, 80, 80), -1)
    cv2.circle(img, (180, 130), 12, (80, 80, 80), -1)
    cv2.ellipse(img, (150, 180), (20, 10), 0, 0, 180, (100, 80, 60), -1)
    cv2.ellipse(img, (150, 150), (8, 15), 0, 0, 360, (180, 140, 100), -1)
    
    print('=== Teste com Imagem Idêntica ===')
    
    # Extrai encoding da imagem
    faces = face_controller.detect_faces_advanced(img)
    if faces:
        face_rect = faces[0]
        test_encoding = face_controller.extract_face_features_enhanced(img, face_rect)
        print(f'Encoding extraído: {len(test_encoding)} características')
        
        # Compara com encoding do banco
        face_utils = FaceRecognitionUtils()
        db_encoding = face_utils.decode_face_encoding(usuario['rosto'])
        
        if db_encoding is not None:
            print(f'Encoding do banco: {len(db_encoding)} características')
            
            # Compara
            euclidean_dist = np.linalg.norm(test_encoding - db_encoding)
            similarity = 1 / (1 + euclidean_dist)
            
            print(f'\nDistância: {euclidean_dist:.4f}')
            print(f'Similaridade: {similarity:.4f}')
            print(f'Threshold: {face_controller.face_recognition_threshold}')
            
            if similarity > face_controller.face_recognition_threshold:
                print('✅ RECONHECIDO!')
            else:
                print('❌ Não reconhecido')
                
                # Tenta com threshold mais baixo
                if similarity > 0.01:
                    print(f'   (Seria reconhecido com threshold de {similarity:.2f})')
        else:
            print('❌ Falha ao decodificar encoding do banco')
    else:
        print('❌ Nenhum rosto detectado')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
