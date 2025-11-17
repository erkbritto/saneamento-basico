"""Controlador avancado para reconhecimento facial"""
import cv2
import numpy as np
import os
import time
import pickle
from typing import List, Tuple, Optional, Dict, Any

try:
    from ..models.models import Usuario, get_db
    from ..utils.face_utils import FaceRecognitionUtils
except ImportError:
    from app.models.models import Usuario, get_db
    from app.utils.face_utils import FaceRecognitionUtils

class AdvancedFaceRecognitionController:
    """Controller completo para reconhecimento facial"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.known_faces_cache = {}
        self.cache_timestamp = None
        self.cache_duration = 300  # 5 minutos
        self.min_face_size = (100, 100)
        self.face_recognition_threshold = 0.3  # Threshold mais realista
        
    def load_known_faces(self) -> Dict[str, Any]:
        """Carrega usuarios com rosto cadastrado"""
        current_time = time.time()
        if self.cache_timestamp and current_time - self.cache_timestamp < self.cache_duration and self.known_faces_cache:
            return self.known_faces_cache
        
        try:
            conn = get_db()
            if not conn:
                return {"success": False, "message": "Erro de conexao"}
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""SELECT id, nome, email, cargo, departamento, rosto, status FROM usuario WHERE rosto IS NOT NULL AND rosto != "" AND status = "ATIVO" ORDER BY nome""")
            usuarios = cursor.fetchall()
            cursor.close()
            conn.close()
            
            known_faces = []
            for usuario in usuarios:
                if usuario["rosto"]:
                    try:
                        face_utils = FaceRecognitionUtils()
                        encoding_data = face_utils.decode_face_encoding(usuario["rosto"])
                        if encoding_data is not None:
                            known_faces.append({
                                "id": usuario["id"],
                                "nome": usuario["nome"],
                                "email": usuario["email"],
                                "cargo": usuario["cargo"],
                                "departamento": usuario["departamento"],
                                "encoding": encoding_data
                            })
                    except Exception as e:
                        print(f"Erro ao processar rosto de {usuario["nome"]}: {e}")
            
            self.known_faces_cache = {"success": True, "faces": known_faces, "count": len(known_faces)}
            self.cache_timestamp = current_time
            return self.known_faces_cache
            
        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}
    
    def detect_faces_advanced(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detecao avancada de rostos"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=6, minSize=self.min_face_size)
            return [(x, y, w, h) for (x, y, w, h) in faces if w >= self.min_face_size[0] and h >= self.min_face_size[1]]
        except Exception as e:
            print(f"Erro na deteccao: {e}")
            return []
    
    def verify_liveness_advanced(self, frame: np.ndarray, face_rect: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """Verificacao basica de liveness"""
        try:
            x, y, w, h = face_rect
            face_region = frame[y:y+h, x:x+w]
            if face_region.size == 0:
                return {"valid": False, "reason": "Regiao invalida"}
            
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            brightness = np.mean(gray_face)
            
            score = 0
            if blur_score > 80:
                score += 50
            if 60 <= brightness <= 180:
                score += 50
            
            return {"valid": score >= 50, "score": score, "percentage": score}
        except Exception as e:
            return {"valid": False, "reason": f"Erro: {str(e)}"}
    
    def extract_face_features_enhanced(self, frame: np.ndarray, face_rect: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Extracao de caracteristicas faciais"""
        try:
            x, y, w, h = face_rect
            face_region = frame[y:y+h, x:x+w]
            if face_region.size == 0:
                return None
            
            # Extrai região do rosto com margem
            margin = 20
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(frame.shape[1], x + w + margin)
            y2 = min(frame.shape[0], y + h + margin)
            
            face_roi = frame[y1:y2, x1:x2]
            print(f"DEBUG: ROI do rosto: {face_roi.shape}")
            
            # Redimensiona para 150x150 (igual ao face_utils)
            face_resized = cv2.resize(face_roi, (150, 150))
            
            # Converte para escala de cinza
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            
            # Aplica equalização de histograma
            face_gray = cv2.equalizeHist(face_gray)
            
            # Calcula histograma com 101 bins
            hist = cv2.calcHist([face_gray], [0], None, [101], [0, 256])
            
            # Normaliza o histograma
            hist = cv2.normalize(hist, hist).flatten()
            
            # Converte para numpy array float64
            features = hist.astype(np.float64)
            
            # Adiciona características estatísticas
            mean_val = np.mean(face_gray)
            std_val = np.std(face_gray)
            
            # Concatena histograma com estatísticas (total 103 características)
            features = np.concatenate([features, [mean_val, std_val]])
            
            print(f"DEBUG: Features extraídas: {len(features)} características")
            
            return features
            
        except Exception as e:
            print(f"Erro na extracao: {e}")
            return None
    
    def compare_faces_enhanced(self, face_features: np.ndarray) -> Optional[Dict[str, Any]]:
        """Comparacao de rostos"""
        faces_data = self.load_known_faces()
        if not faces_data["success"] or faces_data["count"] == 0:
            return None
        
        try:
            best_match = None
            best_score = 0
            
            for known_face in faces_data["faces"]:
                euclidean_dist = np.linalg.norm(face_features - known_face["encoding"])
                similarity = 1 / (1 + euclidean_dist)
                
                if similarity > best_score and similarity > self.face_recognition_threshold:
                    best_score = similarity
                    best_match = {
                        "user": known_face,
                        "confidence": similarity,
                        "euclidean_distance": euclidean_dist
                    }
            
            return best_match
        except Exception as e:
            print(f"Erro na comparacao: {e}")
            return None
    
    def register_face_enhanced(self, user_id: int, image_data: bytes) -> Dict[str, Any]:
        """Cadastro de rosto"""
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                return {"success": False, "message": "Imagem invalida"}
            
            faces = self.detect_faces_advanced(image)
            if len(faces) == 0:
                return {"success": False, "message": "Nenhum rosto detectado"}
            
            face_rect = faces[0]
            face_features = self.extract_face_features_enhanced(image, face_rect)
            if face_features is None:
                return {"success": False, "message": "Falha na extracao"}
            
            conn = get_db()
            if not conn:
                return {"success": False, "message": "Erro de conexao"}
            
            cursor = conn.cursor()
            encoded_data = pickle.dumps(face_features)
            cursor.execute("UPDATE usuario SET rosto = %s WHERE id = %s", (encoded_data, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            self.cache_timestamp = None
            self.known_faces_cache = {}
            
            return {"success": True, "message": "Rosto cadastrado com sucesso"}
        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}
    
    def authenticate_face_real_time(self, frame: np.ndarray) -> Dict[str, Any]:
        """Autenticacao em tempo real"""
        try:
            faces = self.detect_faces_advanced(frame)
            if len(faces) == 0:
                return {"success": False, "message": "Nenhum rosto detectado"}
            
            face_rect = max(faces, key=lambda f: f[2] * f[3])
            liveness_result = self.verify_liveness_advanced(frame, face_rect)
            if not liveness_result["valid"]:
                return {"success": False, "message": "Verificacao falhou"}
            
            face_features = self.extract_face_features_enhanced(frame, face_rect)
            if face_features is None:
                return {"success": False, "message": "Falha na extracao"}
            
            match = self.compare_faces_enhanced(face_features)
            if match:
                return {"success": True, "user": match["user"], "confidence": match["confidence"]}
            else:
                return {"success": False, "message": "Rosto nao reconhecido"}
        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}

# Instancia global
face_controller = AdvancedFaceRecognitionController()

# Funcoes de conveniencia
def register_face(user_id: int, image_data: bytes) -> Dict[str, Any]:
    return face_controller.register_face_enhanced(user_id, image_data)

def verify_face(frame: np.ndarray) -> Dict[str, Any]:
    return face_controller.authenticate_face_real_time(frame)

def process_frame(frame: np.ndarray) -> Dict[str, Any]:
    return verify_face(frame)
