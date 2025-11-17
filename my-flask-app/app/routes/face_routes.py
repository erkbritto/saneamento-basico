"""
Rotas para reconhecimento facial avançado com anti-spoofing
"""
from flask import Blueprint, request, jsonify, session, current_app
import cv2
import numpy as np
import base64
import os
from datetime import datetime

from ..controllers.face_recognition_controller import face_controller
from ..models.models import Usuario, get_db

face_bp = Blueprint('face', __name__, url_prefix='/face')

@face_bp.route('/register', methods=['POST'])
def register_face():
    """Registra o rosto de um usuário com validação avançada"""
    try:
        # Verifica se o usuário está logado
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        
        # Verifica se o arquivo foi enviado
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhuma imagem enviada'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verifica se é um arquivo de imagem válido
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Formato de arquivo inválido. Use PNG, JPG ou JPEG.'}), 400
        
        # Lê os dados da imagem
        image_data = file.read()
        
        # Processa o registro usando o controlador avançado
        result = face_controller.register_face_enhanced(user_id, image_data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"Erro no registro facial: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@face_bp.route('/authenticate', methods=['POST'])
def authenticate_face():
    """Autentica um usuário usando reconhecimento facial em tempo real"""
    try:
        # Verifica se a imagem foi enviada
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhuma imagem enviada'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verifica se é um arquivo de imagem válido
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Formato de arquivo inválido. Use PNG, JPG ou JPEG.'}), 400
        
        # Lê os dados da imagem
        image_data = file.read()
        
        # Decodifica a imagem
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'success': False, 'message': 'Imagem inválida ou corrompida'}), 400
        
        # Processa a autenticação usando o controlador avançado
        result = face_controller.authenticate_face_real_time(image)
        
        if result['success']:
            # Autenticação bem-sucedida - cria sessão
            user = result['user']
            session['user_id'] = user['id']
            session['user_name'] = user['nome']
            session['user_email'] = user['email']
            session['login_method'] = 'face'
            session['login_time'] = datetime.now().isoformat()
            
            # Log da autenticação
            current_app.logger.info(f"Login facial bem-sucedido: {user['nome']} (ID: {user['id']})")
            
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'user': {
                    'id': user['id'],
                    'nome': user['nome'],
                    'email': user['email'],
                    'cargo': user['cargo'],
                    'departamento': user['departamento']
                },
                'confidence': result['confidence'],
                'details': result.get('details', {})
            }), 200
        else:
            # Falha na autenticação
            return jsonify({
                'success': False,
                'message': result['message'],
                'stage': result.get('stage', 'unknown'),
                'liveness_score': result.get('liveness_score', 0),
                'reasons': result.get('reasons', [])
            }), 401
            
    except Exception as e:
        current_app.logger.error(f"Erro na autenticação facial: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@face_bp.route('/verify', methods=['POST'])
def verify_face():
    """Verifica se uma imagem contém um rosto válido (para testes)"""
    try:
        # Verifica se a imagem foi enviada
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhuma imagem enviada'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verifica se é um arquivo de imagem válido
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Formato de arquivo inválido. Use PNG, JPG ou JPEG.'}), 400
        
        # Lê os dados da imagem
        image_data = file.read()
        
        # Decodifica a imagem
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'success': False, 'message': 'Imagem inválida ou corrompida'}), 400
        
        # Detecta rostos
        faces = face_controller.detect_faces_advanced(image)
        
        if len(faces) == 0:
            return jsonify({
                'success': False,
                'message': 'Nenhum rosto detectado na imagem',
                'faces_detected': 0
            }), 400
        
        # Verifica o primeiro rosto encontrado
        face_rect = faces[0]
        liveness_result = face_controller.verify_liveness_advanced(image, face_rect)
        
        return jsonify({
            'success': True,
            'message': 'Rosto detectado com sucesso',
            'faces_detected': len(faces),
            'face_rect': [int(x) for x in face_rect],
            'liveness_check': {
                'valid': bool(liveness_result['valid']),
                'score': int(liveness_result.get('score', 0)),
                'percentage': int(liveness_result.get('percentage', 0))
            },
            'is_real_face': bool(liveness_result['valid'])
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"Erro na verificação facial: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@face_bp.route('/status', methods=['GET'])
def get_face_status():
    """Verifica o status do reconhecimento facial do usuário logado"""
    try:
        # Verifica se o usuário está logado
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        
        # Verifica se o usuário tem rosto cadastrado
        conn = get_db()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão com banco'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nome, email, rosto FROM usuario WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        has_face = bool(user['rosto'] and user['rosto'] != '')
        
        return jsonify({
            'success': True,
            'has_face_registered': has_face,
            'user': {
                'id': user['id'],
                'nome': user['nome'],
                'email': user['email']
            }
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar status facial: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@face_bp.route('/remove', methods=['DELETE'])
def remove_face():
    """Remove o cadastro facial do usuário logado"""
    try:
        # Verifica se o usuário está logado
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        
        # Remove o rosto do banco
        conn = get_db()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão com banco'}), 500
        
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET rosto = NULL WHERE id = %s",
            (user_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # Limpa o cache do controlador
        face_controller.cache_timestamp = None
        face_controller.known_faces_cache = {}
        
        current_app.logger.info(f"Rosto removido pelo usuário ID: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Cadastro facial removido com sucesso'
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"Erro ao remover cadastro facial: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@face_bp.route('/stats', methods=['GET'])
def get_face_stats():
    """Estatísticas do sistema de reconhecimento facial (admin)"""
    try:
        # Verifica se é administrador
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        
        # Verifica se é admin (simplificado - verificar cargo real)
        conn = get_db()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão com banco'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT cargo FROM usuario WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user or user['cargo'] != 'Administrador':
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Busca estatísticas
        cursor.execute("""
            SELECT 
                COUNT(*) as total_usuarios,
                COUNT(CASE WHEN rosto IS NOT NULL AND rosto != '' THEN 1 END) as usuarios_com_rosto,
                COUNT(CASE WHEN status = 'ATIVO' THEN 1 END) as usuarios_ativos
            FROM usuario
        """)
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Carrega faces conhecidas para obter informações atualizadas
        faces_data = face_controller.load_known_faces()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_usuarios': stats['total_usuarios'],
                'usuarios_com_rosto': stats['usuarios_com_rosto'],
                'usuarios_ativos': stats['usuarios_ativos'],
                'faces_carregadas': faces_data.get('count', 0),
                'taxa_adocao': (stats['usuarios_com_rosto'] / stats['total_usuarios'] * 100) if stats['total_usuarios'] > 0 else 0
            }
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
