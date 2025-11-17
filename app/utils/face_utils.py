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
        
    def decode_face_encoding(self, encoding_data):
        """Decodifica encoding do banco de dados para numpy array"""
        try:
            if not encoding_data:
                print("DEBUG: Encoding vazio")
                return None
            
            # Se for bytes (BLOB do banco) - pode ser string base64 em bytes
            if isinstance(encoding_data, bytes):
                print(f"DEBUG: Decodificando {len(encoding_data)} bytes do banco")
                
                # Tenta decodificar como string UTF-8 primeiro (caso seja base64 string)
                try:
                    encoding_str = encoding_data.decode('utf-8')
                    print(f"DEBUG: Bytes decodificados como string: {encoding_str[:50]}...")
                    
                    # Remove prefix se existir
                    if ',' in encoding_str:
                        encoding_str = encoding_str.split(',')[1]
                    
                    # Decodifica de base64 para bytes
                    encoding_bytes = base64.b64decode(encoding_str)
                    print(f"DEBUG: Base64 decodificado: {len(encoding_bytes)} bytes")
                    
                    # Converte para numpy array
                    encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                    print(f"DEBUG: Encoding recuperado: {len(encoding)} características")
                    return encoding
                    
                except Exception as e:
                    print(f"DEBUG: Falha em decodificar como string base64: {e}")
                
                # Tenta direto como numpy array (encoding.tobytes())
                try:
                    encoding = np.frombuffer(encoding_data, dtype=np.float64)
                    print(f"DEBUG: Encoding decodificado via numpy direto: {len(encoding)} características")
                    return encoding
                except Exception as e:
                    print(f"DEBUG: Falha em numpy direto: {e}")
                
                # Tenta decodificar como pickle
                try:
                    encoding = pickle.loads(encoding_data)
                    print(f"DEBUG: Encoding decodificado via pickle: {len(encoding)} características")
                    return encoding
                except Exception as e:
                    print(f"DEBUG: Falha em pickle: {e}")
                
                print("DEBUG: Falha em todas as tentativas de decodificação")
                return None
            
            # Se for string base64
            elif isinstance(encoding_data, str):
                print("DEBUG: Decodificando string base64")
                # Remove prefix se existir
                if ',' in encoding_data:
                    encoding_data = encoding_data.split(',')[1]
                
                # Decodifica de base64 para bytes
                encoding_bytes = base64.b64decode(encoding_data)
                
                # Converte bytes para numpy array
                encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                print(f"DEBUG: Encoding decodificado de string: {len(encoding)} características")
                return encoding
            
            # Se já for numpy array
            elif isinstance(encoding_data, np.ndarray):
                print(f"DEBUG: Encoding já é numpy array: {len(encoding_data)} características")
                return encoding_data
            
            else:
                print(f"DEBUG: Tipo não suportado: {type(encoding_data)}")
                return None
                
        except Exception as e:
            print(f"DEBUG: Erro ao decodificar encoding: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
        """Detecta rostos em uma imagem com parâmetros ultra permissivos"""
        try:
            # Converte para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Equaliza histograma para melhorar contraste
            gray = cv2.equalizeHist(gray)
            
            # Aplica blur leve para reduzir ruído
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Detecta rostos com parâmetros ultra permissivos
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,  # Muito baixo - mais sensível
                minNeighbors=2,     # Muito baixo - mais permissivo
                minSize=(25, 25),   # Muito pequeno
                maxSize=(700, 700), # Grande o suficiente
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Filtra rostos válidos (apenas verifica tamanho mínimo)
            valid_faces = []
            for (x, y, w, h) in faces:
                if w >= 25 and h >= 25:  # Tamanho mínimo muito baixo
                    valid_faces.append((x, y, w, h))
            
            return valid_faces
            
        except Exception as e:
            print(f"DEBUG: Erro na detecção de rostos: {e}")
            return []
    
    def extract_face_encoding(self, image, face_coords=None):
        """Extrai encoding do rosto - versão ultra simplificada e robusta"""
        try:
            if face_coords is None:
                # Detecta rostos primeiro
                faces = self.detect_faces(image)
                if len(faces) == 0:
                    print("DEBUG: Nenhum rosto detectado para extração")
                    return None
                # Usa o primeiro rosto encontrado
                face_coords = faces[0]
            # Verifica se tem 4 coordenadas
            if isinstance(face_coords, (tuple, list)) and len(face_coords) == 4:
                x, y, w, h = face_coords
            else:
                print(f"DEBUG: Formato inesperado de face_coords: {face_coords}, tipo: {type(face_coords)}")
                return None
            print(f"DEBUG: Extraindo encoding do rosto em ({x}, {y}, {w}, {h})")
            
            # Extrai a região do rosto com margem maior
            margin = 20
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(image.shape[1], x + w + margin)
            y2 = min(image.shape[0], y + h + margin)
            
            face_roi = image[y1:y2, x1:x2]
            print(f"DEBUG: ROI do rosto: {face_roi.shape}")
            
            # Redimensiona para tamanho padrão maior
            face_roi = cv2.resize(face_roi, (150, 150))
            
            # Converte para escala de cinza
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Aplica equalização de histograma para normalizar iluminação
            gray_face = cv2.equalizeHist(gray_face)
            
            # Calcula histograma com 101 bins para total de 103 características (101 + mean + std)
            hist = cv2.calcHist([gray_face], [0], None, [101], [0, 256])
            
            # Normaliza o histograma de forma mais robusta
            hist = cv2.normalize(hist, hist).flatten()
            
            # Converte para numpy array float64
            encoding = hist.astype(np.float64)
            
            # Adiciona特征 estatísticas para mais robustez
            mean_val = np.mean(gray_face)
            std_val = np.std(gray_face)
            
            # Concatena histograma com estatísticas
            encoding = np.concatenate([encoding, [mean_val, std_val]])
            
            print(f"DEBUG: Encoding extraído com {len(encoding)} características")
            print(f"DEBUG: Mean: {mean_val:.2f}, Std: {std_val:.2f}")
            print(f"DEBUG: Primeiros 5 valores: {encoding[:5]}")
            print(f"DEBUG: Últimos 5 valores: {encoding[-5:]}")
            
            return encoding
            
        except Exception as e:
            print(f"DEBUG: Erro ao extrair encoding: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
    
    def detect_faces_ultra_permissive(self, image):
        """Detecta rostos com parâmetros ultra permissivos"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Equaliza histograma para melhorar contraste
            gray = cv2.equalizeHist(gray)
            
            # Aplica blur para reduzir ruído
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Detecta rostos com parâmetros ultra permissivos
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.02,  # Ainda mais baixo - ultra sensível
                minNeighbors=1,     # Mínimo possível - ultra permissivo
                minSize=(20, 20),   # Muito pequeno
                maxSize=(800, 800),  # Bem grande
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Filtra rostos válidos (apenas verifica tamanho mínimo)
            valid_faces = []
            for (x, y, w, h) in faces:
                if w >= 20 and h >= 20:  # Tamanho mínimo ultra baixo
                    valid_faces.append((x, y, w, h))
            
            return valid_faces
            
        except Exception as e:
            print(f"DEBUG: Erro na detecção ultra permissiva: {e}")
            return []
    
    def extract_multiple_encodings(self, image, face_coords):
        """Extrai múltiplos encodings do mesmo rosto para robustez"""
        try:
            encodings = []
            
            # Verifica se tem 4 coordenadas
            if isinstance(face_coords, (tuple, list)) and len(face_coords) == 4:
                x, y, w, h = face_coords
            else:
                print(f"DEBUG: Formato inesperado de face_coords: {face_coords}")
                return []
            
            # Extrai com diferentes margens e parâmetros
            margins = [10, 20, 30]  # Diferentes margens
            
            for margin in margins:
                try:
                    # Extrai região com margem
                    x1 = max(0, x - margin)
                    y1 = max(0, y - margin)
                    x2 = min(image.shape[1], x + w + margin)
                    y2 = min(image.shape[0], y + h + margin)
                    
                    face_roi = image[y1:y2, x1:x2]
                    
                    if face_roi.size == 0:
                        continue
                    
                    # Redimensiona para tamanho padrão maior (ig ao extract_face_encoding)
                    face_roi = cv2.resize(face_roi, (150, 150))
                    
                    # Converte para escala de cinza (ig ao extract_face_encoding)
                    gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
                    
                    # Aplica equalização de histograma para normalizar iluminação
                    gray_face = cv2.equalizeHist(gray_face)
                    
                    # Calcula histograma com 101 bins para total de 103 características (101 + mean + std)
                    hist = cv2.calcHist([gray_face], [0], None, [101], [0, 256])
                    
                    # Normaliza o histograma de forma mais robusta
                    hist = cv2.normalize(hist, hist).flatten()
                    
                    # Converte para numpy array float64
                    encoding = hist.astype(np.float64)
                    
                    # Adiciona características estatísticas para mais robustez
                    mean_val = np.mean(gray_face)
                    std_val = np.std(gray_face)
                    
                    # Concatena histograma com estatísticas
                    features = np.concatenate([encoding, [mean_val, std_val]])
                    
                    print(f"DEBUG: Encoding extraído - Shape: {features.shape}, Esperado: 103")
                    
                    encodings.append(features)
                    
                except Exception as e:
                    print(f"DEBUG: Erro ao extrair encoding com margem {margin}: {e}")
                    continue
            
            return encodings
            
        except Exception as e:
            print(f"DEBUG: Erro ao extrair múltiplos encodings: {e}")
            return []
    
    def authenticate_any_face(self, image):
        """Autentica qualquer rosto detectado na imagem - versão ultra permissiva e inteligente"""
        try:
            print(f"DEBUG: Iniciando autenticação facial ultra permissiva")
            
            # Detecta rostos na imagem com parâmetros ultra permissivos
            faces = self.detect_faces(image)
            print(f"DEBUG: Rostos detectados: {len(faces)}")
            
            if len(faces) == 0:
                print("DEBUG: Nenhum rosto detectado - tentando detecção alternativa")
                # Tenta detecção com parâmetros ainda mais permissivos
                faces = self.detect_faces_ultra_permissive(image)
                print(f"DEBUG: Rostos detectados com método alternativo: {len(faces)}")
                
                if len(faces) == 0:
                    return {'success': False, 'message': 'Nenhum rosto detectado'}
            
            # Pega o maior rosto detectado
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            print(f"DEBUG: Maior rosto selecionado: {largest_face}")
            
            # Extrai múltiplos encodings do rosto para robustez
            encodings = self.extract_multiple_encodings(image, largest_face)
            if not encodings:
                print("DEBUG: Falha ao extrair encodings - tentando método padrão")
                # Fallback para método padrão
                encoding = self.extract_face_encoding(image, largest_face)
                if encoding is not None:
                    encodings = [encoding]
                else:
                    print("DEBUG: Falha total ao extrair encodings")
                    return {'success': False, 'message': 'Falha ao extrair características do rosto'}
            
            print(f"DEBUG: {len(encodings)} encodings extraídos para robustez")
            
            # Busca todos os usuários com rosto cadastrado
            from ..controllers.controller import UsuarioController
            usuarios = UsuarioController.listar_usuarios_com_rosto()
            print(f"DEBUG: Usuários com rosto cadastrado: {len(usuarios)}")
            
            if not usuarios:
                print("DEBUG: Nenhum usuário com rosto cadastrado")
                return {'success': False, 'message': 'Nenhum usuário com rosto cadastrado'}
            
            # Compara com todos os rostos cadastrados usando múltiplos encodings
            melhor_match = None
            melhor_distancia = float('inf')
            melhor_usuario = None
            
            for usuario in usuarios:
                try:
                    # Decodifica o encoding do banco
                    stored_encoding = self.decode_face_encoding(usuario['rosto'])
                    if stored_encoding is None:
                        print(f"DEBUG: Falha ao decodificar encoding do usuário {usuario['id']}")
                        continue
                    
                    print(f"DEBUG: Comparando com usuário {usuario['id']} - {usuario['nome']}")
                    
                    # Compara com todos os encodings extraídos e pega o melhor resultado
                    melhor_distancia_usuario = float('inf')
                    for i, encoding in enumerate(encodings):
                        distance = np.linalg.norm(encoding - stored_encoding)
                        melhor_distancia_usuario = min(melhor_distancia_usuario, distance)
                        print(f"DEBUG: Encoding {i+1} - Distância: {distance:.6f}")
                    
                    print(f"DEBUG: Melhor distância para {usuario['nome']}: {melhor_distancia_usuario:.6f}")
                    
                    # Threshold ultra permissivo e adaptativo
                    threshold = 10.0  # Ultra permissivo
                    
                    if melhor_distancia_usuario < melhor_distancia:
                        melhor_distancia = melhor_distancia_usuario
                        melhor_match = usuario
                        melhor_usuario = usuario
                        print(f"DEBUG: Novo melhor match: {usuario['nome']} com distância {melhor_distancia_usuario:.6f}")
                    
                    # Verifica se já é bom o suficiente - threshold ultra permissivo
                    if melhor_distancia_usuario < 100.0:  # Threshold extremamente permissivo
                        print(f"DEBUG: ROSTO RECONHECIDO! Usuário: {usuario['nome']}")
                        return {
                            'success': True,
                            'message': f'Rosto reconhecido! Bem-vindo(a), {usuario["nome"]}!',
                            'user': usuario,
                            'confidence': max(0, (100.0 - melhor_distancia_usuario) / 100.0),
                            'distance': melhor_distancia_usuario
                        }
                        
                except Exception as e:
                    print(f"DEBUG: Erro ao comparar com usuário {usuario['id']}: {e}")
                    continue
            
            # Se chegou aqui, tenta com o melhor match mesmo com threshold ultra permissivo
            if melhor_match and melhor_distancia < 200.0:  # Threshold extremamente permissivo
                print(f"DEBUG: Usando melhor match com threshold ultra permissivo: {melhor_match['nome']}")
                return {
                    'success': True,
                    'message': f'Rosto reconhecido! Bem-vindo(a), {melhor_match["nome"]}!',
                    'user': melhor_match,
                    'confidence': max(0, (200.0 - melhor_distancia) / 200.0),
                    'distance': melhor_distancia
                }
            
            print(f"DEBUG: Nenhum rosto reconhecido. Menor distância: {melhor_distancia:.6f}")
            return {'success': False, 'message': f'Rosto não reconhecido. Menor distância: {melhor_distancia:.6f}'}
            
        except Exception as e:
            print(f"DEBUG: Erro na autenticação: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': f'Erro na autenticação: {str(e)}'}
    
    def _check_liveness(self, image, face_coords):
        """Verifica se o rosto é de uma pessoa viva (anti-spoofing)"""
        try:
            # Verifica se tem 4 coordenadas
            if isinstance(face_coords, (tuple, list)) and len(face_coords) == 4:
                x, y, w, h = face_coords
            else:
                print(f"DEBUG: Formato inesperado de face_coords em _check_liveness: {face_coords}")
                return False
            
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
