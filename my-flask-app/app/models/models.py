# models.py - Operações CRUD para todas as entidades do sistema

import os
from database.db_connection import main as get_connection
import mysql.connector
from mysql.connector import Error

# Função utilitária para obter conexão

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
    def __init__(self, nome, email, senha, cargo, departamento, rosto=None, id=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.cargo = cargo
        self.departamento = departamento
        self.rosto = rosto

    @staticmethod
    def criar(nome, email, senha, cargo, departamento, rosto=None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuario (nome, email, senha, cargo, departamento, rosto)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, email, senha, cargo, departamento, rosto))
        conn.commit()
        cursor.close()
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

# CRUD TAREFA

def criar_tarefa(titulo, descricao, gerente_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tarefa (titulo, descricao, gerente_id)
        VALUES (%s, %s, %s)
    """, (titulo, descricao, gerente_id))
    conn.commit()
    cursor.close()
    conn.close()


def buscar_tarefas_por_usuario(usuario_id):
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

# CRUD PONTO

def registrar_ponto(usuario_id, data, hora_entrada, hora_saida, total_horas, status='REGISTRADO'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ponto (usuario_id, data, hora_entrada, hora_saida, total_horas, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (usuario_id, data, hora_entrada, hora_saida, total_horas, status))
    conn.commit()
    cursor.close()
    conn.close()

# CRUD AUDITORIA

def registrar_auditoria(usuario_id, acao, ip, status='SUCESSO'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO auditoria (usuario_id, acao, ip, status)
        VALUES (%s, %s, %s, %s)
    """, (usuario_id, acao, ip, status))
    conn.commit()
    cursor.close()
    conn.close()

# Funções de acesso e regras de negócio podem ser expandidas conforme necessidade do sistema
