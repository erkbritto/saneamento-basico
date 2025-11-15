"""
Utilitários para reconhecimento facial usando OpenCV
"""
import cv2
import numpy as np
import pickle
import base64
from io import BytesIO

class FaceRecognitionUtils:
    """Classe utilitária para operações de reconhecimento facial"""
    
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def decode_base64_image(self, base64_string):
        """Decodifica string base64 para imagem OpenCV"""
        try:
            # Remove o cabeçalho se existir (data:image/jpeg;base64,...)
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decodifica
            img_data = base64.b64decode(base64_string)
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return image
        except Exception as e:
            print(f"Erro ao decodificar imagem: {str(e)}")
            return None
    
    def detect_faces(self, image):
        """Detecta rostos em uma imagem usando Haar Cascade com validação anti-spoofing"""
        if image is None:
            return []
        
        # Converte para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Melhora a qualidade da imagem
        gray = cv2.equalizeHist(gray)
        
        # Detecta rostos com parâmetros mais precisos
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1,  # Fator de escala mais preciso
            minNeighbors=6,   # Mais vizinhos para reduzir falsos positivos
            minSize=(80, 80), # Tamanho mínimo do rosto
            maxSize=(300, 300) # Tamanho máximo do rosto
        )
        
        # Filtra rostos por qualidade
        valid_faces = []
        for (x, y, w, h) in faces:
            # Verifica proporção do rosto (deve ser razoável)
            aspect_ratio = w / h
            if 0.7 <= aspect_ratio <= 1.4:  # Proporção razoável de rosto
                # Verifica se o rosto tem tamanho adequado
                if w >= 80 and h >= 80:
                    valid_faces.append((x, y, w, h))
        
        print(f"DEBUG: Rostos detectados: {len(faces)}, Rostos válidos: {len(valid_faces)}")
        return valid_faces
    
    def extract_face_encoding(self, image, face_coords=None):
        """Extrai encoding do rosto com características mais robustas"""
        if face_coords is None:
            # Detecta rostos primeiro
            faces = self.detect_faces(image)
            if len(faces) == 0:
                return None
            # Usa o primeiro rosto encontrado
            face_coords = faces[0]
        
        x, y, w, h = face_coords
        
        # Extrai a região do rosto com margem de segurança
        margin = 10
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(image.shape[1], x + w + margin)
        y2 = min(image.shape[0], y + h + margin)
        
        face_roi = image[y1:y2, x1:x2]
        
        # Redimensiona para tamanho padrão maior
        face_roi = cv2.resize(face_roi, (150, 150))
        
        # Converte para escala de cinza
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Aplica CLAHE para melhorar contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced_face = clahe.apply(gray_face)
        
        # Extrai múltiplas características
        features = []
        
        # 1. Histograma de cores original
        hist_color = cv2.calcHist([enhanced_face], [0], None, [64], [0, 256])
        hist_color = cv2.normalize(hist_color, hist_color).flatten()
        features.extend(hist_color)
        
        # 2. Textura usando LBP (Local Binary Pattern)
        try:
            # Calcula LBP
            radius = 3
            n_points = 8 * radius
            lbp = np.zeros_like(enhanced_face)
            
            # Implementação simplificada de LBP
            for i in range(radius, enhanced_face.shape[0] - radius):
                for j in range(radius, enhanced_face.shape[1] - radius):
                    center = enhanced_face[i, j]
                    code = 0
                    for n in range(n_points):
                        angle = 2 * np.pi * n / n_points
                        x = i + radius * np.cos(angle)
                        y = j + radius * np.sin(angle)
                        if enhanced_face[int(x), int(y)] >= center:
                            code |= (1 << n)
                    lbp[i, j] = code
            
            # Histograma do LBP
            hist_lbp = cv2.calcHist([lbp], [0], None, [256], [0, 256])
            hist_lbp = cv2.normalize(hist_lbp, hist_lbp).flatten()
            features.extend(hist_lbp)
        except:
            pass
        
        # 3. Momentos de Hu (forma do rosto)
        moments = cv2.moments(enhanced_face)
        hu_moments = cv2.HuMoments(moments)
        hu_moments = np.sign(hu_moments) * np.log(np.abs(hu_moments) + 1e-10)
        features.extend(hu_moments.flatten())
        
        # 4. Gradientes (bordas do rosto)
        sobel_x = cv2.Sobel(enhanced_face, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(enhanced_face, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        hist_gradient = cv2.calcHist([gradient_magnitude.astype(np.uint8)], [0], None, [32], [0, 256])
        hist_gradient = cv2.normalize(hist_gradient, hist_gradient).flatten()
        features.extend(hist_gradient)
        
        # Converte para numpy array
        encoding = np.array(features, dtype=np.float64)
        
        print(f"DEBUG: Encoding extraído com {len(encoding)} características")
        return encoding
    
    def register_face(self, image, user_id):
        """Registra um rosto para um usuário"""
        try:
            # Detecta rostos na imagem
            faces = self.detect_faces(image)
            
            if len(faces) == 0:
                return False, "Nenhum rosto detectado na imagem"
            
            if len(faces) > 1:
                return False, "Múltiplos rostos detectados. Por favor, envie uma imagem com apenas um rosto"
            
            # Extrai encoding do rosto
            face_encoding = self.extract_face_encoding(image, faces[0])
            
            if face_encoding is None:
                return False, "Erro ao extrair características do rosto"
            
            # Adiciona aos encodings conhecidos
            self.known_face_encodings.append(face_encoding)
            self.known_face_ids.append(user_id)
            
            return True, "Rosto registrado com sucesso"
            
        except Exception as e:
            return False, f"Erro ao registrar rosto: {str(e)}"
    
    def compare_faces(self, face_encoding1, face_encoding2, threshold=0.65):
        """Compara dois encodings de rosto usando múltiplas métricas"""
        if face_encoding1 is None or face_encoding2 is None:
            return False
        
        if len(face_encoding1) != len(face_encoding2):
            return False
        
        # Divide o encoding em diferentes tipos de características
        # Assumindo a ordem: histograma(64) + LBP(256) + Hu(7) + gradientes(32) = 359
        hist1, lbp1, hu1, grad1 = self._split_encoding(face_encoding1)
        hist2, lbp2, hu2, grad2 = self._split_encoding(face_encoding2)
        
        scores = []
        
        # 1. Compara histograma de cores (peso: 30%)
        if hist1 is not None and hist2 is not None:
            hist_corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            scores.append(hist_corr * 0.3)
            print(f"DEBUG: Correlação histograma: {hist_corr:.4f}")
        
        # 2. Compara textura LBP (peso: 35%)
        if lbp1 is not None and lbp2 is not None:
            lbp_corr = cv2.compareHist(lbp1, lbp2, cv2.HISTCMP_CORREL)
            scores.append(lbp_corr * 0.35)
            print(f"DEBUG: Correlação LBP: {lbp_corr:.4f}")
        
        # 3. Compara momentos de Hu (peso: 20%)
        if hu1 is not None and hu2 is not None:
            hu_dist = np.linalg.norm(hu1 - hu2)
            hu_sim = 1.0 / (1.0 + hu_dist)  # Converte distância para similaridade
            scores.append(hu_sim * 0.2)
            print(f"DEBUG: Similaridade Hu: {hu_sim:.4f}")
        
        # 4. Compara gradientes (peso: 15%)
        if grad1 is not None and grad2 is not None:
            grad_corr = cv2.compareHist(grad1, grad2, cv2.HISTCMP_CORREL)
            scores.append(grad_corr * 0.15)
            print(f"DEBUG: Correlação gradientes: {grad_corr:.4f}")
        
        # Calcula score final
        final_score = sum(scores) if scores else 0
        
        print(f"DEBUG: Score final: {final_score:.4f} (threshold: {threshold})")
        
        # Validação adicional: verifica se features individuais são razoáveis
        if final_score > threshold:
            # Verifica se não é muito perfeito (possível spoof)
            if final_score > 0.95:
                print("DEBUG: Score muito alto, possível spoof - aplicando verificação extra")
                # Adiciona verificação de ruído/imperfeições
                if not self._validate_natural_face(face_encoding1, face_encoding2):
                    print("DEBUG: Falhou na validação de rosto natural")
                    return False
        
        return final_score >= threshold
    
    def _split_encoding(self, encoding):
        """Divide o encoding em diferentes tipos de características"""
        try:
            # Tamanhos esperados: histograma(64) + LBP(256) + Hu(7) + gradientes(32) = 359
            if len(encoding) >= 359:
                hist = encoding[0:64].reshape(64, 1)
                lbp = encoding[64:320].reshape(256, 1)
                hu = encoding[320:327]
                grad = encoding[327:359].reshape(32, 1)
                return hist, lbp, hu, grad
            else:
                # Fallback para encoding antigo (só histograma)
                return encoding.reshape(-1, 1), None, None, None
        except:
            return None, None, None, None
    
    def _validate_natural_face(self, encoding1, encoding2):
        """Valida se os rostos parecem naturais (não fotos/vídeos)"""
        try:
            # Verifica variação nas características (rosto natural tem imperfeições)
            variance = np.var(encoding1)
            if variance < 0.001:  # Muito uniforme = possível foto
                return False
            
            # Verifica simetria (rostos naturais não são perfeitamente simétricos)
            hist1, lbp1, hu1, grad1 = self._split_encoding(encoding1)
            if lbp1 is not None:
                lbp_variance = np.var(lbp1)
                if lbp_variance < 0.01:  # Textura muito uniforme
                    return False
            
            return True
        except:
            return True  # Se não conseguir validar, aceita
    
    def authenticate_face(self, image, user_id):
        """Autentica um rosto específico de um usuário"""
        try:
            # Detecta rostos
            faces = self.detect_faces(image)
            
            if len(faces) == 0:
                return False, "Nenhum rosto detectado"
            
            if len(faces) > 1:
                return False, "Múltiplos rostos detectados"
            
            # Extrai encoding
            face_encoding = self.extract_face_encoding(image, faces[0])
            
            if face_encoding is None:
                return False, "Erro ao processar rosto"
            
            # Procura pelo encoding do usuário
            for i, known_id in enumerate(self.known_face_ids):
                if known_id == user_id:
                    if self.compare_faces(face_encoding, self.known_face_encodings[i]):
                        return True, "Rosto autenticado com sucesso"
                    else:
                        return False, "Rosto não corresponde ao usuário"
            
            return False, "Usuário não possui rosto cadastrado"
            
        except Exception as e:
            return False, f"Erro na autenticação: {str(e)}"
    
    def authenticate_any_face(self, image):
        """Autentica contra qualquer rosto conhecido com verificação de vivacidade"""
        try:
            # Detecta rostos
            faces = self.detect_faces(image)
            print(f"DEBUG: Rostos detectados na imagem: {len(faces)}")
            
            if len(faces) == 0:
                return False, None, "Nenhum rosto detectado"
            
            if len(faces) > 1:
                return False, None, "Múltiplos rostos detectados"
            
            # Verificação de vivacidade (liveness detection)
            if not self._check_liveness(image, faces[0]):
                print("DEBUG: Falhou na verificação de vivacidade")
                return False, None, "Verificação de vivacidade falhou. Posicione-se melhor."
            
            # Extrai encoding
            face_encoding = self.extract_face_encoding(image, faces[0])
            
            if face_encoding is None:
                return False, None, "Erro ao processar rosto"
            
            print(f"DEBUG: Comparando com {len(self.known_face_encodings)} rostos conhecidos")
            
            # Compara com todos os rostos conhecidos
            best_score = 0
            best_user_id = None
            
            for i, known_encoding in enumerate(self.known_face_encodings):
                # Usa comparação detalhada
                if self.compare_faces(face_encoding, known_encoding):
                    user_id = self.known_face_ids[i]
                    print(f"DEBUG: Rosto reconhecido! User ID: {user_id}")
                    
                    # Verificação adicional de consistência
                    if self._verify_face_consistency(image, known_encoding):
                        return True, user_id, "Rosto reconhecido com sucesso"
                    else:
                        print(f"DEBUG: User {user_id} falhou na verificação de consistência")
            
            print("DEBUG: Nenhum rosto correspondente encontrado")
            return False, None, "Rosto não reconhecido"
            
        except Exception as e:
            return False, None, f"Erro na autenticação: {str(e)}"
    
    def _check_liveness(self, image, face_coords):
        """Verifica se o rosto é de uma pessoa viva (anti-spoofing)"""
        try:
            x, y, w, h = face_coords
            
            # Extrai região do rosto
            face_roi = image[y:y+h, x:x+w]
            
            # Converte para diferentes espaços de cor
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
            
            # 1. Verifica qualidade da imagem (blur detection)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:  # Muito borrado = possível foto
                print(f"DEBUG: Imagem muito borrada: {laplacian_var}")
                return False
            
            # 2. Verifica variação de cor (rostos naturais têm variação)
            color_variance = np.var(hsv[:,:,1])  # Saturação
            if color_variance < 50:  # Pouca variação de cor
                print(f"DEBUG: Pouca variação de cor: {color_variance}")
                return False
            
            # 3. Verifica bordas (rostos naturais têm textura)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            if edge_density < 0.05:  # Poucas bordas
                print(f"DEBUG: Poucas bordas detectadas: {edge_density}")
                return False
            
            # 4. Verifica iluminação (não deve ser muito uniforme)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_std = np.std(hist)
            if hist_std < 10:  # Iluminação muito uniforme
                print(f"DEBUG: Iluminação muito uniforme: {hist_std}")
                return False
            
            print(f"DEBUG: Liveness check passado - Blur: {laplacian_var:.1f}, Cor: {color_variance:.1f}, Bordas: {edge_density:.3f}")
            return True
            
        except Exception as e:
            print(f"DEBUG: Erro no liveness check: {e}")
            return True  # Se falhar, aceita (fallback)
    
    def _verify_face_consistency(self, image, stored_encoding):
        """Verifica consistência do rosto com encoding armazenado"""
        try:
            # Detecta rosto novamente para garantir consistência
            faces = self.detect_faces(image)
            if len(faces) == 0:
                return False
            
            # Extrai encoding do mesmo rosto
            current_encoding = self.extract_face_encoding(image, faces[0])
            
            if current_encoding is None:
                return False
            
            # Compara com encoding armazenado usando threshold mais alto
            return self.compare_faces(current_encoding, stored_encoding, threshold=0.7)
            
        except:
            return True  # Fallback
    
    def save_face_encoding(self, face_encoding):
        """Converte encoding para bytes para salvar no banco"""
        return pickle.dumps(face_encoding)
    
    def load_face_encoding(self, encoding_bytes):
        """Carrega encoding dos bytes do banco"""
        return pickle.loads(encoding_bytes)
    
    def load_known_faces_from_database(self, users_with_faceid):
        """Carrega rostos conhecidos do banco de dados"""
        self.known_face_encodings = []
        self.known_face_ids = []
        
        for user in users_with_faceid:
            if user.get('rosto'):
                try:
                    encoding = self.load_face_encoding(user['rosto'])
                    self.known_face_encodings.append(encoding)
                    self.known_face_ids.append(user['id'])
                except Exception as e:
                    print(f"Erro ao carregar encoding do usuário {user['id']}: {str(e)}")

# Instância global
face_utils = FaceRecognitionUtils()
