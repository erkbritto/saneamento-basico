from flask import Flask, send_from_directory
from app.routes.routes import main
from app.routes.face_routes import face_bp
import os

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = 'sua-chave-secreta-aqui'  # Necessário para sessões e flash

# Configurações de upload
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Registra os blueprints
app.register_blueprint(main)
app.register_blueprint(face_bp, url_prefix='/face')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Cria a pasta de uploads se não existir
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Inicia o servidor
    app.run(host='0.0.0.0', port=5000, debug=True)