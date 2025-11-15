# controllers/controller.py - Controllers para todas as entidades do sistema

import base64
import cv2
import numpy as np
from datetime import datetime
from app.models.models import Usuario, Tarefa, Ponto, Auditoria, get_db
from app.utils.face_utils import FaceRecognitionUtils
import hashlib

class UsuarioController:
    """Controller para operações de usuários"""
    
    @staticmethod
    def criar_usuario(nome, email, senha, cargo, departamento=None, rosto=None):
        """Cria um novo usuário com reconhecimento facial opcional"""
        try:
            # Verifica se email já existe
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuario WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return {'success': False, 'message': 'Email já cadastrado. Use outro email.'}
            
            # Hash da senha
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            
            # Cria o usuário primeiro sem o rosto
            cursor.execute("""
                INSERT INTO usuario (nome, email, senha, cargo, departamento, status, criado_em)
                VALUES (%s, %s, %s, %s, %s, 'ATIVO', NOW())
            """, (nome, email, senha_hash, cargo, departamento))
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            conn.close()

            # Se houver dados de rosto, processa o reconhecimento facial
            if rosto and rosto.strip():
                try:
                    # Verifica se é um JSON do face-api.js ou base64
                    if rosto.startswith('{'):
                        # É JSON do face-api.js - converte para base64
                        import json
                        face_data = json.loads(rosto)
                        # Tenta registrar o FaceID
                        result = FaceIDController.registrar_faceid(user_id, rosto)
                        if not result['success']:
                            print(f"Erro ao registrar FaceID: {result['message']}")
                    else:
                        # É base64 direto
                        result = FaceIDController.registrar_faceid(user_id, rosto)
                        if not result['success']:
                            print(f"Erro ao registrar FaceID: {result['message']}")
                except Exception as e:
                    print(f"Erro ao processar FaceID: {e}")

            return {'success': True, 'message': 'Usuário criado com sucesso', 'user_id': user_id}
            
        except Exception as e:
            return {'success': False, 'message': f'Erro ao criar usuário: {str(e)}'}
    
    @staticmethod
    def autenticar_usuario(email, senha):
        """Autentica usuário por email e senha"""
        try:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM usuario 
                WHERE email = %s AND senha = %s AND status = 'ATIVO'
            """, (email, senha_hash))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                # Atualiza último acesso
                Usuario.atualizar(user['id'], ultimo_acesso=datetime.now())
                return {'success': True, 'user': user}
            else:
                return {'success': False, 'message': 'Email ou senha incorretos'}
                
        except Exception as e:
            return {'success': False, 'message': f'Erro ao autenticar: {str(e)}'}
    
    @staticmethod
    def buscar_usuario_por_id(user_id):
        """Busca usuário por ID"""
        try:
            return Usuario.buscar_por_id(user_id)
        except Exception as e:
            return None
    
    @staticmethod
    def atualizar_usuario(user_id, **kwargs):
        """Atualiza dados do usuário"""
        try:
            Usuario.atualizar(user_id, **kwargs)
            return {'success': True, 'message': 'Usuário atualizado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao atualizar: {str(e)}'}
    
    @staticmethod
    def listar_usuarios():
        """Lista todos os usuários"""
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nome, email, cargo, departamento, status FROM usuario ORDER BY nome")
            usuarios = cursor.fetchall()
            cursor.close()
            conn.close()
            return usuarios
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []

class FaceIDController:
    """Controller para operações de reconhecimento facial"""
    
    @staticmethod
    def registrar_faceid(user_id, image_base64):
        """Registra FaceID de um usuário"""
        if not user_id or not image_base64:
            return {'success': False, 'message': 'user_id e image são obrigatórios'}
        
        # Verifica se usuário existe
        user = Usuario.buscar_por_id(user_id)
        if not user:
            return {'success': False, 'message': 'Usuário não encontrado'}
        
        try:
            # Decodifica a imagem base64
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            img_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {'success': False, 'message': 'Erro ao processar a imagem'}
            
            # Usa FaceRecognitionUtils para registrar o rosto
            face_utils = FaceRecognitionUtils()
            encoding = face_utils.extract_face_encoding(frame)
            
            if encoding is None:
                return {'success': False, 'message': 'Nenhum rosto detectado na imagem'}
            
            # Salva o encoding no banco de dados
            encoding_str = base64.b64encode(encoding.tobytes()).decode('utf-8')
            Usuario.atualizar_face_encoding(user_id, encoding_str)
            
            return {'success': True, 'message': 'FaceID cadastrado com sucesso!'}
            
        except Exception as e:
            return {'success': False, 'message': f'Erro no servidor: {str(e)}'}
    
    @staticmethod
    def autenticar_faceid(image_base64):
        """Autentica usuário via FaceID"""
        if not image_base64:
            return {'success': False, 'message': 'Imagem é obrigatória'}
        
        try:
            # Decodifica a imagem base64
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            img_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {'success': False, 'message': 'Erro ao processar a imagem'}
            
            # Usa FaceRecognitionUtils para autenticar contra qualquer rosto conhecido
            face_utils = FaceRecognitionUtils()
            
            # Carrega todos os rostos cadastrados do banco
            users_with_faceid = Usuario.buscar_usuarios_com_faceid()
            if not users_with_faceid:
                return {'success': False, 'message': 'Nenhum usuário com FaceID cadastrado'}
            
            print(f"DEBUG: Encontrados {len(users_with_faceid)} usuários com FaceID")
            
            # Registra todos os rostos conhecidos no sistema
            for user in users_with_faceid:
                if user.get('rosto'):
                    try:
                        # Decodifica o encoding salvo
                        saved_encoding_bytes = base64.b64decode(user['rosto'])
                        saved_encoding = np.frombuffer(saved_encoding_bytes, dtype=np.float64)
                        
                        # Adiciona ao sistema de reconhecimento
                        face_utils.known_face_encodings.append(saved_encoding)
                        face_utils.known_face_ids.append(user['id'])
                        print(f"DEBUG: Rosto do usuário {user['id']} - {user['nome']} carregado")
                    except Exception as e:
                        print(f"DEBUG: Erro ao carregar rosto do usuário {user['id']}: {e}")
                        continue  # Pula usuários com encoding inválido
            
            print(f"DEBUG: Total de {len(face_utils.known_face_encodings)} rostos carregados para comparação")
            
            # Tenta autenticar contra qualquer rosto conhecido
            success, user_id, message = face_utils.authenticate_any_face(frame)
            print(f"DEBUG: Resultado da autenticação - Success: {success}, User ID: {user_id}, Message: {message}")
            
            if success and user_id:
                # Busca dados do usuário autenticado
                for user in users_with_faceid:
                    if user['id'] == user_id:
                        return {
                            'success': True,
                            'message': 'Autenticação por reconhecimento facial realizada com sucesso!',
                            'user': {
                                'id': user['id'],
                                'nome': user['nome'],
                                'email': user['email'],
                                'cargo': user['cargo']
                            }
                        }
            
            return {'success': False, 'message': 'Rosto não reconhecido. Tente novamente ou use login tradicional.'}
            
        except Exception as e:
            return {'success': False, 'message': f'Erro no servidor: {str(e)}'}

    @staticmethod
    def verificar_faceid_cadastrado(user_id):
        """Verifica se usuário tem FaceID cadastrado"""
        try:
            has_faceid = Usuario.verificar_faceid_cadastrado(user_id)
            return {'success': True, 'has_faceid': has_faceid}
        except Exception as e:
            return {'success': False, 'message': str(e)}

class TarefaController:
    """Controller para operações de tarefas"""
    
    @staticmethod
    def listar_tarefas_usuario(usuario_id):
        """Lista todas as tarefas de um usuário"""
        try:
            return Tarefa.buscar_por_usuario(usuario_id)
        except Exception as e:
            print(f"Erro ao listar tarefas: {e}")
            return []
    
    @staticmethod
    def criar_tarefa(titulo, descricao, gerente_id=None):
        """Cria uma nova tarefa"""
        try:
            Tarefa.criar(titulo, descricao, gerente_id)
            return {'success': True, 'message': 'Tarefa criada com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao criar tarefa: {str(e)}'}
    
    @staticmethod
    def listar_todas_tarefas():
        """Lista todas as tarefas do sistema"""
        try:
            return Tarefa.buscar_todas()
        except Exception as e:
            print(f"Erro ao listar tarefas: {e}")
            return []

class PontoController:
    """Controller para operações de ponto"""
    
    @staticmethod
    def registrar_ponto(usuario_id, data, hora_entrada=None, hora_saida=None, total_horas=None, status='REGISTRADO'):
        """Registra ponto do usuário"""
        try:
            Ponto.registrar(usuario_id, data, hora_entrada, hora_saida, total_horas, status)
            return {'success': True, 'message': 'Ponto registrado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao registrar ponto: {str(e)}'}
    
    @staticmethod
    def listar_pontos_usuario(usuario_id, data_inicio=None, data_fim=None):
        """Lista pontos de um usuário"""
        try:
            return Ponto.buscar_por_usuario(usuario_id, data_inicio, data_fim)
        except Exception as e:
            print(f"Erro ao listar pontos: {e}")
            return []

class DashboardController:
    """Controller para operações do dashboard"""
    
    @staticmethod
    def obter_dados_dashboard(usuario_id):
        """Obtém dados para o dashboard do usuário"""
        try:
            # Obter tarefas do usuário
            tarefas = Tarefa.buscar_por_usuario(usuario_id)
            
            # Obter pontos do usuário
            pontos = Ponto.buscar_por_usuario(usuario_id)
            
            # Obter auditorias recentes
            auditorias = Auditoria.buscar(usuario_id)
            
            return {
                'tarefas': tarefas,
                'pontos': pontos,
                'auditorias': auditorias[:10]  # Últimas 10 auditorias
            }
        except Exception as e:
            print(f"Erro ao obter dados do dashboard: {e}")
            return {'tarefas': [], 'pontos': [], 'auditorias': []}

class AuditoriaController:
    """Controller para operações de auditoria"""
    
    @staticmethod
    def registrar_auditoria(usuario_id, acao, ip=None, status='SUCESSO', detalhes=None):
        """Registra uma ação de auditoria"""
        try:
            Auditoria.registrar(usuario_id, acao, ip, status, detalhes)
            return {'success': True}
        except Exception as e:
            print(f"Erro ao registrar auditoria: {e}")
            return {'success': False}
    
    @staticmethod
    def listar_auditoria(usuario_id=None, data_inicio=None, data_fim=None):
        """Lista registros de auditoria"""
        try:
            return Auditoria.buscar(usuario_id, data_inicio, data_fim)
        except Exception as e:
            print(f"Erro ao listar auditoria: {e}")
            return []

class RelatorioController:
    """Controller para operações de relatórios"""
    
    @staticmethod
    def gerar_relatorio_pontos(usuario_id, data_inicio, data_fim):
        """Gera relatório de pontos no período"""
        try:
            pontos = Ponto.buscar_por_usuario(usuario_id, data_inicio, data_fim)
            return {'success': True, 'data': pontos}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao gerar relatório: {str(e)}'}
    
    @staticmethod
    def gerar_relatorio_tarefas(usuario_id, status=None):
        """Gera relatório de tarefas"""
        try:
            tarefas = Tarefa.buscar_por_usuario(usuario_id)
            if status:
                tarefas = [t for t in tarefas if t['status'] == status]
            return {'success': True, 'data': tarefas}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao gerar relatório: {str(e)}'}
