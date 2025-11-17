"""
Sistema de Reconhecimento Facial Avançado
Integrado com o sistema Flask e MySQL
"""
import cv2
import numpy as np
import pickle
import base64
import os
import sys
from datetime import datetime
from typing import List, Tuple, Optional, Dict

# Adicionar o caminho do projeto para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))

from app.models.models import Usuario, get_db
from app.controllers.controller import UsuarioController

class AdvancedFaceRecognition:
    """Sistema completo de reconhecimento facial com anti-spoofing"""
    
    def __init__(self):
        # Configurações do OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        # Configurações da webcam
        self.webcam = None
        self.camera_running = False
        
        # Parâmetros de reconhecimento
        self.face_recognition_threshold = 0.6  # Limiar de similaridade
        self.min_face_size = (80, 80)  # Tamanho mínimo do rosto
        self.anti_spoofing_enabled = True
        
        # Cache de usuários cadastrados
        self.known_faces = []
        self.last_update = None
        
        # Controle de frames para anti-spoofing
        self.frame_history = []
        self.max_history = 10
        
    def initialize_camera(self, camera_id: int = 0) -> bool:
        """Inicializa a câmera com configurações otimizadas"""
        try:
            self.webcam = cv2.VideoCapture(camera_id)
            
            # Configurações para melhor qualidade
            self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.webcam.set(cv2.CAP_PROP_FPS, 30)
            self.webcam.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            
            # Testa se a câmera foi inicializada
            if self.webcam.isOpened():
                self.camera_running = True
                print("✅ Câmera inicializada com sucesso")
                return True
            else:
                print("❌ Falha ao inicializar câmera")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao inicializar câmera: {e}")
            return False
    
    def load_known_faces(self) -> bool:
        """Carrega todos os usuários com rosto cadastrado do banco"""
        try:
            print("🔄 Carregando rostos cadastrados...")
            
            # Obtém usuários com rosto cadastrado
            usuarios = UsuarioController.listar_usuarios_com_rosto()
            
            self.known_faces = []
            loaded_count = 0
            
            for usuario in usuarios:
                if usuario['rosto']:
                    try:
                        # Decodifica o encoding do banco
                        encoding_data = self._decode_face_encoding(usuario['rosto'])
                        
                        if encoding_data is not None:
                            self.known_faces.append({
                                'id': usuario['id'],
                                'nome': usuario['nome'],
                                'email': usuario['email'],
                                'encoding': encoding_data
                            })
                            loaded_count += 1
                            print(f"✅ Rosto carregado: {usuario['nome']}")
                        else:
                            print(f"⚠️ Encoding inválido para: {usuario['nome']}")
                            
                    except Exception as e:
                        print(f"❌ Erro ao processar rosto de {usuario['nome']}: {e}")
            
            print(f"📊 Total de rostos carregados: {loaded_count}")
            self.last_update = datetime.now()
            return loaded_count > 0
            
        except Exception as e:
            print(f"❌ Erro ao carregar rostos: {e}")
            return False
    
    def _decode_face_encoding(self, encoding_data) -> Optional[np.ndarray]:
        """Decodifica encoding do banco de dados"""
        try:
            if not encoding_data:
                return None
            
            # Se for bytes (BLOB do banco)
            if isinstance(encoding_data, bytes):
                try:
                    # Tenta decodificar como pickle
                    encoding = pickle.loads(encoding_data)
                    if isinstance(encoding, np.ndarray):
                        return encoding
                except:
                    pass
                
                # Tenta decodificar como base64
                try:
                    encoding_str = base64.b64encode(encoding_data).decode('utf-8')
                    encoding_bytes = base64.b64decode(encoding_str)
                    encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                    return encoding
                except:
                    pass
            
            # Se for string base64
            elif isinstance(encoding_data, str):
                try:
                    # Remove prefix se existir
                    if ',' in encoding_data:
                        encoding_data = encoding_data.split(',')[1]
                    
                    encoding_bytes = base64.b64decode(encoding_data)
                    encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                    return encoding
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"❌ Erro na decodificação: {e}")
            return None
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detecta rostos em um frame com filtros de qualidade"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Equalização de histograma para melhorar contraste
            gray = cv2.equalizeHist(gray)
            
            # Detecção com parâmetros otimizados
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,  # Menos escalonamento para mais precisão
                minNeighbors=5,    # Mais vizinhos para menos falsos positivos
                minSize=self.min_face_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Filtra rostos muito pequenos ou em posições estranhas
            valid_faces = []
            for (x, y, w, h) in faces:
                # Verifica proporção razoável do rosto
                aspect_ratio = w / h
                if 0.7 <= aspect_ratio <= 1.5:  # Proporção normal de rosto
                    valid_faces.append((x, y, w, h))
            
            return valid_faces
            
        except Exception as e:
            print(f"❌ Erro na detecção de rostos: {e}")
            return []
    
    def verify_liveness(self, frame: np.ndarray, face_rect: Tuple[int, int, int, int]) -> bool:
        """Verifica se é uma pessoa real (anti-spoofing)"""
        if not self.anti_spoofing_enabled:
            return True
        
        try:
            x, y, w, h = face_rect
            
            # Extrai região do rosto
            face_region = frame[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return False
            
            # 1. Detecção de olhos (básico anti-spoofing)
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            eyes = self.eye_cascade.detectMultiScale(gray_face, 1.1, 3)
            
            if len(eyes) < 2:
                return False
            
            # 2. Análise de blur (fotos geralmente têm mais blur)
            blur_score = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            if blur_score < 100:  # Muito borrado = provavelmente foto
                return False
            
            # 3. Análise de brilho e contraste
            brightness = np.mean(gray_face)
            contrast = np.std(gray_face)
            
            if brightness < 40 or brightness > 200:  # Muito escuro ou muito claro
                return False
            
            if contrast < 30:  # Baixo contraste = possível foto
                return False
            
            # 4. Detecção de movimento (se houver histórico)
            if len(self.frame_history) > 0:
                # Compara com frame anterior para detectar movimento
                prev_gray = cv2.cvtColor(self.frame_history[-1], cv2.COLOR_BGR2GRAY)
                current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Calcula diferença absoluta
                diff = cv2.absdiff(prev_gray, current_gray)
                motion_score = np.mean(diff)
                
                # Se não houver movimento suficiente, pode ser foto
                if motion_score < 5:
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na verificação de liveness: {e}")
            return False
    
    def extract_face_features(self, frame: np.ndarray, face_rect: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Extrai características do rosto para comparação"""
        try:
            x, y, w, h = face_rect
            
            # Extrai região do rosto
            face_region = frame[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return None
            
            # Redimensiona para tamanho padrão
            face_resized = cv2.resize(face_region, (100, 100))
            
            # Converte para escala de cinza
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            
            # Normalização
            face_normalized = face_gray / 255.0
            
            # Cria um vetor de características simples
            # (em um sistema real, usaríamos redes neurais como FaceNet)
            features = face_normalized.flatten()
            
            return features.astype(np.float64)
            
        except Exception as e:
            print(f"❌ Erro na extração de características: {e}")
            return None
    
    def compare_faces(self, face_features: np.ndarray) -> Optional[Dict]:
        """Compara rosto detectado com rostos cadastrados"""
        if len(self.known_faces) == 0:
            return None
        
        try:
            best_match = None
            best_score = float('inf')
            
            for known_face in self.known_faces:
                # Calcula distância euclidiana
                distance = np.linalg.norm(face_features - known_face['encoding'])
                
                # Se a distância for menor que o limiar e for a melhor até agora
                if distance < self.face_recognition_threshold and distance < best_score:
                    best_score = distance
                    best_match = known_face
            
            if best_match:
                return {
                    'user': best_match,
                    'confidence': 1 - (best_score / self.face_recognition_threshold),
                    'distance': best_score
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Erro na comparação de rostos: {e}")
            return None
    
    def authenticate_user(self, max_attempts: int = 10) -> Optional[Dict]:
        """Processo completo de autenticação facial"""
        if not self.camera_running:
            if not self.initialize_camera():
                return None
        
        if not self.load_known_faces():
            print("❌ Nenhum rosto cadastrado encontrado")
            return None
        
        print("🎥 Iniciando autenticação facial...")
        print("👤 Posicione seu rosto na câmera")
        print("⏱️ Aguardando reconhecimento...")
        
        attempts = 0
        consecutive_detections = 0
        required_consecutive = 3  # Detecções consecutivas para confirmar
        
        while attempts < max_attempts:
            ret, frame = self.webcam.read()
            
            if not ret:
                print("❌ Falha ao capturar frame")
                attempts += 1
                continue
            
            # Adiciona ao histórico para análise de movimento
            self.frame_history.append(frame.copy())
            if len(self.frame_history) > self.max_history:
                self.frame_history.pop(0)
            
            # Detecta rostos
            faces = self.detect_faces(frame)
            
            if len(faces) > 0:
                # Pega o maior rosto detectado
                face_rect = max(faces, key=lambda f: f[2] * f[3])
                
                # Verifica liveness
                if self.verify_liveness(frame, face_rect):
                    # Extrai características
                    face_features = self.extract_face_features(frame, face_rect)
                    
                    if face_features is not None:
                        # Compara com rostos cadastrados
                        match = self.compare_faces(face_features)
                        
                        if match:
                            consecutive_detections += 1
                            
                            # Desenha retângulo verde
                            x, y, w, h = face_rect
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(frame, f"Reconhecido: {match['user']['nome']}", 
                                      (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            print(f"✅ Detecção {consecutive_detections}/{required_consecutive}: {match['user']['nome']}")
                            
                            # Se tiver detecções consecutivas suficientes, autentica
                            if consecutive_detections >= required_consecutive:
                                print(f"🎉 Usuário autenticado: {match['user']['nome']}")
                                print(f"📧 Email: {match['user']['email']}")
                                print(f"🎯 Confiança: {match['confidence']:.2f}")
                                
                                return match
                        else:
                            consecutive_detections = 0
                            # Desenha retângulo vermelho
                            x, y, w, h = face_rect
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                            cv2.putText(frame, "Nao reconhecido", 
                                      (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    # Falha no anti-spoofing
                    x, y, w, h = face_rect
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                    cv2.putText(frame, "Verificando...", 
                              (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                consecutive_detections = 0
            
            # Mostra o frame
            cv2.imshow('Autenticacao Facial', frame)
            
            # Verifica se usuário quer sair
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("❌ Autenticação cancelada pelo usuário")
                break
            
            attempts += 1
        
        print("❌ Falha na autenticação: número máximo de tentativas atingido")
        return None
    
    def register_new_face(self, user_id: int, num_samples: int = 10) -> bool:
        """Cadastro de novo rosto no sistema"""
        if not self.camera_running:
            if not self.initialize_camera():
                return False
        
        print(f"📸 Iniciando cadastro facial para usuário ID: {user_id}")
        print("👤 Posicione seu rosto bem centralizado na câmera")
        print("⏱️ Mantenha a posição por alguns segundos...")
        
        samples_collected = []
        quality_threshold = 50  # Qualidade mínima da imagem
        
        while len(samples_collected) < num_samples:
            ret, frame = self.webcam.read()
            
            if not ret:
                continue
            
            # Detecta rostos
            faces = self.detect_faces(frame)
            
            if len(faces) > 0:
                # Pega o maior rosto
                face_rect = max(faces, key=lambda f: f[2] * f[3])
                
                # Verifica qualidade e liveness
                if self.verify_liveness(frame, face_rect):
                    # Extrai características
                    face_features = self.extract_face_features(frame, face_rect)
                    
                    if face_features is not None:
                        # Verifica qualidade das características
                        quality_score = np.std(face_features)
                        
                        if quality_score > quality_threshold:
                            samples_collected.append(face_features)
                            
                            # Desenha retângulo verde
                            x, y, w, h = face_rect
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(frame, f"Amostra {len(samples_collected)}/{num_samples}", 
                                      (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            print(f"✅ Amostra {len(samples_collected)}/{num_samples} coletada")
                        else:
                            # Baixa qualidade
                            x, y, w, h = face_rect
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                            cv2.putText(frame, "Baixa qualidade", 
                                      (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                else:
                    # Falha na verificação
                    x, y, w, h = face_rect
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "Verificando...", 
                              (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Mostra o frame
            cv2.imshow('Cadastro Facial', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("❌ Cadastro cancelado")
                return False
        
        # Calcula média das amostras para criar um template robusto
        if len(samples_collected) >= 5:  # Mínimo de amostras
            try:
                # Remove outliers (amostras muito diferentes)
                samples_array = np.array(samples_collected)
                mean_sample = np.mean(samples_array, axis=0)
                
                # Codifica para armazenamento
                encoded_data = pickle.dumps(mean_sample)
                
                # Salva no banco de dados
                conn = get_db()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE usuario SET rosto = %s WHERE id = %s",
                        (encoded_data, user_id)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    print(f"✅ Rosto cadastrado com sucesso para usuário ID: {user_id}")
                    return True
                else:
                    print("❌ Erro de conexão com o banco de dados")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro ao salvar rosto no banco: {e}")
                return False
        else:
            print("❌ Não foram coletadas amostras suficientes")
            return False
    
    def cleanup(self):
        """Libera recursos"""
        if self.webcam:
            self.webcam.release()
        cv2.destroyAllWindows()
        self.camera_running = False


def main():
    """Função principal para testes"""
    print("🚀 Iniciando Sistema de Reconhecimento Facial Avançado")
    print("=" * 60)
    
    # Inicializa o sistema
    face_system = AdvancedFaceRecognition()
    
    try:
        # Menu de opções
        while True:
            print("\n📋 MENU:")
            print("1. 🔐 Autenticar usuário")
            print("2. 📸 Cadastrar novo rosto")
            print("3. 🔄 Recarregar rostos cadastrados")
            print("4. ❌ Sair")
            
            option = input("\n👉 Escolha uma opção (1-4): ").strip()
            
            if option == '1':
                print("\n🔐 INICIANDO AUTENTICAÇÃO FACIAL")
                print("Pressione 'q' para cancelar a qualquer momento\n")
                
                result = face_system.authenticate_user()
                
                if result:
                    print(f"\n🎉 AUTENTICAÇÃO BEM-SUCEDIDA!")
                    print(f"👤 Usuário: {result['user']['nome']}")
                    print(f"📧 Email: {result['user']['email']}")
                    print(f"🎯 Confiança: {result['confidence']:.2f}")
                    
                    # Aqui você pode integrar com o sistema Flask
                    # Ex: criar sessão, redirecionar para dashboard, etc.
                else:
                    print("\n❌ FALHA NA AUTENTICAÇÃO!")
                    print("Tente novamente ou contate o administrador.")
            
            elif option == '2':
                print("\n📸 CADASTRO DE NOVO ROSTO")
                user_id = input("👉 Digite o ID do usuário: ").strip()
                
                if user_id.isdigit():
                    user_id = int(user_id)
                    
                    print("Pressione 'q' para cancelar a qualquer momento\n")
                    success = face_system.register_new_face(user_id)
                    
                    if success:
                        print("\n✅ ROSTO CADASTRADO COM SUCESSO!")
                    else:
                        print("\n❌ FALHA NO CADASTRO!")
                else:
                    print("❌ ID inválido!")
            
            elif option == '3':
                print("\n🔄 RECARREGANDO ROSTOS CADASTRADOS...")
                success = face_system.load_known_faces()
                
                if success:
                    print("✅ Rostos recarregados com sucesso!")
                else:
                    print("❌ Erro ao recarregar rostos!")
            
            elif option == '4':
                print("\n👋 Encerrando sistema...")
                break
            
            else:
                print("❌ Opção inválida!")
    
    except KeyboardInterrupt:
        print("\n\n👋 Sistema interrompido pelo usuário")
    
    finally:
        face_system.cleanup()
        print("✅ Sistema encerrado")


if __name__ == "__main__":
    main()
    
