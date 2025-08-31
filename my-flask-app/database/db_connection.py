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
        # Cria a conexão
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'APS'),
            password=os.getenv('DB_PASSWORD', '0511'),
            database=os.getenv('DB_DATABASE', 'saneamento')
        )

        if connection.is_connected():
            print("✅ Conexão estabelecida com sucesso!")

    except Error as e:
        print(f"❌ Erro ao conectar: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("🔒 Conexão encerrada com segurança.")

if __name__ == "__main__":
    main()
