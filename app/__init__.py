#!/usr/bin/env python3
"""
Pacote principal da aplicação Flask
"""

from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    CORS(app)
    
    # Configurações
    app.secret_key = os.getenv('SECRET_KEY', 'sua-chave-secreta-aqui')
    
    # Configurações do banco de dados
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_PORT', '3306')
    os.environ.setdefault('DB_USER', 'root')
    os.environ.setdefault('DB_PASSWORD', '0511')
    os.environ.setdefault('DB_DATABASE', 'saneamento')
    
    # Configurações de upload
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Registro dos blueprints
    from app.routes.routes import main
    from app.routes.face_routes import face_bp
    
    app.register_blueprint(main)
    app.register_blueprint(face_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

# Instância da aplicação para uso direto
app = create_app()
