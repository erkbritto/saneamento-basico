# Testa autenticacao apos correcao
import sys
import numpy as np
import cv2

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
    
    print('=== Teste de Autenticacao ===')
    
    # Testa autenticacao
    result = face_controller.authenticate_face_real_time(img)
    print(f'Resultado: {result}')
    
    if result.get('success'):
        print('✅ Autenticacao funcionando!')
        user_info = result.get('user', {})
        print(f'Usuário: {user_info.get("nome", "N/A")}')
        print(f'Score: {result.get("score", 0)}')
    else:
        print(f'❌ Falha na autenticacao: {result.get("message", "Erro desconhecido")}')
    
    print('\n🎉 Teste concluído!')
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
