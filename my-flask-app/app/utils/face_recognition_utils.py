# face_recognition_utils.py - Sistema de Reconhecimento Facial com OpenCV
# 🎯 Objetivo: Processamento, encoding e validação de rostos para autenticação
# 🔧 Prioridade: FACEID
# 📱 Mobile: SIM | 🌙 Dark Mode: SIM

import cv2
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import pickle


class FaceRecognitionSystem:
    """Sistema completo de reconhecimento facial"""
    
    def __init__(self):
        self.tolerance = 0.6  # Tolerância para comparação (menor = mais rigoroso)
        self.model = "hog"  # Modelo: 'hog' (CPU) ou 'cnn' (GPU)
    
    def process_image_from_base64(self, base64_string):
        """
        Processa imagem em base64 e retorna array numpy
        
        Args:
            base64_string: String base64 da imagem
            
        Returns:
            numpy.ndarray: Imagem processada ou None se falhar
        """
        try:
            # Remove prefixo data:image se existir
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decodifica base64
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data))
            
            # Converte para RGB (face_recognition usa RGB)
            image_rgb = np.array(image.convert('RGB'))
            
            return image_rgb
        except Exception as e:
            print(f"Erro ao processar imagem base64: {e}")
            return None
    
    def detect_faces(self, image):
        """
        Detecta rostos na imagem
        
        Args:
            image: numpy array da imagem
            
        Returns:
            list: Lista de localizações dos rostos [(top, right, bottom, left), ...]
        """
        try:
            face_locations = face_recognition.face_locations(image, model=self.model)
            return face_locations
        except Exception as e:
            print(f"Erro ao detectar rostos: {e}")
            return []
    
    def encode_face(self, image):
        """
        Gera encoding (vetor de características) do rosto na imagem
        
        Args:
            image: numpy array da imagem
            
        Returns:
            tuple: (encoding, face_location) ou (None, None) se falhar
        """
        try:
            # Detecta rostos
            face_locations = self.detect_faces(image)
            
            if len(face_locations) == 0:
                return None, "Nenhum rosto detectado na imagem"
            
            if len(face_locations) > 1:
                return None, "Múltiplos rostos detectados. Use uma foto com apenas um rosto"
            
            # Gera encoding do rosto
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if len(face_encodings) == 0:
                return None, "Não foi possível gerar encoding do rosto"
            
            return face_encodings[0], None
        
        except Exception as e:
            print(f"Erro ao gerar encoding: {e}")
            return None, f"Erro ao processar rosto: {str(e)}"
    
    def compare_faces(self, known_encoding, unknown_encoding):
        """
        Compara dois encodings faciais
        
        Args:
            known_encoding: Encoding conhecido (do banco de dados)
            unknown_encoding: Encoding a ser comparado
            
        Returns:
            tuple: (match: bool, distance: float)
        """
        try:
            # Calcula distância entre encodings
            face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
            
            # Verifica se é uma correspondência
            match = face_distance <= self.tolerance
            
            # Calcula confiança (0-100%)
            confidence = (1 - face_distance) * 100
            
            return match, confidence
        
        except Exception as e:
            print(f"Erro ao comparar rostos: {e}")
            return False, 0.0
    
    def validate_image_quality(self, image):
        """
        Valida qualidade da imagem para reconhecimento facial
        
        Args:
            image: numpy array da imagem
            
        Returns:
            tuple: (valid: bool, message: str)
        """
        try:
            # Verifica dimensões mínimas
            height, width = image.shape[:2]
            if width < 200 or height < 200:
                return False, "Imagem muito pequena. Use uma resolução maior"
            
            # Verifica se há rosto
            face_locations = self.detect_faces(image)
            if len(face_locations) == 0:
                return False, "Nenhum rosto detectado. Posicione seu rosto na câmera"
            
            if len(face_locations) > 1:
                return False, "Múltiplos rostos detectados. Apenas um rosto deve estar visível"
            
            # Verifica tamanho do rosto na imagem (deve ocupar pelo menos 20% da altura)
            top, right, bottom, left = face_locations[0]
            face_height = bottom - top
            if face_height < height * 0.2:
                return False, "Rosto muito distante. Aproxime-se da câmera"
            
            # Verifica iluminação básica (não muito escura)
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            mean_brightness = np.mean(gray)
            if mean_brightness < 50:
                return False, "Imagem muito escura. Melhore a iluminação"
            
            return True, "Imagem válida"
        
        except Exception as e:
            print(f"Erro ao validar qualidade: {e}")
            return False, f"Erro na validação: {str(e)}"
    
    def serialize_encoding(self, encoding):
        """
        Serializa encoding para armazenamento no banco
        
        Args:
            encoding: numpy array do encoding
            
        Returns:
            str: Encoding serializado em base64
        """
        try:
            # Serializa com pickle e converte para base64
            pickled = pickle.dumps(encoding)
            encoded = base64.b64encode(pickled).decode('utf-8')
            return encoded
        except Exception as e:
            print(f"Erro ao serializar encoding: {e}")
            return None
    
    def deserialize_encoding(self, encoded_string):
        """
        Deserializa encoding do banco de dados
        
        Args:
            encoded_string: String base64 do encoding
            
        Returns:
            numpy.ndarray: Encoding deserializado
        """
        try:
            # Decodifica base64 e deserializa com pickle
            decoded = base64.b64decode(encoded_string)
            encoding = pickle.loads(decoded)
            return encoding
        except Exception as e:
            print(f"Erro ao deserializar encoding: {e}")
            return None
    
    def register_face(self, base64_image):
        """
        Registra um novo rosto (fluxo completo)
        
        Args:
            base64_image: Imagem em base64
            
        Returns:
            dict: {'success': bool, 'encoding': str, 'message': str}
        """
        try:
            # Processa imagem
            image = self.process_image_from_base64(base64_image)
            if image is None:
                return {
                    'success': False,
                    'encoding': None,
                    'message': 'Erro ao processar imagem'
                }
            
            # Valida qualidade
            valid, message = self.validate_image_quality(image)
            if not valid:
                return {
                    'success': False,
                    'encoding': None,
                    'message': message
                }
            
            # Gera encoding
            encoding, error = self.encode_face(image)
            if encoding is None:
                return {
                    'success': False,
                    'encoding': None,
                    'message': error or 'Erro ao gerar encoding'
                }
            
            # Serializa encoding
            serialized = self.serialize_encoding(encoding)
            if serialized is None:
                return {
                    'success': False,
                    'encoding': None,
                    'message': 'Erro ao serializar encoding'
                }
            
            return {
                'success': True,
                'encoding': serialized,
                'message': 'Rosto registrado com sucesso!'
            }
        
        except Exception as e:
            print(f"Erro no registro facial: {e}")
            return {
                'success': False,
                'encoding': None,
                'message': f'Erro no registro: {str(e)}'
            }
    
    def authenticate_face(self, base64_image, stored_encoding):
        """
        Autentica um rosto comparando com encoding armazenado
        
        Args:
            base64_image: Imagem em base64
            stored_encoding: Encoding armazenado (serializado)
            
        Returns:
            dict: {'success': bool, 'confidence': float, 'message': str}
        """
        try:
            # Processa imagem
            image = self.process_image_from_base64(base64_image)
            if image is None:
                return {
                    'success': False,
                    'confidence': 0.0,
                    'message': 'Erro ao processar imagem'
                }
            
            # Gera encoding da imagem atual
            current_encoding, error = self.encode_face(image)
            if current_encoding is None:
                return {
                    'success': False,
                    'confidence': 0.0,
                    'message': error or 'Nenhum rosto detectado'
                }
            
            # Deserializa encoding armazenado
            known_encoding = self.deserialize_encoding(stored_encoding)
            if known_encoding is None:
                return {
                    'success': False,
                    'confidence': 0.0,
                    'message': 'Erro ao carregar dados faciais'
                }
            
            # Compara rostos
            match, confidence = self.compare_faces(known_encoding, current_encoding)
            
            if match:
                return {
                    'success': True,
                    'confidence': round(confidence, 2),
                    'message': f'Autenticação bem-sucedida! Confiança: {round(confidence, 2)}%'
                }
            else:
                return {
                    'success': False,
                    'confidence': round(confidence, 2),
                    'message': f'Rosto não reconhecido. Confiança: {round(confidence, 2)}%'
                }
        
        except Exception as e:
            print(f"Erro na autenticação facial: {e}")
            return {
                'success': False,
                'confidence': 0.0,
                'message': f'Erro na autenticação: {str(e)}'
            }


# Instância global do sistema
face_system = FaceRecognitionSystem()
