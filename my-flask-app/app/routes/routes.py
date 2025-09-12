from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import time

main = Blueprint('main', __name__)

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

@main.route('/meio-ambiente')
def meio_ambiente():
    if 'user' not in session:
        return redirect(url_for('main.login'))
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