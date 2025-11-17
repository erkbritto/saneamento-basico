# Testa comparacao de encodings
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
    
    # Cria imagem de teste similar a do usuario
    img = np.full((300, 300, 3), 128, dtype=np.uint8)
    center = (150, 150)
    axes = (80, 100)
    cv2.ellipse(img, center, axes, 0, 0, 360, (200, 160, 120), -1)
    cv2.circle(img, (120, 130), 12, (80, 80, 80), -1)
    cv2.circle(img, (180, 130), 12, (80, 80, 80), -1)
    cv2.ellipse(img, (150, 180), (20, 10), 0, 0, 180, (100, 80, 60), -1)
    cv2.ellipse(img, (150, 150), (8, 15), 0, 0, 360, (180, 140, 100), -1)
    
    print('=== Teste de Comparacao de Encodings ===')
    
    # Extrai encoding da imagem de teste
    faces = face_controller.detect_faces_advanced(img)
    if faces:
        face_rect = faces[0]
        test_encoding = face_controller.extract_face_features_enhanced(img, face_rect)
        print(f'Encoding de teste: {len(test_encoding)} características')
        print(f'Primeiros valores: {test_encoding[:5]}')
    else:
        print('Nenhum rosto detectado na imagem de teste')
        exit(1)
    
    # Carrega encoding do banco
    from app.models.models import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT rosto FROM usuario WHERE id = 1')
    usuario = cursor.fetchone()
    
    # Decodifica encoding do banco
    from app.utils.face_utils import FaceRecognitionUtils
    face_utils = FaceRecognitionUtils()
    db_encoding = face_utils.decode_face_encoding(usuario['rosto'])
    
    if db_encoding is not None:
        print(f'Encoding do banco: {len(db_encoding)} características')
        print(f'Primeiros valores: {db_encoding[:5]}')
        
        # Compara os encodings
        euclidean_dist = np.linalg.norm(test_encoding - db_encoding)
        similarity = 1 / (1 + euclidean_dist)
        
        print(f'\nComparação:')
        print(f'Distância Euclidiana: {euclidean_dist:.4f}')
        print(f'Similaridade: {similarity:.4f}')
        print(f'Threshold: {face_controller.face_recognition_threshold}')
        
        if similarity > face_controller.face_recognition_threshold:
            print('✅ Rosto reconhecido!')
        else:
            print('❌ Rosto não reconhecido')
    else:
        print('❌ Falha ao decodificar encoding do banco')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
