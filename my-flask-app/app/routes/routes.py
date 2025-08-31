from flask import Blueprint, render_template, request, redirect, url_for, flash, session

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Redireciona para login se não estiver autenticado
    if 'user' not in session:
        return redirect(url_for('main.login'))
    return redirect(url_for('main.index'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Autenticação fictícia
        if email == 'admin@gmail.com' and password == 'admin123':
            session['user'] = email  # Marca usuário como logado
            return redirect(url_for('main.index'))
        else:
            flash('Credenciais inválidas. Use: admin@gmail.com / admin123', 'error')
    return render_template('login.html')

@main.route('/dashboard')
def index():
    # Protege a rota do dashboard
    if 'user' not in session:
        flash('Faça login para acessar o dashboard', 'error')
        return redirect(url_for('main.login'))
    return render_template('index.html')

@main.route('/logout')
def logout():
    session.pop('user', None)
    flash('Você saiu do sistema', 'success')
    return redirect(url_for('main.login'))