"""
Script para iniciar ambos os sistemas simultaneamente com autenticação:
- Sistema de Login (porta 5002)
- Sistema Financeiro (porta 5000)
- Sistema de Estoque (porta 5001)
"""

import subprocess
import sys
import os
import time
import webbrowser
import json
import hashlib
from flask import Flask, render_template_string, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'chave-super-secreta-mudar-em-producao-12345'

# Variáveis globais para os processos
financeiro_process = None
estoque_process = None
sistemas_iniciados = False

# Diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Arquivo de credenciais criptografadas
CREDENTIALS_FILE = os.path.join(current_dir, 'credentials.enc')

def hash_password(password):
    """Criptografa a senha usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def inicializar_credenciais():
    """Cria credenciais padrão se não existirem"""
    if not os.path.exists(CREDENTIALS_FILE):
        credenciais = {
            'username': 'admin',
            'password': hash_password('admin')
        }
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credenciais, f)
        print("✅ Credenciais padrão criadas: admin/admin")
        print("⚠️  IMPORTANTE: Altere a senha no primeiro acesso!")

def carregar_credenciais():
    """Carrega as credenciais do arquivo criptografado"""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return None

def salvar_credenciais(username, password):
    """Salva as credenciais criptografadas"""
    credenciais = {
        'username': username,
        'password': hash_password(password)
    }
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credenciais, f)

def verificar_credenciais(username, password):
    """Verifica se as credenciais estão corretas"""
    credenciais = carregar_credenciais()
    if credenciais:
        return (credenciais['username'] == username and 
                credenciais['password'] == hash_password(password))
    return False

def iniciar_sistemas():
    """Inicia os sistemas financeiro e de estoque"""
    global financeiro_process, estoque_process, sistemas_iniciados
    
    if not sistemas_iniciados:
        print("\n💰 Iniciando Sistema Financeiro na porta 5000...")
        financeiro_process = subprocess.Popen(
            [sys.executable, os.path.join(current_dir, "financeiro.py")],
            cwd=current_dir
        )
        
        time.sleep(2)
        
        print("📦 Iniciando Sistema de Estoque na porta 5001...")
        estoque_process = subprocess.Popen(
            [sys.executable, os.path.join(current_dir, "estoque.py")],
            cwd=current_dir
        )
        
        sistemas_iniciados = True
        print("\n✅ Sistemas iniciados com sucesso!")

# Template HTML para a página de login
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Sistema Integrado</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 400px;
            max-width: 90%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .alert-error {
            background-color: #fee;
            color: #c33;
            border: 1px solid #fcc;
        }
        .alert-success {
            background-color: #efe;
            color: #3c3;
            border: 1px solid #cfc;
        }
        .alert-warning {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .icon {
            text-align: center;
            margin-bottom: 20px;
            font-size: 60px;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="icon">🔐</div>
        <h1>Sistema Integrado</h1>
        <p class="subtitle">Financeiro & Estoque</p>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="form-group">
                <label for="username">Usuário</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Senha</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Entrar</button>
        </form>
        
        <div class="footer">
            <p>Credenciais padrão: admin/admin</p>
            <p>Copyright © Delean Mafra - 2025</p>
        </div>
    </div>
</body>
</html>
'''

# Template para página inicial após login
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Sistema Integrado</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 20px 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
        }
        .user-info {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        .card-icon {
            font-size: 60px;
            margin-bottom: 15px;
        }
        .card h2 {
            color: #333;
            margin-bottom: 10px;
        }
        .card p {
            color: #666;
            margin-bottom: 20px;
        }
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .alert-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-warning {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Dashboard</h1>
            <div class="user-info">
                <span>👤 {{ username }}</span>
                <a href="{{ url_for('alterar_senha') }}" class="btn btn-secondary">Alterar Senha</a>
                <a href="{{ url_for('logout') }}" class="btn btn-danger">Sair</a>
            </div>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="cards">
            <div class="card">
                <div class="card-icon">💰</div>
                <h2>Sistema Financeiro</h2>
                <p>Gestão completa de receitas e despesas</p>
                <a href="http://127.0.0.1:5000" target="_blank" class="btn btn-primary">Acessar Sistema</a>
            </div>
            
            <div class="card">
                <div class="card-icon">📦</div>
                <h2>Sistema de Estoque</h2>
                <p>Controle de produtos, compras e vendas</p>
                <a href="http://127.0.0.1:5001" target="_blank" class="btn btn-primary">Acessar Sistema</a>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Template para alterar senha
CHANGE_PASSWORD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alterar Senha</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 450px;
            max-width: 90%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            padding: 14px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
            margin-top: 10px;
            width: 100%;
            text-align: center;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .alert-error {
            background-color: #fee;
            color: #c33;
            border: 1px solid #fcc;
        }
        .alert-success {
            background-color: #efe;
            color: #3c3;
            border: 1px solid #cfc;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔑 Alterar Senha</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="form-group">
                <label for="current_password">Senha Atual</label>
                <input type="password" id="current_password" name="current_password" required>
            </div>
            <div class="form-group">
                <label for="new_password">Nova Senha</label>
                <input type="password" id="new_password" name="new_password" required>
            </div>
            <div class="form-group">
                <label for="confirm_password">Confirmar Nova Senha</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            <button type="submit" class="btn btn-primary">Alterar Senha</button>
            <a href="{{ url_for('dashboard') }}" class="btn btn-secondary">Cancelar</a>
        </form>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verificar_credenciais(username, password):
            session['logged_in'] = True
            session['username'] = username
            iniciar_sistemas()
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    # Verificar se é primeira execução
    if not os.path.exists(CREDENTIALS_FILE):
        flash('Primeira execução! Use: admin/admin', 'warning')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_TEMPLATE, username=session.get('username'))

@app.route('/alterar-senha', methods=['GET', 'POST'])
def alterar_senha():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verificar senha atual
        if not verificar_credenciais(session.get('username'), current_password):
            flash('Senha atual incorreta!', 'error')
            return render_template_string(CHANGE_PASSWORD_TEMPLATE)
        
        # Verificar se as senhas novas coincidem
        if new_password != confirm_password:
            flash('As senhas não coincidem!', 'error')
            return render_template_string(CHANGE_PASSWORD_TEMPLATE)
        
        # Verificar tamanho mínimo
        if len(new_password) < 4:
            flash('A senha deve ter no mínimo 4 caracteres!', 'error')
            return render_template_string(CHANGE_PASSWORD_TEMPLATE)
        
        # Salvar nova senha
        salvar_credenciais(session.get('username'), new_password)
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template_string(CHANGE_PASSWORD_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

def main():
    print("=" * 50)
    print("🔐 Sistema de Autenticação Iniciado")
    print("=" * 50)
    
    # Inicializar credenciais padrão
    inicializar_credenciais()
    
    print("\n📍 Acesse: http://127.0.0.1:5002")
    print("⚠️  Pressione Ctrl+C para encerrar todos os sistemas.")
    print("=" * 50)
    
    # Abre o navegador na página de login
    time.sleep(1)
    try:
        webbrowser.open("http://127.0.0.1:5002")
    except:
        pass
    
    try:
        # Inicia o servidor Flask
        app.run(host='127.0.0.1', port=5002, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando os sistemas...")
        if financeiro_process:
            financeiro_process.terminate()
        if estoque_process:
            estoque_process.terminate()
        print("✅ Sistemas encerrados.")

if __name__ == "__main__":
    main()
