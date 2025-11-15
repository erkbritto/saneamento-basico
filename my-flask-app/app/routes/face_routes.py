"""
Rotas para o sistema de reconhecimento facial simplificado
"""
from flask import Blueprint, request, jsonify, session, render_template, url_for
import os
import cv2
import numpy as np
from datetime import datetime
from werkzeug.utils import secure_filename
import base64

from ..controllers.face_recognition_controller import register_face, verify_face, process_frame

face_bp = Blueprint('face', __name__, template_folder='../../templates')

# Configurações
def create_upload_folder():
    """Cria a pasta de uploads se não existir"""
    upload_folder = os.path.join('app', 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

UPLOAD_FOLDER = create_upload_folder()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@face_bp.route('/api/face/register', methods=['POST'])
def register_face_route():
    """Rota para registrar um novo rosto"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
    
    if file and allowed_file(file.filename):
        # Lê a imagem diretamente do arquivo
        file_data = file.read()
        nparr = np.frombuffer(file_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'success': False, 'message': 'Erro ao processar a imagem'}), 400
        
        # Registra o rosto
        success, message = register_face(
            image=image,
            user_id=session['user_id'],
            user_name=session.get('user_name', 'Usuário')
        )
        
        return jsonify({'success': success, 'message': message})
    
    return jsonify({'success': False, 'message': 'Tipo de arquivo não permitido'}), 400

@face_bp.route('/api/face/verify', methods=['POST'])
def verify_face_route():
    """Rota para verificar um rosto em tempo real"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    if 'image' not in request.json:
        return jsonify({'success': False, 'message': 'Nenhuma imagem fornecida'}), 400
    
    try:
        # Decodifica a imagem base64
        img_data = request.json['image'].split(',')[1]  # Remove o cabeçalho 'data:image/...;base64,'
        img_bytes = base64.b64decode(img_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'success': False, 'message': 'Erro ao processar a imagem'}), 400
        
        # Processa o frame para detecção de rostos
        processed_frame = process_frame(frame)
        
        # Converte o frame processado para base64 para retornar
        _, buffer = cv2.imencode('.jpg', processed_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Verifica o rosto
        success, message = verify_face(frame, session['user_id'])
        
        return jsonify({
            'success': success,
            'message': message,
            'authenticated': success,
            'processed_image': f'data:image/jpeg;base64,{frame_base64}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao processar a imagem: {str(e)}'
        }), 500

@face_bp.route('/api/face/check', methods=['GET'])
def check_face_registered():
    """Verifica se o usuário atual tem um rosto registrado"""
    if 'user_id' not in session:
        return jsonify({'has_face': False, 'message': 'Usuário não autenticado'}), 401
    
    # Verifica se o usuário tem um rosto registrado
    # Esta é uma verificação simplificada - você deve implementar a lógica real
    has_face = os.path.exists(os.path.join(
        UPLOAD_FOLDER,
        f"{session['user_id']}_face.jpg"
    ))
    
    return jsonify({
        'has_face': has_face,
        'message': 'Rosto encontrado' if has_face else 'Nenhum rosto registrado'
    })

# Rotas para teste (remova em produção)
@face_bp.route('/face/register', methods=['GET'])
def register_face_page():
    """Página de teste para registro facial"""
    if 'user_id' not in session:
        return 'Acesso não autorizado', 401
    
    # Renderiza o template de registro facial
    return render_template('face_register.html', 
                         user_id=session['user_id'],
                         user_name=session.get('user_name', 'Usuário'))
