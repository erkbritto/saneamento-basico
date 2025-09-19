
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import time

from app.models.models import criar_usuario, Usuario, atualizar_usuario, deletar_usuario


main = Blueprint('main', __name__)


# Rota para criar conta (GET exibe formulário, POST processa cadastro)
@main.route('/criarconta', methods=['GET', 'POST'])
def criarconta():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        departamento = request.form.get('departamento')
        rosto = request.form.get('rosto')
        cargo = 'FUNCIONARIO'
        if not all([nome, email, senha, departamento]):
            flash('Preencha todos os campos obrigatórios', 'error')
            return render_template('criarconta.html')
        try:
            from app.models.models import criar_usuario
            criar_usuario(nome, email, senha, cargo, departamento, rosto)
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash(f'Erro ao criar conta: {str(e)}', 'error')
            return render_template('criarconta.html')
    return render_template('criarconta.html')

@main.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    return redirect(url_for('main.dashboard'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Autenticação fictícia
        users = {
            'admin@gmail.com': {'password': 'admin123', 'role': 'GOVERNANTE', 'name': 'Administrador'},
            'supervisor@gmail.com': {'password': 'super123', 'role': 'SUPERVISOR', 'name': 'Supervisor'},
            'funcionario@gmail.com': {'password': 'func123', 'role': 'FUNCIONARIO', 'name': 'Funcionário'}
        }
        
        if email in users and users[email]['password'] == password:
            session['user'] = users[email]['name']
            session['user_role'] = users[email]['role']
            session['user_email'] = email
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Credenciais inválidas. Tente: admin@gmail.com/admin123, supervisor@gmail.com/super123 ou funcionario@gmail.com/func123', 'error')
    
    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Faça login para acessar o dashboard', 'error')
        return redirect(url_for('main.login'))
    return render_template('index.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema', 'success')
    return redirect(url_for('main.login'))

@main.route('/api/dashboard-data')
def dashboard_data():
    if 'user' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    # Dados base para todos os usuários
    data = {
        'activeUsers': 42,
        'efficiency': 87,
        'timestamp': time.time()
    }
    
    # Dados adicionais para GOVERNANTE e SUPERVISOR
    if session.get('user_role') in ['GOVERNANTE', 'SUPERVISOR']:
        data.update({
            'environmentImpact': 76,
            'criticalAlerts': 3
        })
    
    # Dados específicos para GOVERNANTE
    if session.get('user_role') == 'GOVERNANTE':
        data.update({
            'airQuality': 85,
            'waterQuality': 92,
            'wasteManagement': 78,
            'greenCoverage': 65
        })
    
    return jsonify(data)

@main.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': time.time()})

# Rotas protegidas por papel
@main.route('/ponto-eletronico')
def ponto_eletronico():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    if session.get('user_role') not in ['SUPERVISOR', 'FUNCIONARIO']:
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('ponto_eletronico.html')

@main.route('/tarefas')
def tarefas():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    if session.get('user_role') not in ['SUPERVISOR', 'FUNCIONARIO']:
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('tarefas.html')

@main.route('/relatorios')
def relatorios():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    if session.get('user_role') not in ['GOVERNANTE', 'SUPERVISOR']:
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('relatorios.html')

@main.route('/analises')
def analises():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    if session.get('user_role') not in ['GOVERNANTE', 'SUPERVISOR']:
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('analises.html')

@main.route('/usuarios')
def usuarios():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    if session.get('user_role') != 'GOVERNANTE':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('usuarios.html')

# Rota para cadastrar usuário
@main.route('/usuarios/cadastrar', methods=['POST'])
def cadastrar_usuario_ajax():
    if 'user' not in session or session.get('user_role') != 'GOVERNANTE':
        return jsonify({'success': False, 'message': 'Acesso não autorizado'}), 403
    data = request.get_json(force=True)
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    cargo = data.get('cargo')
    departamento = data.get('departamento')
    status = data.get('status')
    # Validação dos campos obrigatórios
    if not nome or not email or not senha or not cargo or not departamento or not status:
        return jsonify({'success': False, 'message': 'Preencha todos os campos obrigatórios.'}), 400
    if cargo not in ['FUNCIONARIO', 'SUPERVISOR', 'MASTER']:
        return jsonify({'success': False, 'message': 'Cargo inválido.'}), 400
    if status not in ['ATIVO', 'INATIVO', 'PENDENTE']:
        return jsonify({'success': False, 'message': 'Status inválido.'}), 400
    # Validação simples de email
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'message': 'Email inválido.'}), 400
    if len(senha) < 6:
        return jsonify({'success': False, 'message': 'A senha deve ter pelo menos 6 caracteres.'}), 400
    try:
        criar_usuario(nome, email, senha, cargo, departamento)
        return jsonify({'success': True, 'message': 'Usuário cadastrado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao cadastrar usuário: {str(e)}'}), 500

@main.route('/meio-ambiente')
def meio_ambiente():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    
# Rota para listar usuários (JSON)
@main.route('/usuarios/listar', methods=['GET'])
def listar_usuarios():
    try:
        conn = Usuario.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, cargo, departamento FROM usuario")
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'usuarios': usuarios})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para editar usuário
@main.route('/usuarios/editar/<int:id>', methods=['POST'])
def editar_usuario(id):
    data = request.get_json()
    try:
        atualizar_usuario(id, **data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# Rota para excluir usuário
@main.route('/usuarios/excluir/<int:id>', methods=['POST'])
def excluir_usuario(id):
    try:
        deletar_usuario(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    if session.get('user_role') != 'GOVERNANTE':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('meio_ambiente.html')

@main.route('/auditoria')
def auditoria():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    if session.get('user_role') != 'GOVERNANTE':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('auditoria.html')