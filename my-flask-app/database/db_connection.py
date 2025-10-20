"""
Conexão simples e segura com MySQL.
"""

import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Carrega variáveis de ambiente
load_dotenv()

def main():
    try:
        # Verifica se todas as variáveis de ambiente necessárias estão presentes
        required_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_DATABASE']
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"❌ Variável de ambiente {var} não encontrada no arquivo .env")
        
        # Cria a conexão usando apenas variáveis do .env
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE')
        )

        if connection.is_connected():
            print("✅ Conexão estabelecida com sucesso!")
            
            # Exemplo: executar uma consulta simples para testar
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📋 Versão do MySQL: {version[0]}")
            
            # Mostra informações da conexão
            print(f"📍 Host: {os.getenv('DB_HOST')}")
            print(f"🚪 Porta: {os.getenv('DB_PORT')}")
            print(f"👤 Usuário: {os.getenv('DB_USER')}")
            print(f"🗃️ Banco de dados: {os.getenv('DB_DATABASE')}")
            
            cursor.close()

    except ValueError as e:
        print(e)
    except Error as e:
        print(f"❌ Erro ao conectar: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("🔒 Conexão encerrada com segurança.")

if __name__ == "__main__":
    main()