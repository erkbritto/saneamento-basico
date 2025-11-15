"""
UtilitÃ¡rio para converter dados do face-api.js em imagens base64
"""
import base64
import json
import cv2
import numpy as np
from io import BytesIO

class FaceAPIConverter:
    """Converte dados de detecÃ§Ã£o do face-api.js em imagens processÃ¡veis"""
    
    @staticmethod
    def extract_face_from_video(video_element, face_box):
        """
        Extrai a regiÃ£o do rosto do vÃ­deo baseado nas coordenadas do face-api.js
        Esta funÃ§Ã£o deve ser chamada no frontend antes de enviar ao backend
        """
        # Esta funÃ§Ã£o seria implementada no frontend JavaScript
        # Por enquanto, vamos processar o JSON recebido
        pass
    
    @staticmethod
    def process_face_api_json(face_json):
        """
        Processa o JSON recebido do face-api.js e tenta extrair informaÃ§Ãµes Ãºteis
        """
        try:
            if not face_json or face_json.strip() == '':
                return None
                
            face_data = json.loads(face_json)
            
            # Se for apenas coordenadas, nÃ£o podemos processar sem a imagem
            if isinstance(face_data, dict) and 'x' in face_data:
                # Ã‰ um bounding box - precisamos da imagem original
                return None
                
            return face_data
            
        except json.JSONDecodeError:
            # NÃ£o Ã© JSON, pode ser base64 direto
            return face_json
        except Exception as e:
            print(f"Erro ao processar JSON do face-api.js: {str(e)}")
            return None
    
    @staticmethod
    def create_placeholder_image():
        """
        Cria uma imagem placeholder quando nÃ£o conseguimos processar o rosto
        """
        # Cria uma imagem preta como placeholder
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Converte para base64
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return img_base64
