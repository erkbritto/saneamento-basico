"""Controllers - Camada de lógica de negócio"""

from app.models.models import (
    Usuario, 
    buscar_tarefas_por_usuario,
    registrar_ponto as model_registrar_ponto,
    registrar_auditoria
)
from datetime import datetime
import json


class UsuarioController:
    """Controller para operações de usuário"""
    
    @staticmethod
    def autenticar(email, password):
        """Autentica um usuário"""
        # TODO: Implementar autenticação real com banco de dados
        # Por enquanto, mantém a lógica fictícia
        users = {
            'admin@gmail.com': {'password': 'admin123', 'role': 'GOVERNANTE', 'name': 'Administrador'},
            'supervisor@gmail.com': {'password': 'super123', 'role': 'SUPERVISOR', 'name': 'Supervisor'},
            'funcionario@gmail.com': {'password': 'func123', 'role': 'FUNCIONARIO', 'name': 'Funcionário'}
        }
        
        if email in users and users[email]['password'] == password:
            return {
                'success': True,
                'user': users[email]
            }
        return {
            'success': False,
            'message': 'Credenciais inválidas'
        }
    
    @staticmethod
    def criar_usuario(nome, email, senha, cargo, departamento, status='ATIVO', rosto=None):
        """Cria um novo usuário com validações"""
        # Validações
        if not all([nome, email, senha, cargo, departamento, status]):
            return {'success': False, 'message': 'Preencha todos os campos obrigatórios.'}
        
        if cargo not in ['FUNCIONARIO', 'SUPERVISOR', 'MASTER']:
            return {'success': False, 'message': 'Cargo inválido.'}
        
        if status not in ['ATIVO', 'INATIVO', 'PENDENTE']:
            return {'success': False, 'message': 'Status inválido.'}
        
        if '@' not in email or '.' not in email:
            return {'success': False, 'message': 'Email inválido.'}
        
        if len(senha) < 6:
            return {'success': False, 'message': 'A senha deve ter pelo menos 6 caracteres.'}
        
        try:
            Usuario.criar(nome, email, senha, cargo, departamento, rosto)
            return {'success': True, 'message': 'Usuário cadastrado com sucesso!'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao cadastrar usuário: {str(e)}'}
    
    @staticmethod
    def listar_usuarios():
        """Lista todos os usuários"""
        try:
            conn = Usuario.get_db()
            if not conn:
                return {'success': False, 'usuarios': [], 'message': 'Falha na conexão com o banco de dados.'}
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nome, cargo, departamento FROM usuario")
            usuarios = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return {'success': True, 'usuarios': usuarios}
        except Exception as e:
            return {'success': False, 'usuarios': [], 'message': f'Erro ao listar usuários: {str(e)}'}
    
    @staticmethod
    def atualizar_usuario(id, **kwargs):
        """Atualiza um usuário"""
        try:
            Usuario.atualizar(id, **kwargs)
            return {'success': True, 'message': 'Usuário atualizado com sucesso!'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao atualizar usuário: {str(e)}'}
    
    @staticmethod
    def deletar_usuario(id):
        """Deleta um usuário"""
        try:
            Usuario.deletar(id)
            return {'success': True, 'message': 'Usuário deletado com sucesso!'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao deletar usuário: {str(e)}'}


class TarefaController:
    """Controller para operações de tarefas"""
    
    @staticmethod
    def listar_tarefas_usuario(usuario_id):
        """Lista tarefas de um usuário específico"""
        if not usuario_id:
            return {'success': False, 'message': 'usuario_id é obrigatório.'}
        
        try:
            conn = Usuario.get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.id, t.titulo, t.status, t.data_criacao, t.data_conclusao
                FROM tarefa t
                JOIN funcionario_tarefa ft ON t.id = ft.tarefa_id
                WHERE ft.funcionario_id = %s
                ORDER BY t.data_criacao DESC
            """, (usuario_id,))
            tarefas = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return {'success': True, 'tarefas': tarefas}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao buscar tarefas: {str(e)}'}


class PontoController:
    """Controller para operações de ponto eletrônico"""
    
    @staticmethod
    def listar_historico(usuario_id):
        """Lista histórico de ponto de um usuário"""
        if not usuario_id:
            return {'success': False, 'message': 'usuario_id é obrigatório.'}
        
        try:
            conn = Usuario.get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, data, hora_entrada, hora_saida, total_horas, status "
                "FROM ponto WHERE usuario_id=%s ORDER BY data DESC",
                (usuario_id,)
            )
            pontos = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return {'success': True, 'historico': pontos}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao buscar histórico: {str(e)}'}
    
    @staticmethod
    def registrar_ponto(usuario_id, data_ponto, hora_entrada, localizacao=None):
        """Registra ponto eletrônico"""
        if not all([usuario_id, data_ponto, hora_entrada]):
            return {'success': False, 'message': 'Campos obrigatórios ausentes.'}
        
        try:
            conn = Usuario.get_db()
            cursor = conn.cursor(dictionary=True)
            
            # Verifica duplicidade
            cursor.execute(
                "SELECT id FROM ponto WHERE usuario_id=%s AND data=%s",
                (usuario_id, data_ponto)
            )
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return {'success': False, 'message': 'Ponto já registrado para este usuário e data.'}
            
            # Insere registro de ponto
            cursor.execute(
                "INSERT INTO ponto (usuario_id, data, hora_entrada, status) VALUES (%s, %s, %s, 'REGISTRADO')",
                (usuario_id, data_ponto, hora_entrada)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            return {'success': True, 'message': 'Ponto registrado com sucesso.'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao registrar ponto: {str(e)}'}


class DashboardController:
    """Controller para dados do dashboard"""
    
    @staticmethod
    def obter_dados_dashboard(user_role):
        """Retorna dados do dashboard baseado no papel do usuário"""
        import time
        
        # Dados base para todos os usuários
        data = {
            'activeUsers': 42,
            'efficiency': 87,
            'timestamp': time.time()
        }
        
        # Dados adicionais para GOVERNANTE e SUPERVISOR
        if user_role in ['GOVERNANTE', 'SUPERVISOR']:
            data.update({
                'environmentImpact': 76,
                'criticalAlerts': 3
            })
        
        # Dados específicos para GOVERNANTE
        if user_role == 'GOVERNANTE':
            data.update({
                'airQuality': 85,
                'waterQuality': 92,
                'wasteManagement': 78,
                'greenCoverage': 65
            })
        
        return data


class RelatorioController:
    """Controller para geração de relatórios"""
    
    @staticmethod
    def gerar_relatorio(period='week', start=None, end=None):
        """Gera relatório de tarefas por período"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        # Definir intervalo de datas
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'week':
            start_date = now - timedelta(days=now.weekday())
            end_date = now
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'custom' and start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
        else:
            start_date = now - timedelta(days=7)
            end_date = now
        
        try:
            conn = Usuario.get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.id, t.titulo, t.status, t.data_criacao, t.data_conclusao, u.nome as gerente
                FROM tarefa t
                LEFT JOIN usuario u ON t.gerente_id = u.id
                WHERE t.data_criacao >= %s AND t.data_criacao <= %s
            """, (start_date, end_date))
            tarefas = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return {'success': True, 'tarefas': tarefas}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao gerar relatório: {str(e)}'}


class AuditoriaController:
    """Controller para auditoria"""
    
    @staticmethod
    def listar_registros(usuario=None, data_inicial=None, data_final=None):
        """Lista registros de auditoria com filtros"""
        # TODO: Implementar consulta real ao banco
        registros = [
            {
                'data_hora': '2025-09-26 14:32',
                'usuario': 'admin@gmail.com',
                'acao': 'Login realizado',
                'ip': '127.0.0.1',
                'status': 'Sucesso'
            },
            {
                'data_hora': '2025-09-26 13:12',
                'usuario': 'erick@teste.com',
                'acao': 'Tentativa de login',
                'ip': '192.168.0.15',
                'status': 'Falha'
            },
            {
                'data_hora': '2025-09-25 19:44',
                'usuario': 'supervisor@empresa.com',
                'acao': 'Alteração em Tarefas',
                'ip': '10.0.0.5',
                'status': 'Info'
            }
        ]
        
        # Filtros simulados
        if usuario:
            registros = [r for r in registros if usuario.lower() in r['usuario'].lower()]
        
        return {'success': True, 'registros': registros}


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
            # TODO: Implementar sistema de reconhecimento facial
            # from app.utils.face_recognition_utils import face_system
            # result = face_system.register_face(image_base64)
            
            # Por enquanto, retorna sucesso simulado
            # Usuario.atualizar_face_encoding(user_id, result['encoding'])
            return {'success': True, 'message': 'FaceID cadastrado com sucesso!'}
        except Exception as e:
            return {'success': False, 'message': f'Erro no servidor: {str(e)}'}
    
    @staticmethod
    def autenticar_faceid(image_base64):
        """Autentica usuário via FaceID"""
        if not image_base64:
            return {'success': False, 'message': 'Imagem é obrigatória'}
        
        try:
            users_with_faceid = Usuario.buscar_usuarios_com_faceid()
            
            if not users_with_faceid:
                return {
                    'success': False,
                    'message': 'Nenhum usuário com FaceID cadastrado. Use login tradicional.'
                }
            
            # TODO: Implementar reconhecimento facial real
            # from app.utils.face_recognition_utils import face_system
            # best_match = None
            # best_confidence = 0
            # 
            # for user in users_with_faceid:
            #     result = face_system.authenticate_face(image_base64, user['rosto'])
            #     if result['success'] and result['confidence'] > best_confidence:
            #         best_confidence = result['confidence']
            #         best_match = user
            
            # Por enquanto, retorna erro
            return {
                'success': False,
                'message': 'Rosto não reconhecido. Tente novamente ou use login tradicional.'
            }
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
