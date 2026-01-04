"""
Sistema Integrado PEX III - Versão Compilada
Executa três sistemas Flask em threads separadas:
- Sistema de Login (porta 5002)
- Sistema Financeiro (porta 5000)
- Sistema de Estoque (porta 5001)
Funciona corretamente quando compilado com PyInstaller.
"""

import sys
import os
import time
import webbrowser
import json
import hashlib
import threading
import csv
from datetime import datetime
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, flash, jsonify

# ============================================================================
# CONFIGURAÇÃO DE DIRETÓRIOS PARA PYINSTALLER
# ============================================================================

def pex3_get_base_dir_dm():
    """Retorna o diretório base correto para PyInstaller ou execução normal"""
    if getattr(sys, 'frozen', False):
        # Executando como executável compilado
        return os.path.dirname(sys.executable)
    else:
        # Executando como script Python
        return os.path.dirname(os.path.abspath(__file__))

def pex3_get_resource_dir_dm():
    """Retorna o diretório de recursos (templates) para PyInstaller"""
    if getattr(sys, 'frozen', False):
        # PyInstaller extrai para _MEIPASS
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

pex3_BASE_DIR_dm = pex3_get_base_dir_dm()
pex3_RESOURCE_DIR_dm = pex3_get_resource_dir_dm()

# Arquivos de dados (sempre no diretório do executável para persistência)
pex3_CREDENTIALS_FILE_dm = os.path.join(pex3_BASE_DIR_dm, 'credentials.enc')
pex3_DB_FILE_dm = os.path.join(pex3_BASE_DIR_dm, 'database.json')
pex3_PRODUTOS_CSV_dm = os.path.join(pex3_BASE_DIR_dm, 'produtos.csv')
pex3_ESTOQUE_DB_dm = os.path.join(pex3_BASE_DIR_dm, 'estoque_db.json')

print(f"📁 Diretório base: {pex3_BASE_DIR_dm}")
print(f"📁 Diretório recursos: {pex3_RESOURCE_DIR_dm}")

# ============================================================================
# APLICAÇÃO DE LOGIN (PORTA 5002)
# ============================================================================

pex3_app_login_dm = Flask(__name__, template_folder=os.path.join(pex3_RESOURCE_DIR_dm, 'templates'))
pex3_app_login_dm.secret_key = 'chave-super-secreta-mudar-em-producao-12345'

# Variáveis globais
pex3_sistemas_iniciados_dm = False
pex3_navegador_aberto_dm = False

def pex3_hash_password_dm(pex3_password_dm):
    """Criptografa a senha usando SHA256"""
    return hashlib.sha256(pex3_password_dm.encode()).hexdigest()

def pex3_inicializar_credenciais_dm():
    """Cria credenciais padrão se não existirem"""
    if not os.path.exists(pex3_CREDENTIALS_FILE_dm):
        pex3_credenciais_dm = {
            'username': 'admin',
            'password': pex3_hash_password_dm('admin')
        }
        with open(pex3_CREDENTIALS_FILE_dm, 'w') as f:
            json.dump(pex3_credenciais_dm, f)
        print("✅ Credenciais padrão criadas: admin/admin")
        print("⚠️  IMPORTANTE: Altere a senha no primeiro acesso!")

def pex3_carregar_credenciais_dm():
    """Carrega as credenciais do arquivo criptografado"""
    if os.path.exists(pex3_CREDENTIALS_FILE_dm):
        with open(pex3_CREDENTIALS_FILE_dm, 'r') as f:
            return json.load(f)
    return None

def pex3_salvar_credenciais_dm(pex3_username_dm, pex3_password_dm):
    """Salva as credenciais criptografadas"""
    pex3_credenciais_dm = {
        'username': pex3_username_dm,
        'password': pex3_hash_password_dm(pex3_password_dm)
    }
    with open(pex3_CREDENTIALS_FILE_dm, 'w') as f:
            json.dump(pex3_credenciais_dm, f)

def pex3_verificar_credenciais_dm(pex3_username_dm, pex3_password_dm):
    """Verifica se as credenciais estão corretas"""
    pex3_credenciais_dm = pex3_carregar_credenciais_dm()
    if pex3_credenciais_dm:
        return (pex3_credenciais_dm['username'] == pex3_username_dm and 
                pex3_credenciais_dm['password'] == pex3_hash_password_dm(pex3_password_dm))
    return False

# Templates HTML embutidos
pex3_LOGIN_TEMPLATE_dm = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Sistema Integrado</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex; justify-content: center; align-items: center; min-height: 100vh;
        }
        .login-container {
            background: white; padding: 40px; border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); width: 400px; max-width: 90%;
        }
        h1 { text-align: center; color: #333; margin-bottom: 10px; font-size: 28px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: 500; }
        input {
            width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px;
            font-size: 16px; transition: border-color 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; }
        button {
            width: 100%; padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600;
            cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }
        .alert { padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
        .alert-error { background-color: #fee; color: #c33; border: 1px solid #fcc; }
        .alert-success { background-color: #efe; color: #3c3; border: 1px solid #cfc; }
        .alert-warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .icon { text-align: center; margin-bottom: 20px; font-size: 60px; }
        .footer { text-align: center; margin-top: 20px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="icon">🔐</div>
        <h1>Sistema Integrado</h1>
        <p class="subtitle">Financeiro & Estoque - PEX III</p>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}{% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}{% endif %}
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
            <p>Copyright © Delean Mafra - 2026</p>
        </div>
    </div>
</body>
</html>
'''

pex3_DASHBOARD_TEMPLATE_dm = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Sistema Integrado</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white; padding: 20px 30px; border-radius: 15px; margin-bottom: 30px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { color: #333; }
        .user-info { display: flex; gap: 15px; align-items: center; }
        .btn {
            padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer;
            font-size: 14px; font-weight: 600; text-decoration: none; display: inline-block;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-danger { background: #dc3545; color: white; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card {
            background: white; padding: 30px; border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center;
        }
        .card-icon { font-size: 60px; margin-bottom: 15px; }
        .card h2 { color: #333; margin-bottom: 10px; }
        .card p { color: #666; margin-bottom: 20px; }
        .alert { padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        .alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status { font-size: 12px; color: #28a745; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Dashboard - PEX III</h1>
            <div class="user-info">
                <span>👤 {{ username }}</span>
                <a href="{{ url_for('pex3_alterar_senha_dm') }}" class="btn btn-secondary">Alterar Senha</a>
                <a href="{{ url_for('pex3_logout_dm') }}" class="btn btn-danger">Sair</a>
            </div>
        </div>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}{% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}{% endif %}
        {% endwith %}
        <div class="cards">
            <div class="card">
                <div class="card-icon">💰</div>
                <h2>Sistema Financeiro</h2>
                <p>Gestão completa de receitas e despesas</p>
                <a href="http://127.0.0.1:5000" target="_blank" class="btn btn-primary">Acessar Sistema</a>
                <p class="status">✅ Servidor ativo na porta 5000</p>
            </div>
            <div class="card">
                <div class="card-icon">📦</div>
                <h2>Sistema de Estoque</h2>
                <p>Controle de produtos, compras e vendas</p>
                <a href="http://127.0.0.1:5001" target="_blank" class="btn btn-primary">Acessar Sistema</a>
                <p class="status">✅ Servidor ativo na porta 5001</p>
            </div>
        </div>
    </div>
</body>
</html>
'''

pex3_CHANGE_PASSWORD_TEMPLATE_dm = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alterar Senha</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex; justify-content: center; align-items: center; min-height: 100vh;
        }
        .container {
            background: white; padding: 40px; border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); width: 450px; max-width: 90%;
        }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: 500; }
        input {
            width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px;
            font-size: 16px; transition: border-color 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; }
        .btn {
            padding: 14px 20px; border: none; border-radius: 8px; cursor: pointer;
            font-size: 16px; font-weight: 600; transition: transform 0.2s; text-decoration: none;
            display: inline-block;
        }
        .btn-primary { width: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-secondary { background: #f0f0f0; color: #333; margin-top: 10px; width: 100%; text-align: center; }
        .btn:hover { transform: translateY(-2px); }
        .alert { padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
        .alert-error { background-color: #fee; color: #c33; border: 1px solid #fcc; }
        .alert-success { background-color: #efe; color: #3c3; border: 1px solid #cfc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔑 Alterar Senha</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}{% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}{% endif %}
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
            <a href="{{ url_for('pex3_dashboard_dm') }}" class="btn btn-secondary">Cancelar</a>
        </form>
    </div>
</body>
</html>
'''

@pex3_app_login_dm.route('/', methods=['GET', 'POST'])
def pex3_login_dm():
    global pex3_sistemas_iniciados_dm
    if request.method == 'POST':
        pex3_username_dm = request.form.get('username')
        pex3_password_dm = request.form.get('password')
        
        if pex3_verificar_credenciais_dm(pex3_username_dm, pex3_password_dm):
            session['logged_in'] = True
            session['username'] = pex3_username_dm
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('pex3_dashboard_dm'))
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    if not os.path.exists(pex3_CREDENTIALS_FILE_dm):
        flash('Primeira execução! Use: admin/admin', 'warning')
    
    return render_template_string(pex3_LOGIN_TEMPLATE_dm)

@pex3_app_login_dm.route('/dashboard')
def pex3_dashboard_dm():
    if not session.get('logged_in'):
        return redirect(url_for('pex3_login_dm'))
    return render_template_string(pex3_DASHBOARD_TEMPLATE_dm, username=session.get('username'))

@pex3_app_login_dm.route('/alterar-senha', methods=['GET', 'POST'])
def pex3_alterar_senha_dm():
    if not session.get('logged_in'):
        return redirect(url_for('pex3_login_dm'))
    
    if request.method == 'POST':
        pex3_current_password_dm = request.form.get('current_password')
        pex3_new_password_dm = request.form.get('new_password')
        pex3_confirm_password_dm = request.form.get('confirm_password')
        
        if not pex3_verificar_credenciais_dm(session.get('username'), pex3_current_password_dm):
            flash('Senha atual incorreta!', 'error')
            return render_template_string(pex3_CHANGE_PASSWORD_TEMPLATE_dm)
        
        if pex3_new_password_dm != pex3_confirm_password_dm:
            flash('As senhas não coincidem!', 'error')
            return render_template_string(pex3_CHANGE_PASSWORD_TEMPLATE_dm)
        
        if len(pex3_new_password_dm) < 4:
            flash('A senha deve ter no mínimo 4 caracteres!', 'error')
            return render_template_string(pex3_CHANGE_PASSWORD_TEMPLATE_dm)
        
        pex3_salvar_credenciais_dm(session.get('username'), pex3_new_password_dm)
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('pex3_dashboard_dm'))
    
    return render_template_string(pex3_CHANGE_PASSWORD_TEMPLATE_dm)

@pex3_app_login_dm.route('/logout')
def pex3_logout_dm():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('pex3_login_dm'))


# ============================================================================
# APLICAÇÃO FINANCEIRO (PORTA 5000)
# ============================================================================

pex3_app_financeiro_dm = Flask(__name__, template_folder=os.path.join(pex3_RESOURCE_DIR_dm, 'templates'))

def pex3_init_financeiro_db_dm():
    if not os.path.exists(pex3_DB_FILE_dm):
        pex3_data_dm = {
            "transactions": [],
            "categories": [
                {"nome": "Salário", "tipo": "receita"},
                {"nome": "Venda", "tipo": "receita"},
                {"nome": "Alimentação", "tipo": "despesa"},
                {"nome": "Limpeza", "tipo": "despesa"},
                {"nome": "Aluguel", "tipo": "despesa"},
                {"nome": "Diversos", "tipo": "ambos"}
            ],
            "payment_methods": ["PIX", "Cartão", "Dinheiro", "Boleto", "Outros"]
        }
        with open(pex3_DB_FILE_dm, 'w', encoding='utf-8') as f:
            json.dump(pex3_data_dm, f, indent=4, ensure_ascii=False)

def pex3_load_financeiro_db_dm():
    pex3_init_financeiro_db_dm()
    with open(pex3_DB_FILE_dm, 'r', encoding='utf-8') as f:
        return json.load(f)

def pex3_save_financeiro_db_dm(pex3_data_dm):
    with open(pex3_DB_FILE_dm, 'w', encoding='utf-8') as f:
        json.dump(pex3_data_dm, f, indent=4, ensure_ascii=False)

def pex3_filtrar_financeiro_por_data_dm(pex3_transacoes_dm, pex3_data_inicio_dm, pex3_data_fim_dm):
    if not pex3_data_inicio_dm and not pex3_data_fim_dm:
        return pex3_transacoes_dm

    pex3_filtradas_dm = []
    for pex3_t_dm in pex3_transacoes_dm:
        pex3_data_t_dm = pex3_t_dm.get('data_gasto', '')  # Formato YYYY-MM-DD
        if pex3_data_inicio_dm and pex3_data_t_dm < pex3_data_inicio_dm:
            continue
        if pex3_data_fim_dm and pex3_data_t_dm > pex3_data_fim_dm:
            continue
        pex3_filtradas_dm.append(pex3_t_dm)
    return pex3_filtradas_dm

@pex3_app_financeiro_dm.route('/')
def pex3_financeiro_index_dm():
    pex3_db_dm = pex3_load_financeiro_db_dm()
    pex3_data_inicio_dm = request.args.get('data_inicio', '')
    pex3_data_fim_dm = request.args.get('data_fim', '')

    pex3_transacoes_dm = pex3_filtrar_financeiro_por_data_dm(pex3_db_dm.get('transactions', []), pex3_data_inicio_dm, pex3_data_fim_dm)
    pex3_receitas_dm = sum(pex3_t_dm['valor'] for pex3_t_dm in pex3_transacoes_dm if pex3_t_dm.get('tipo') == 'receber')
    pex3_despesas_dm = sum(pex3_t_dm['valor'] for pex3_t_dm in pex3_transacoes_dm if pex3_t_dm.get('tipo') == 'pagar')

    return render_template(
        'index.html',
        receitas=pex3_receitas_dm,
        despesas=pex3_despesas_dm,
        saldo=pex3_receitas_dm - pex3_despesas_dm,
        data_inicio=pex3_data_inicio_dm,
        data_fim=pex3_data_fim_dm,
    )

@pex3_app_financeiro_dm.route('/lancamentos')
def pex3_financeiro_lancamentos_dm():
    pex3_db_dm = pex3_load_financeiro_db_dm()
    pex3_data_inicio_dm = request.args.get('data_inicio', '')
    pex3_data_fim_dm = request.args.get('data_fim', '')

    pex3_transacoes_dm = pex3_filtrar_financeiro_por_data_dm(pex3_db_dm.get('transactions', []), pex3_data_inicio_dm, pex3_data_fim_dm)
    pex3_transacoes_dm.sort(key=lambda x: x.get('data_gasto', ''), reverse=True)

    return render_template(
        'lancamentos.html',
        transactions=pex3_transacoes_dm,
        data_inicio=pex3_data_inicio_dm,
        data_fim=pex3_data_fim_dm,
    )

@pex3_app_financeiro_dm.route('/cadastrar/<pex3_tipo_dm>', methods=['GET', 'POST'])
def pex3_financeiro_cadastrar_dm(pex3_tipo_dm):
    pex3_db_dm = pex3_load_financeiro_db_dm()
    if request.method == 'POST':
        pex3_nova_transacao_dm = {
            "id": len(pex3_db_dm['transactions']) + 1,
            "tipo": pex3_tipo_dm,
            "data_gasto": request.form['data_gasto'],
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "valor": float(request.form['valor']),
            "categoria": request.form['categoria'],
            "forma_pagamento": request.form.get('forma_pagamento', 'N/A'),
            "descricao": request.form['descricao'],
        }
        pex3_db_dm['transactions'].append(pex3_nova_transacao_dm)
        pex3_save_financeiro_db_dm(pex3_db_dm)
        return redirect(url_for('pex3_financeiro_lancamentos_dm'))

    if pex3_tipo_dm == 'receber':
        pex3_categorias_dm = [c['nome'] for c in pex3_db_dm['categories'] if c['tipo'] in ['receita', 'ambos']]
    else:
        pex3_categorias_dm = [c['nome'] for c in pex3_db_dm['categories'] if c['tipo'] in ['despesa', 'ambos']]

    return render_template(
        'form_lancamento.html',
        tipo=pex3_tipo_dm,
        categorias=pex3_categorias_dm,
        metodos=pex3_db_dm['payment_methods'],
    )

@pex3_app_financeiro_dm.route('/categorias', methods=['GET', 'POST'])
def pex3_financeiro_categorias_dm():
    pex3_db_dm = pex3_load_financeiro_db_dm()
    if request.method == 'POST':
        pex3_db_dm['categories'].append({"nome": request.form['nome'], "tipo": request.form['tipo']})
        pex3_save_financeiro_db_dm(pex3_db_dm)
        return redirect(url_for('pex3_financeiro_categorias_dm'))
    return render_template('categorias.html', categorias=pex3_db_dm['categories'])

@pex3_app_financeiro_dm.route('/analytics')
def pex3_financeiro_analytics_dm():
    pex3_db_dm = pex3_load_financeiro_db_dm()
    pex3_data_inicio_dm = request.args.get('data_inicio', '')
    pex3_data_fim_dm = request.args.get('data_fim', '')

    pex3_transactions_dm = pex3_filtrar_financeiro_por_data_dm(pex3_db_dm.get('transactions', []), pex3_data_inicio_dm, pex3_data_fim_dm)
    pex3_transactions_dm.sort(key=lambda x: x.get('data_gasto', ''))

    pex3_gastos_por_categoria_dm = defaultdict(float)
    pex3_mensal_rec_desp_dm = defaultdict(lambda: {"receita": 0, "despesa": 0})
    pex3_evolucao_datas_dm = []
    pex3_evolucao_saldo_dm = []
    pex3_saldo_acumulado_dm = 0
    pex3_pagamentos_receita_data_dm = defaultdict(float)
    pex3_mensal_categoria_dm = defaultdict(lambda: defaultdict(float))

    for pex3_t_dm in pex3_transactions_dm:
        pex3_data_dt_dm = pex3_t_dm['data_gasto']
        pex3_mes_ano_dm = pex3_data_dt_dm[:7]
        pex3_valor_dm = pex3_t_dm['valor']

        if pex3_t_dm['tipo'] == 'receber':
            pex3_saldo_acumulado_dm += pex3_valor_dm
            pex3_mensal_rec_desp_dm[pex3_mes_ano_dm]["receita"] += pex3_valor_dm
            pex3_pagamentos_receita_data_dm[pex3_t_dm['forma_pagamento']] += pex3_valor_dm
        else:
            pex3_saldo_acumulado_dm -= pex3_valor_dm
            pex3_mensal_rec_desp_dm[pex3_mes_ano_dm]["despesa"] += pex3_valor_dm
            pex3_gastos_por_categoria_dm[pex3_t_dm['categoria']] += pex3_valor_dm
            pex3_mensal_categoria_dm[pex3_mes_ano_dm][pex3_t_dm['categoria']] += pex3_valor_dm

        pex3_evolucao_datas_dm.append(pex3_data_dt_dm)
        pex3_evolucao_saldo_dm.append(pex3_saldo_acumulado_dm)

    pex3_meses_ordenados_dm = sorted(pex3_mensal_rec_desp_dm.keys())
    pex3_todas_categorias_gastos_dm = list(pex3_gastos_por_categoria_dm.keys())
    pex3_dados_mensais_cat_dm = {
        pex3_cat_dm: [pex3_mensal_categoria_dm[pex3_mes_dm][pex3_cat_dm] for pex3_mes_dm in pex3_meses_ordenados_dm]
        for pex3_cat_dm in pex3_todas_categorias_gastos_dm
    }

    return render_template(
        'analytics.html',
        cat_labels=list(pex3_gastos_por_categoria_dm.keys()),
        cat_values=list(pex3_gastos_por_categoria_dm.values()),
        pag_labels=list(pex3_pagamentos_receita_data_dm.keys()),
        pag_values=list(pex3_pagamentos_receita_data_dm.values()),
        meses_labels=pex3_meses_ordenados_dm,
        mensal_receitas=[pex3_mensal_rec_desp_dm[pex3_m_dm]["receita"] for pex3_m_dm in pex3_meses_ordenados_dm],
        mensal_despesas=[pex3_mensal_rec_desp_dm[pex3_m_dm]["despesa"] for pex3_m_dm in pex3_meses_ordenados_dm],
        evolucao_datas=pex3_evolucao_datas_dm,
        evolucao_saldo=pex3_evolucao_saldo_dm,
        dados_mensais_cat=pex3_dados_mensais_cat_dm,
        categorias_lista=pex3_todas_categorias_gastos_dm,
        data_inicio=pex3_data_inicio_dm,
        data_fim=pex3_data_fim_dm,
    )


# ============================================================================
# APLICAÇÃO ESTOQUE (PORTA 5001)
# ============================================================================

pex3_app_estoque_dm = Flask(__name__, template_folder=os.path.join(pex3_RESOURCE_DIR_dm, 'templates'))
pex3_app_estoque_dm.secret_key = 'estoque_secret_key_2025'

def pex3_init_produtos_csv_dm():
    if not os.path.exists(pex3_PRODUTOS_CSV_dm):
        with open(pex3_PRODUTOS_CSV_dm, 'w', newline='', encoding='utf-8') as f:
            pex3_writer_dm = csv.writer(f, delimiter=';')
            pex3_writer_dm.writerow(['codigo_barras', 'nome', 'saldo', 'preco_venda', 'preco_compra'])
            pex3_writer_dm.writerow(['7891234567890', 'Produto Exemplo 1', '10', '25.90', '15.50'])
            pex3_writer_dm.writerow(['7891234567891', 'Produto Exemplo 2', '5', '49.90', '30.00'])

def pex3_init_estoque_db_dm():
    if not os.path.exists(pex3_ESTOQUE_DB_dm):
        pex3_data_dm = {"movimentacoes": [], "vendas": [], "compras": []}
        with open(pex3_ESTOQUE_DB_dm, 'w', encoding='utf-8') as f:
            json.dump(pex3_data_dm, f, indent=4, ensure_ascii=False)

def pex3_load_produtos_dm():
    pex3_produtos_dm = []
    if os.path.exists(pex3_PRODUTOS_CSV_dm):
        with open(pex3_PRODUTOS_CSV_dm, 'r', encoding='utf-8') as f:
            pex3_reader_dm = csv.DictReader(f, delimiter=';')
            for pex3_row_dm in pex3_reader_dm:
                pex3_row_dm['saldo'] = int(pex3_row_dm['saldo'])
                pex3_row_dm['preco_venda'] = float(pex3_row_dm['preco_venda'])
                pex3_row_dm['preco_compra'] = float(pex3_row_dm['preco_compra'])
                pex3_produtos_dm.append(pex3_row_dm)
    return pex3_produtos_dm

def pex3_save_produtos_dm(pex3_produtos_dm):
    with open(pex3_PRODUTOS_CSV_dm, 'w', newline='', encoding='utf-8') as f:
        pex3_writer_dm = csv.writer(f, delimiter=';')
        pex3_writer_dm.writerow(['codigo_barras', 'nome', 'saldo', 'preco_venda', 'preco_compra'])
        for pex3_p_dm in pex3_produtos_dm:
            pex3_writer_dm.writerow([pex3_p_dm['codigo_barras'], pex3_p_dm['nome'], pex3_p_dm['saldo'], pex3_p_dm['preco_venda'], pex3_p_dm['preco_compra']])

def pex3_load_estoque_db_dm():
    with open(pex3_ESTOQUE_DB_dm, 'r', encoding='utf-8') as f:
        return json.load(f)

def pex3_save_estoque_db_dm(pex3_data_dm):
    with open(pex3_ESTOQUE_DB_dm, 'w', encoding='utf-8') as f:
        json.dump(pex3_data_dm, f, indent=4, ensure_ascii=False)

@pex3_app_estoque_dm.route('/')
def pex3_estoque_index_dm():
    pex3_init_produtos_csv_dm()
    pex3_init_estoque_db_dm()
    pex3_produtos_dm = pex3_load_produtos_dm()
    
    pex3_total_produtos_dm = len(pex3_produtos_dm)
    pex3_valor_total_dm = sum(pex3_p_dm['saldo'] * pex3_p_dm['preco_venda'] for pex3_p_dm in pex3_produtos_dm)
    pex3_produtos_baixo_estoque_dm = [pex3_p_dm for pex3_p_dm in pex3_produtos_dm if pex3_p_dm['saldo'] < 5]
    
    return render_template('estoque/index.html',
                         produtos=pex3_produtos_dm,
                         total_produtos=pex3_total_produtos_dm,
                         valor_total=pex3_valor_total_dm,
                         produtos_baixo_estoque=pex3_produtos_baixo_estoque_dm)

@pex3_app_estoque_dm.route('/produtos')
def pex3_estoque_produtos_dm():
    pex3_init_produtos_csv_dm()
    pex3_produtos_dm = pex3_load_produtos_dm()
    return render_template('estoque/produtos.html', produtos=pex3_produtos_dm)

@pex3_app_estoque_dm.route('/produtos/adicionar', methods=['GET', 'POST'])
def pex3_estoque_adicionar_produto_dm():
    if request.method == 'POST':
        pex3_produtos_dm = pex3_load_produtos_dm()
        pex3_novo_produto_dm = {
            'codigo_barras': request.form['codigo_barras'],
            'nome': request.form['nome'],
            'saldo': int(request.form['saldo']),
            'preco_venda': float(request.form['preco_venda']),
            'preco_compra': float(request.form['preco_compra'])
        }
        pex3_produtos_dm.append(pex3_novo_produto_dm)
        pex3_save_produtos_dm(pex3_produtos_dm)
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('pex3_estoque_produtos_dm'))
    
    return render_template('estoque/adicionar_produto.html')

@pex3_app_estoque_dm.route('/produtos/editar/<pex3_codigo_dm>', methods=['GET', 'POST'])
def pex3_estoque_editar_produto_dm(pex3_codigo_dm):
    pex3_produtos_dm = pex3_load_produtos_dm()
    pex3_produto_dm = next((pex3_p_dm for pex3_p_dm in pex3_produtos_dm if pex3_p_dm['codigo_barras'] == pex3_codigo_dm), None)
    
    if not pex3_produto_dm:
        flash('Produto não encontrado!', 'error')
        return redirect(url_for('pex3_estoque_produtos_dm'))
    
    if request.method == 'POST':
        pex3_produto_dm['nome'] = request.form['nome']
        pex3_produto_dm['saldo'] = int(request.form['saldo'])
        pex3_produto_dm['preco_venda'] = float(request.form['preco_venda'])
        pex3_produto_dm['preco_compra'] = float(request.form['preco_compra'])
        pex3_save_produtos_dm(pex3_produtos_dm)
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('pex3_estoque_produtos_dm'))
    
    return render_template('estoque/editar_produto.html', produto=pex3_produto_dm)

@pex3_app_estoque_dm.route('/produtos/excluir/<pex3_codigo_dm>')
def pex3_estoque_excluir_produto_dm(pex3_codigo_dm):
    pex3_produtos_dm = pex3_load_produtos_dm()
    pex3_produtos_dm = [pex3_p_dm for pex3_p_dm in pex3_produtos_dm if pex3_p_dm['codigo_barras'] != pex3_codigo_dm]
    pex3_save_produtos_dm(pex3_produtos_dm)
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('pex3_estoque_produtos_dm'))

@pex3_app_estoque_dm.route('/venda', methods=['GET', 'POST'])
def pex3_estoque_venda_dm():
    pex3_init_produtos_csv_dm()
    pex3_init_estoque_db_dm()
    pex3_produtos_dm = pex3_load_produtos_dm()
    
    if request.method == 'POST':
        pex3_codigo_dm = request.form['codigo_barras']
        pex3_quantidade_dm = int(request.form['quantidade'])
        
        pex3_produto_dm = next((pex3_p_dm for pex3_p_dm in pex3_produtos_dm if pex3_p_dm['codigo_barras'] == pex3_codigo_dm), None)
        if pex3_produto_dm and pex3_produto_dm['saldo'] >= pex3_quantidade_dm:
            pex3_produto_dm['saldo'] -= pex3_quantidade_dm
            pex3_save_produtos_dm(pex3_produtos_dm)
            
            # Registrar venda
            pex3_db_dm = pex3_load_estoque_db_dm()
            pex3_venda_dm = {
                'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'codigo_barras': pex3_codigo_dm,
                'nome': pex3_produto_dm['nome'],
                'quantidade': pex3_quantidade_dm,
                'preco_unitario': pex3_produto_dm['preco_venda'],
                'total': pex3_quantidade_dm * pex3_produto_dm['preco_venda']
            }
            pex3_db_dm['vendas'].append(pex3_venda_dm)
            pex3_save_estoque_db_dm(pex3_db_dm)
            
            flash(f'Venda realizada: {pex3_quantidade_dm}x {pex3_produto_dm["nome"]}', 'success')
        else:
            flash('Estoque insuficiente ou produto não encontrado!', 'error')
        
        return redirect(url_for('pex3_estoque_venda_dm'))
    
    return render_template('estoque/venda.html', produtos=pex3_produtos_dm)

@pex3_app_estoque_dm.route('/compra', methods=['GET', 'POST'])
def pex3_estoque_compra_dm():
    pex3_init_produtos_csv_dm()
    pex3_init_estoque_db_dm()
    pex3_produtos_dm = pex3_load_produtos_dm()
    
    if request.method == 'POST':
        pex3_codigo_dm = request.form['codigo_barras']
        pex3_quantidade_dm = int(request.form['quantidade'])
        
        pex3_produto_dm = next((pex3_p_dm for pex3_p_dm in pex3_produtos_dm if pex3_p_dm['codigo_barras'] == pex3_codigo_dm), None)
        if pex3_produto_dm:
            pex3_produto_dm['saldo'] += pex3_quantidade_dm
            pex3_save_produtos_dm(pex3_produtos_dm)
            
            # Registrar compra
            pex3_db_dm = pex3_load_estoque_db_dm()
            pex3_compra_dm = {
                'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'codigo_barras': pex3_codigo_dm,
                'nome': pex3_produto_dm['nome'],
                'quantidade': pex3_quantidade_dm,
                'preco_unitario': pex3_produto_dm['preco_compra'],
                'total': pex3_quantidade_dm * pex3_produto_dm['preco_compra']
            }
            pex3_db_dm['compras'].append(pex3_compra_dm)
            pex3_save_estoque_db_dm(pex3_db_dm)
            
            flash(f'Compra registrada: {pex3_quantidade_dm}x {pex3_produto_dm["nome"]}', 'success')
        else:
            flash('Produto não encontrado!', 'error')
        
        return redirect(url_for('pex3_estoque_compra_dm'))
    
    return render_template('estoque/compra.html', produtos=pex3_produtos_dm)

@pex3_app_estoque_dm.route('/relatorios')
def pex3_estoque_relatorios_dm():
    pex3_init_estoque_db_dm()
    pex3_db_dm = pex3_load_estoque_db_dm()
    
    pex3_total_vendas_dm = sum(pex3_v_dm['total'] for pex3_v_dm in pex3_db_dm.get('vendas', []))
    pex3_total_compras_dm = sum(pex3_c_dm['total'] for pex3_c_dm in pex3_db_dm.get('compras', []))
    
    return render_template('estoque/relatorios.html',
                         vendas=pex3_db_dm.get('vendas', []),
                         compras=pex3_db_dm.get('compras', []),
                         total_vendas=pex3_total_vendas_dm,
                         total_compras=pex3_total_compras_dm)


# ============================================================================
# FUNÇÕES PARA INICIAR SERVIDORES EM THREADS
# ============================================================================

def pex3_run_login_server_dm():
    """Executa o servidor de login na porta 5002"""
    from werkzeug.serving import make_server
    pex3_server_dm = make_server('127.0.0.1', 5002, pex3_app_login_dm, threaded=True)
    print("🔐 Servidor de Login iniciado na porta 5002")
    pex3_server_dm.serve_forever()

def pex3_run_financeiro_server_dm():
    """Executa o servidor financeiro na porta 5000"""
    from werkzeug.serving import make_server
    pex3_init_financeiro_db_dm()
    pex3_server_dm = make_server('127.0.0.1', 5000, pex3_app_financeiro_dm, threaded=True)
    print("💰 Servidor Financeiro iniciado na porta 5000")
    pex3_server_dm.serve_forever()

def pex3_run_estoque_server_dm():
    """Executa o servidor de estoque na porta 5001"""
    from werkzeug.serving import make_server
    # Usa o sistema completo de estoque (estoque.py), compatível com templates/estoque/*
    import estoque as pex3_estoque_module_dm
    from jinja2 import ChoiceLoader, FileSystemLoader

    # Persistir dados ao lado do executável e carregar templates do RESOURCE_DIR
    pex3_estoque_module_dm.pex3_PRODUTOS_CSV_dm = pex3_PRODUTOS_CSV_dm
    pex3_estoque_module_dm.pex3_ESTOQUE_DB_dm = pex3_ESTOQUE_DB_dm
    pex3_estoque_module_dm.pex3_FINANCEIRO_DB_dm = pex3_DB_FILE_dm

    pex3_templates_root_dm = os.path.join(pex3_RESOURCE_DIR_dm, 'templates')
    pex3_estoque_module_dm.pex3_app_dm.jinja_loader = ChoiceLoader([
        FileSystemLoader(pex3_templates_root_dm),
        pex3_estoque_module_dm.pex3_app_dm.jinja_loader,
    ])

    pex3_estoque_module_dm.pex3_init_produtos_csv_dm()
    pex3_estoque_module_dm.pex3_init_estoque_db_dm()
    pex3_server_dm = make_server('127.0.0.1', 5001, pex3_estoque_module_dm.pex3_app_dm, threaded=True)
    print("📦 Servidor de Estoque iniciado na porta 5001")
    pex3_server_dm.serve_forever()


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def pex3_main_dm():
    global pex3_navegador_aberto_dm
    
    print("=" * 60)
    print("🚀 SISTEMA INTEGRADO PEX III")
    print("=" * 60)
    print(f"📁 Diretório de dados: {pex3_BASE_DIR_dm}")
    print("=" * 60)
    
    # Inicializar credenciais
    pex3_inicializar_credenciais_dm()
    
    # Iniciar servidores em threads daemon
    print("\n⏳ Iniciando servidores...")
    
    pex3_thread_financeiro_dm = threading.Thread(target=pex3_run_financeiro_server_dm, daemon=True)
    pex3_thread_estoque_dm = threading.Thread(target=pex3_run_estoque_server_dm, daemon=True)
    pex3_thread_login_dm = threading.Thread(target=pex3_run_login_server_dm, daemon=True)
    
    pex3_thread_financeiro_dm.start()
    pex3_thread_estoque_dm.start()
    time.sleep(1)  # Aguardar os servidores secundários iniciarem
    pex3_thread_login_dm.start()
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS SERVIDORES INICIADOS COM SUCESSO!")
    print("=" * 60)
    print("=" * 60)
    print("⚠️  Pressione Ctrl+C para encerrar todos os sistemas.")
    print("=" * 60)
    
    # Abrir navegador por padrão; para desabilitar defina PEX3_AUTO_OPEN=0
    if os.environ.get('PEX3_AUTO_OPEN', '1') == '1' and not pex3_navegador_aberto_dm:
        time.sleep(2)
        try:
            webbrowser.open("http://127.0.0.1:5002")
            pex3_navegador_aberto_dm = True
        except Exception as pex3_e_dm:
            print(f"⚠️ Não foi possível abrir o navegador: {pex3_e_dm}")
    
    # Manter o programa rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando sistemas...")
        print("✅ Sistemas encerrados. Até logo!")
        sys.exit(0)


if __name__ == "__main__":
    # Evitar que o multiprocessing do PyInstaller cause problemas
    import multiprocessing
    multiprocessing.freeze_support()
    pex3_main_dm()
