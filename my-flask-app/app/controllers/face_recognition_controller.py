"""
Controlador para reconhecimento facial simplificado usando apenas OpenCV
"""
import cv2
import numpy as np
import os
import time
from datetime import datetime
import pickle

class FaceDetector:
    """Classe para detecção de rostos usando OpenCV"""
    
    def __init__(self):
        # Inicializa o detector de faces e olhos do OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    def detect_faces(self, frame):
        """Detecta rostos em um frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return faces
    
    def detect_eyes(self, face_region):
        """Detecta olhos em uma região do rosto"""
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray_face, 1.1, 4)
        return len(eyes) >= 2  # Retorna True se pelo menos 2 olhos forem detectados


class AntiSpoofingDetector:
    """Classe para detecção de tentativas de spoofing usando apenas OpenCV"""
    
    def __init__(self):
        # Inicializa o detector de faces do OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Parâmetros para detecção de movimento
        self.last_frame = None
        self.motion_threshold = 1000
        
    def detect_eyes(self, frame, face_rect):
        """Detecta olhos na região do rosto"""
        x, y, w, h = face_rect
        roi_gray = frame[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        # Converte para tons de cinza para detecção de olhos
        gray = cv2.cvtColor(roi_gray, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray, 1.3, 5)
        
        return len(eyes) > 0  # Retorna True se pelo menos um olho for detectado
    
    def detect_motion(self, frame):
        """Detecta movimento entre frames para evitar fotos estáticas"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.last_frame is None:
            self.last_frame = gray
            return True
            
        frame_delta = cv2.absdiff(self.last_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        motion = np.sum(thresh) > self.motion_threshold
        self.last_frame = gray
        
        return motion
    
    def detect_face_quality(self, frame, face_rect):
        """Verifica a qualidade do rosto detectado"""
        x, y, w, h = face_rect
        face_region = frame[y:y+h, x:x+w]
        
        # Verifica se a região do rosto tem tamanho suficiente
        if face_region.size == 0 or w < 100 or h < 100:
            return False, "Rosto muito pequeno ou fora do quadro."
            
        # Verifica o contraste da imagem
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        contrast = gray.std()
        
        if contrast < 30:
            return False, "Contraste insuficiente. Melhore a iluminação."
            
        # Verifica se os olhos estão visíveis
        if not self.detect_eyes(frame, face_rect):
            return False, "Não foi possível detectar os olhos. Remova óculos escuros."
            
        return True, "Rosto de boa qualidade."


class FaceRecognitionSystem:
    """Sistema simplificado de detecção facial"""
    
    def __init__(self):
        # Inicializa o detector de rostos
        self.detector = FaceDetector()
        self.anti_spoof = AntiSpoofingDetector()
        
        # Dados dos usuários cadastrados
        self.known_faces = {}  # {user_id: {'name': str, 'face_region': np.array}}
        
        # Parâmetros
        self.min_face_size = 100  # Tamanho mínimo do rosto em pixels
        self.face_margin = 20     # Margem ao redor do rosto
    
    def register_face(self, image, user_id, user_name):
        """Registra um novo rosto no sistema"""
        # Detecta o maior rosto na imagem
        faces = self.detector.detect_faces(image)
        if len(faces) == 0:
            return False, "Nenhum rosto detectado na imagem"
        
        # Pega o maior rosto
        x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
        
        # Verifica se o rosto é grande o suficiente
        if w < self.min_face_size or h < self.min_face_size:
            return False, "Rosto muito pequeno. Aproxime-se da câmera"
        
        # Extrai a região do rosto com uma margem
        margin = self.face_margin
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(image.shape[1], x + w + margin)
        y2 = min(image.shape[0], y + h + margin)
        face_region = image[y1:y2, x1:x2]
        
        # Verifica se há olhos no rosto
        if not self.detector.detect_eyes(face_region):
            return False, "Não foi possível detectar os olhos. Certifique-se de que seu rosto está bem iluminado"
        
        # Armazena os dados do rosto
        self.known_faces[user_id] = {
            'name': user_name,
            'face_region': face_region
        }
        
        return True, "Rosto cadastrado com sucesso!"
    
    def process_frame(self, frame):
        """Processa um frame de vídeo para detecção de rostos"""
        # Faz uma cópia do frame original
        output_frame = frame.copy()
        
        # Detecta rostos
        faces = self.detector.detect_faces(frame)
        
        # Processa cada rosto detectado
        for (x, y, w, h) in faces:
            # Desenha um retângulo ao redor do rosto
            cv2.rectangle(output_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Verifica se há olhos no rosto
            face_region = frame[y:y+h, x:x+w]
            has_eyes = self.detector.detect_eyes(face_region)
            
            # Adiciona um rótulo
            status = "Rosto detectado"
            if has_eyes:
                status += " (com olhos)"
            else:
                status += " (sem olhos detectados)"
                
            cv2.putText(output_frame, status, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return output_frame
    
    def verify_liveness(self, frame, face_rect):
        """Verifica se o rosto é real usando múltiplas técnicas"""
        # 1. Verifica movimento
        if not self.anti_spoof.detect_motion(frame):
            return False, "Nenhum movimento detectado. Por favor, mova-se levemente."
        
        # 2. Verifica qualidade da imagem e olhos
        is_valid, message = self.anti_spoof.detect_face_quality(frame, face_rect)
        if not is_valid:
            return False, message
        
        return True, "Verificação de vivacidade concluída com sucesso."
        
    def verify_face(self, image, user_id):
        """
        Verifica se o rosto na imagem corresponde ao usuário
        
        Args:
            image: Imagem contendo o rosto a ser verificado
            user_id: ID do usuário para verificação
            
        Returns:
            tuple: (bool, str) - (True/False, mensagem de status)
        """
        # Verifica se o usuário está cadastrado
        if user_id not in self.known_faces:
            return False, "Usuário não encontrado"
            
        # Obtém a região do rosto cadastrada
        stored_face = self.known_faces[user_id]['face_region']
        
        # Detecta rostos na imagem fornecida
        faces = self.detector.detect_faces(image)
        if len(faces) == 0:
            return False, "Nenhum rosto detectado na imagem"
            
        # Pega o maior rosto
        x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
        
        # Extrai a região do rosto com uma margem
        margin = self.face_margin
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(image.shape[1], x + w + margin)
        y2 = min(image.shape[0], y + h + margin)
        face_region = image[y1:y2, x1:x2]
        
        # Verifica se há olhos no rosto
        if not self.detector.detect_eyes(face_region):
            return False, "Não foi possível detectar os olhos. Certifique-se de que seu rosto está bem iluminado"
            
        # Redimensiona as imagens para o mesmo tamanho para comparação
        try:
            face_region = cv2.resize(face_region, (stored_face.shape[1], stored_face.shape[0]))
            
            # Converte para escala de cinza para comparação
            face_gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            stored_gray = cv2.cvtColor(stored_face, cv2.COLOR_BGR2GRAY)
            
            # Calcula a diferença absoluta entre as imagens
            diff = cv2.absdiff(face_gray, stored_gray)
            
            # Calcula a média da diferença
            mean_diff = diff.mean()
            
            # Define um limiar para considerar como correspondência
            threshold = 30  # Pode ser ajustado conforme necessário
            
            if mean_diff < threshold:
                return True, "Rosto verificado com sucesso"
            else:
                return False, "Rosto não corresponde ao cadastrado"
                
        except Exception as e:
            return False, f"Erro ao processar a imagem: {str(e)}"


# Instância global do sistema de reconhecimento facial
face_system = FaceRecognitionSystem()

def register_face(image, user_id, user_name):
    """Registra um novo rosto no sistema"""
    return face_system.register_face(image, user_id, user_name)

def verify_face(image, user_id):
    """Verifica se o rosto na imagem corresponde ao usuário"""
    return face_system.verify_face(image, user_id)

def process_frame(frame):
    """Processa um frame de vídeo para detecção de rostos"""
    return face_system.process_frame(frame)
