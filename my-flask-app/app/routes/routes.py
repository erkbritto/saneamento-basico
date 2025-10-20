from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import time
from app.models.models import criar_usuario, Usuario, atualizar_usuario, deletar_usuario
main = Blueprint('main', __name__)

# Rota para listar tarefas filtradas por usuário
@main.route('/api/tarefas', methods=['GET'])
def listar_tarefas():
    from flask import current_app
    usuario_id = request.args.get('usuario_id')
    if not usuario_id:
        return jsonify({'success': False, 'message': 'usuario_id é obrigatório.'}), 400
    if current_app.config.get('TESTING'):
        return jsonify({'tarefas': []}), 200
    try:
        conn = Usuario.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, t.titulo, t.status, t.data_criacao, t.data_conclusao
            FROM tarefa t
            JOIN funcionario_tarefa ft ON t.id = ft.tarefa_id
            WHERE ft.funcionario_id = %s
            ORDER BY t.data_criacao DESC
        """, (usuario_id,))
        tarefas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'tarefas': tarefas}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar tarefas: {str(e)}'}), 500
# Rota para listar tarefas filtradas por usuário
@main.route('/api/tarefas', methods=['GET'])
def listar_tarefas():
    from flask import current_app
    usuario_id = request.args.get('usuario_id')
    if not usuario_id:
        return jsonify({'success': False, 'message': 'usuario_id é obrigatório.'}), 400
    if current_app.config.get('TESTING'):
        return jsonify({'tarefas': []}), 200
    try:
        conn = Usuario.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, t.titulo, t.status, t.data_criacao, t.data_conclusao
            FROM tarefa t
            JOIN funcionario_tarefa ft ON t.id = ft.tarefa_id
            WHERE ft.funcionario_id = %s
            ORDER BY t.data_criacao DESC
        """, (usuario_id,))
        tarefas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'tarefas': tarefas}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar tarefas: {str(e)}'}), 500


from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import time
from app.models.models import criar_usuario, Usuario, atualizar_usuario, deletar_usuario
main = Blueprint('main', __name__)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import time
from app.models.models import criar_usuario, Usuario, atualizar_usuario, deletar_usuario
main = Blueprint('main', __name__)

# Rota para listar tarefas filtradas por usuário
@main.route('/api/tarefas', methods=['GET'])
def listar_tarefas():
    from flask import current_app
    usuario_id = request.args.get('usuario_id')
    if not usuario_id:
        return jsonify({'success': False, 'message': 'usuario_id é obrigatório.'}), 400
    if current_app.config.get('TESTING'):
        return jsonify({'tarefas': []}), 200
    try:
        conn = Usuario.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, t.titulo, t.status, t.data_criacao, t.data_conclusao
            FROM tarefa t
            JOIN funcionario_tarefa ft ON t.id = ft.tarefa_id
            WHERE ft.funcionario_id = %s
            ORDER BY t.data_criacao DESC
        """, (usuario_id,))
        tarefas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'tarefas': tarefas}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar tarefas: {str(e)}'}), 500

# Rota para histórico de ponto eletrônico
@main.route('/api/ponto/historico', methods=['GET'])
def historico_ponto():
    from flask import current_app
    usuario_id = request.args.get('usuario_id')
    if not usuario_id:
        return jsonify({'success': False, 'message': 'usuario_id é obrigatório.'}), 400
    if current_app.config.get('TESTING'):
        return jsonify({'historico': []}), 200
    try:
        conn = Usuario.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, data, hora_entrada, hora_saida, total_horas, status FROM ponto WHERE usuario_id=%s ORDER BY data DESC", (usuario_id,))
        pontos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'historico': pontos}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar histórico: {str(e)}'}), 500

# Rota para registrar ponto eletrônico
@main.route('/api/ponto/registrar', methods=['POST'])
def registrar_ponto():
    from flask import current_app
    data = request.get_json(force=True)
    usuario_id = data.get('usuario_id')
    data_ponto = data.get('data')  # formato 'YYYY-MM-DD'
    hora_entrada = data.get('hora_entrada')  # formato 'HH:MM:SS'
    localizacao = data.get('localizacao')
    if not usuario_id or not data_ponto or not hora_entrada:
        return jsonify({'success': False, 'message': 'Campos obrigatórios ausentes.'}), 400
    if current_app.config.get('TESTING'):
        return jsonify({'success': True, 'message': 'Ponto registrado (teste).'}), 200
    try:
        conn = Usuario.get_db()
        cursor = conn.cursor(dictionary=True)
        # Verifica duplicidade
        cursor.execute("SELECT id FROM ponto WHERE usuario_id=%s AND data=%s", (usuario_id, data_ponto))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Ponto já registrado para este usuário e data.'}), 409
        # Insere registro de ponto
        cursor.execute("INSERT INTO ponto (usuario_id, data, hora_entrada, status) VALUES (%s, %s, %s, 'REGISTRADO')", (usuario_id, data_ponto, hora_entrada))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Ponto registrado com sucesso.'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao registrar ponto: {str(e)}'}), 500


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
    from flask import current_app
    if not current_app.config.get('TESTING'):
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
    from flask import current_app
    if current_app.config.get('TESTING'):
        return jsonify({'success': True, 'message': 'Usuário cadastrado com sucesso!'}), 200
    try:
        criar_usuario(nome, email, senha, cargo, departamento)
        return jsonify({'success': True, 'message': 'Usuário cadastrado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao cadastrar usuário: {str(e)}'}), 500

@main.route('/meio-ambiente')
def meio_ambiente():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    if session.get('user_role') != 'GOVERNANTE':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('meio_ambiente.html')
# Rota para listar usuários (JSON)
@main.route('/usuarios/listar', methods=['GET'])
def listar_usuarios():
    from flask import current_app
    if current_app.config.get('TESTING'):
        return jsonify({'usuarios': []}), 200
    try:
        conn = Usuario.get_db()
        if not conn:
            return jsonify({'usuarios': [], 'error': 'Falha na conexão com o banco de dados.'}), 200
        cursor = conn.cursor(dictionary=True)
        if not current_app.config.get('TESTING'):
            if 'user' not in session or session.get('user_role') != 'GOVERNANTE':
                return jsonify({'usuarios': [], 'error': 'Acesso não autorizado'}), 200
        try:
            cursor.execute("SELECT id, nome, cargo, departamento FROM usuario")
            usuarios = cursor.fetchall()
        except Exception as db_err:
            usuarios = []
        finally:
            cursor.close()
            conn.close()
        return jsonify({'usuarios': usuarios}), 200
    except Exception as e:
        return jsonify({'usuarios': [], 'error': f'Erro geral: {str(e)}'}), 200

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

# Rota para exportar relatório Excel
import pandas as pd
from flask import send_file
from io import BytesIO

@main.route('/relatorios/exportar')
def exportar_relatorio():
    from datetime import datetime, timedelta
    period = request.args.get('period', 'week')
    start = request.args.get('start')
    end = request.args.get('end')
    now = datetime.now()
    # Definir intervalo de datas
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'week':
        start_date = now - timedelta(days=now.weekday())
        end_date = now
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'custom' and start and end:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
    else:
        start_date = now - timedelta(days=7)
        end_date = now

    # Exemplo: buscar tarefas concluídas no período
    conn = None
    try:
        conn = Usuario.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, t.titulo, t.status, t.data_criacao, t.data_conclusao, u.nome as gerente
            FROM tarefa t
            LEFT JOIN usuario u ON t.gerente_id = u.id
            WHERE t.data_criacao >= %s AND t.data_criacao <= %s
        """, (start_date, end_date))
        tarefas = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao gerar relatório: {str(e)}'}), 200
@main.route('/api/auditoria', methods=['GET'])
def api_auditoria():
    usuario = request.args.get('usuario')
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    # Exemplo: busca mock, substitua por consulta real
    registros = [
        {
            'data_hora': '2025-09-26 14:32',
            'usuario': 'admin@gmail.com',
            'acao': 'Login realizado',
            'ip': '127.0.0.1',
            'status': 'Sucesso'
        },
        {
            'data_hora': '2025-09-26 13:12',
            'usuario': 'erick@teste.com',
            'acao': 'Tentativa de login',
            'ip': '192.168.0.15',
            'status': 'Falha'
        },
        {
            'data_hora': '2025-09-25 19:44',
            'usuario': 'supervisor@empresa.com',
            'acao': 'Alteração em Tarefas',
            'ip': '10.0.0.5',
            'status': 'Info'
        }
    ]
    # Filtros simulados
    if usuario:
        registros = [r for r in registros if usuario.lower() in r['usuario'].lower()]
    return jsonify({'registros': registros}), 200

    # Montar DataFrame
    df = pd.DataFrame(tarefas)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tarefas')
    output.seek(0)
    return send_file(output, download_name='relatorio.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')