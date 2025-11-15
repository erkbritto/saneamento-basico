# models.py - Operações CRUD para todas as entidades do sistema

import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

def get_db():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE')
        )
        return connection
    except Error as e:
        print(f"Erro ao conectar: {e}")
        return None


# Classe Usuario
class Usuario:
    def __init__(self, id=None, nome=None, email=None, senha=None, cargo=None, 
                 status='ATIVO', departamento=None, ultimo_acesso=None, rosto=None, criado_em=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.cargo = cargo  # ENUM: 'FUNCIONARIO', 'SUPERVISOR', 'MASTER'
        self.status = status  # ENUM: 'ATIVO', 'INATIVO', 'PENDENTE'
        self.departamento = departamento
        self.ultimo_acesso = ultimo_acesso
        self.rosto = rosto
        self.criado_em = criado_em

    @staticmethod
    def criar(nome, email, senha, cargo, departamento=None, rosto=None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuario (nome, email, senha, cargo, departamento, rosto, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'ATIVO')
        """, (nome, email, senha, cargo, departamento, rosto))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def buscar_usuarios_com_faceid():
        """Busca todos os usuários que possuem FaceID cadastrado"""
        conn = get_db()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome, email, cargo, rosto 
                FROM usuario 
                WHERE rosto IS NOT NULL
            """)
            users = cursor.fetchall()
            cursor.close()
            return users
        except Error as e:
            print(f"Erro ao buscar usuários com FaceID: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    @staticmethod
    def verificar_faceid_cadastrado(user_id):
        """Verifica se um usuário específico tem FaceID cadastrado"""
        conn = get_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM usuario 
                WHERE id = %s AND rosto IS NOT NULL
            """, (user_id,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count > 0
        except Error as e:
            print(f"Erro ao verificar FaceID: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    @staticmethod
    def buscar_por_email(email):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return Usuario(**user)
        return None
    
    @staticmethod
    def buscar_por_id(user_id):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return Usuario(**user)
        return None
    
    @staticmethod
    def atualizar_face_encoding(user_id, face_encoding):
        """Atualiza o encoding facial do usuário"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuario SET rosto = %s WHERE id = %s", (face_encoding, user_id))
        conn.commit()
        cursor.close()
        conn.close()
    
    @staticmethod
    def buscar_usuarios_com_faceid():
        """Retorna todos os usuários que possuem FaceID cadastrado"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, rosto FROM usuario WHERE rosto IS NOT NULL AND rosto != ''")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    
    @staticmethod
    def verificar_faceid_cadastrado(user_id):
        """Verifica se o usuário tem FaceID cadastrado"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT rosto FROM usuario WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result and result.get('rosto'):
            return True
        return False

    @staticmethod
    def atualizar(id, **kwargs):
        conn = get_db()
        cursor = conn.cursor()
        campos = ', '.join([f"{k}=%s" for k in kwargs.keys()])
        valores = list(kwargs.values()) + [id]
        cursor.execute(f"UPDATE usuario SET {campos} WHERE id=%s", valores)
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def deletar(id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

def criar_usuario(nome, email, senha, cargo, departamento, rosto=None):
    Usuario.criar(nome, email, senha, cargo, departamento, rosto)

def buscar_usuario_por_email(email):
    return Usuario.buscar_por_email(email)

def atualizar_usuario(id, **kwargs):
    Usuario.atualizar(id, **kwargs)

def deletar_usuario(id):
    Usuario.deletar(id)

# Classe Tarefa
class Tarefa:
    def __init__(self, titulo, descricao=None, status='PENDENTE', gerente_id=None, id=None):
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.status = status  # ENUM: 'PENDENTE', 'ANDAMENTO', 'CONCLUIDA'
        self.gerente_id = gerente_id
        self.data_criacao = None
        self.data_conclusao = None
    
    @staticmethod
    def criar(titulo, descricao, gerente_id=None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tarefa (titulo, descricao, gerente_id, status)
            VALUES (%s, %s, %s, 'PENDENTE')
        """, (titulo, descricao, gerente_id))
        conn.commit()
        cursor.close()
        conn.close()
    
    @staticmethod
    def buscar_por_usuario(usuario_id):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.* FROM tarefa t
            JOIN funcionario_tarefa ft ON ft.tarefa_id = t.id
            WHERE ft.funcionario_id = %s
        """, (usuario_id,))
        tarefas = cursor.fetchall()
        cursor.close()
        conn.close()
        return tarefas
    
    @staticmethod
    def buscar_todas():
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tarefa ORDER BY data_criacao DESC")
        tarefas = cursor.fetchall()
        cursor.close()
        conn.close()
        return tarefas

# Classe Ponto
class Ponto:
    def __init__(self, usuario_id, data, hora_entrada=None, hora_saida=None, total_horas=None, status='REGISTRADO', id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.data = data
        self.hora_entrada = hora_entrada
        self.hora_saida = hora_saida
        self.total_horas = total_horas
        self.status = status  # ENUM: 'REGISTRADO', 'FALTA', 'JUSTIFICADO'
        self.criado_em = None
    
    @staticmethod
    def registrar(usuario_id, data, hora_entrada=None, hora_saida=None, total_horas=None, status='REGISTRADO'):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ponto (usuario_id, data, hora_entrada, hora_saida, total_horas, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario_id, data, hora_entrada, hora_saida, total_horas, status))
        conn.commit()
        cursor.close()
        conn.close()
    
    @staticmethod
    def buscar_por_usuario(usuario_id, data_inicio=None, data_fim=None):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        if data_inicio and data_fim:
            cursor.execute("""
                SELECT * FROM ponto 
                WHERE usuario_id = %s AND data BETWEEN %s AND %s
                ORDER BY data DESC
            """, (usuario_id, data_inicio, data_fim))
        else:
            cursor.execute("""
                SELECT * FROM ponto 
                WHERE usuario_id = %s
                ORDER BY data DESC
            """, (usuario_id,))
        
        pontos = cursor.fetchall()
        cursor.close()
        conn.close()
        return pontos

# Classe Auditoria
class Auditoria:
    def __init__(self, usuario_id, acao, ip=None, status='SUCESSO', detalhes=None, id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.acao = acao
        self.ip = ip
        self.status = status  # ENUM: 'SUCESSO', 'FALHA'
        self.detalhes = detalhes
        self.data_hora = None
    
    @staticmethod
    def registrar(usuario_id, acao, ip=None, status='SUCESSO', detalhes=None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO auditoria (usuario_id, acao, ip, status, detalhes)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, acao, ip, status, detalhes))
        conn.commit()
        cursor.close()
        conn.close()
    
    @staticmethod
    def buscar(usuario_id=None, data_inicio=None, data_fim=None):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT a.*, u.nome as nome_usuario 
            FROM auditoria a 
            LEFT JOIN usuario u ON a.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if usuario_id:
            query += " AND a.usuario_id = %s"
            params.append(usuario_id)
        
        if data_inicio and data_fim:
            query += " AND DATE(a.data_hora) BETWEEN %s AND %s"
            params.extend([data_inicio, data_fim])
        
        query += " ORDER BY a.data_hora DESC"
        
        cursor.execute(query, params)
        auditorias = cursor.fetchall()
        cursor.close()
        conn.close()
        return auditorias

# Funções de acesso e regras de negócio podem ser expandidas conforme necessidade do sistema
