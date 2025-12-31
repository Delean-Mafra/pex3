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

def get_base_dir():
    """Retorna o diretório base correto para PyInstaller ou execução normal"""
    if getattr(sys, 'frozen', False):
        # Executando como executável compilado
        return os.path.dirname(sys.executable)
    else:
        # Executando como script Python
        return os.path.dirname(os.path.abspath(__file__))

def get_resource_dir():
    """Retorna o diretório de recursos (templates) para PyInstaller"""
    if getattr(sys, 'frozen', False):
        # PyInstaller extrai para _MEIPASS
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
RESOURCE_DIR = get_resource_dir()

# Arquivos de dados (sempre no diretório do executável para persistência)
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.enc')
DB_FILE = os.path.join(BASE_DIR, 'database.json')
PRODUTOS_CSV = os.path.join(BASE_DIR, 'produtos.csv')
ESTOQUE_DB = os.path.join(BASE_DIR, 'estoque_db.json')

print(f"📁 Diretório base: {BASE_DIR}")
print(f"📁 Diretório recursos: {RESOURCE_DIR}")

# ============================================================================
# APLICAÇÃO DE LOGIN (PORTA 5002)
# ============================================================================

app_login = Flask(__name__, template_folder=os.path.join(RESOURCE_DIR, 'templates'))
app_login.secret_key = 'chave-super-secreta-mudar-em-producao-12345'

# Variáveis globais
sistemas_iniciados = False
navegador_aberto = False

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

# Templates HTML embutidos
LOGIN_TEMPLATE = '''
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
            <p>Copyright © Delean Mafra - 2025</p>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
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
                <a href="{{ url_for('alterar_senha') }}" class="btn btn-secondary">Alterar Senha</a>
                <a href="{{ url_for('logout') }}" class="btn btn-danger">Sair</a>
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

CHANGE_PASSWORD_TEMPLATE = '''
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
            <a href="{{ url_for('dashboard') }}" class="btn btn-secondary">Cancelar</a>
        </form>
    </div>
</body>
</html>
'''

@app_login.route('/', methods=['GET', 'POST'])
def login():
    global sistemas_iniciados
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verificar_credenciais(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    if not os.path.exists(CREDENTIALS_FILE):
        flash('Primeira execução! Use: admin/admin', 'warning')
    
    return render_template_string(LOGIN_TEMPLATE)

@app_login.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_TEMPLATE, username=session.get('username'))

@app_login.route('/alterar-senha', methods=['GET', 'POST'])
def alterar_senha():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not verificar_credenciais(session.get('username'), current_password):
            flash('Senha atual incorreta!', 'error')
            return render_template_string(CHANGE_PASSWORD_TEMPLATE)
        
        if new_password != confirm_password:
            flash('As senhas não coincidem!', 'error')
            return render_template_string(CHANGE_PASSWORD_TEMPLATE)
        
        if len(new_password) < 4:
            flash('A senha deve ter no mínimo 4 caracteres!', 'error')
            return render_template_string(CHANGE_PASSWORD_TEMPLATE)
        
        salvar_credenciais(session.get('username'), new_password)
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template_string(CHANGE_PASSWORD_TEMPLATE)

@app_login.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))


# ============================================================================
# APLICAÇÃO FINANCEIRO (PORTA 5000)
# ============================================================================

app_financeiro = Flask(__name__, template_folder=os.path.join(RESOURCE_DIR, 'templates'))

def init_financeiro_db():
    if not os.path.exists(DB_FILE):
        data = {
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
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def load_financeiro_db():
    init_financeiro_db()
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_financeiro_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def filtrar_financeiro_por_data(transacoes, data_inicio, data_fim):
    if not data_inicio and not data_fim:
        return transacoes

    filtradas = []
    for t in transacoes:
        data_t = t.get('data_gasto', '')  # Formato YYYY-MM-DD
        if data_inicio and data_t < data_inicio:
            continue
        if data_fim and data_t > data_fim:
            continue
        filtradas.append(t)
    return filtradas

@app_financeiro.route('/')
def financeiro_index():
    db = load_financeiro_db()
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')

    transacoes = filtrar_financeiro_por_data(db.get('transactions', []), data_inicio, data_fim)
    receitas = sum(t['valor'] for t in transacoes if t.get('tipo') == 'receber')
    despesas = sum(t['valor'] for t in transacoes if t.get('tipo') == 'pagar')

    return render_template(
        'index.html',
        receitas=receitas,
        despesas=despesas,
        saldo=receitas - despesas,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

@app_financeiro.route('/lancamentos')
def financeiro_lancamentos():
    db = load_financeiro_db()
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')

    transacoes = filtrar_financeiro_por_data(db.get('transactions', []), data_inicio, data_fim)
    transacoes.sort(key=lambda x: x.get('data_gasto', ''), reverse=True)

    return render_template(
        'lancamentos.html',
        transactions=transacoes,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

@app_financeiro.route('/cadastrar/<tipo>', methods=['GET', 'POST'])
def financeiro_cadastrar(tipo):
    db = load_financeiro_db()
    if request.method == 'POST':
        nova_transacao = {
            "id": len(db['transactions']) + 1,
            "tipo": tipo,
            "data_gasto": request.form['data_gasto'],
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "valor": float(request.form['valor']),
            "categoria": request.form['categoria'],
            "forma_pagamento": request.form.get('forma_pagamento', 'N/A'),
            "descricao": request.form['descricao'],
        }
        db['transactions'].append(nova_transacao)
        save_financeiro_db(db)
        return redirect(url_for('financeiro_lancamentos'))

    if tipo == 'receber':
        categorias = [c['nome'] for c in db['categories'] if c['tipo'] in ['receita', 'ambos']]
    else:
        categorias = [c['nome'] for c in db['categories'] if c['tipo'] in ['despesa', 'ambos']]

    return render_template(
        'form_lancamento.html',
        tipo=tipo,
        categorias=categorias,
        metodos=db['payment_methods'],
    )

@app_financeiro.route('/categorias', methods=['GET', 'POST'])
def financeiro_categorias():
    db = load_financeiro_db()
    if request.method == 'POST':
        db['categories'].append({"nome": request.form['nome'], "tipo": request.form['tipo']})
        save_financeiro_db(db)
        return redirect(url_for('financeiro_categorias'))
    return render_template('categorias.html', categorias=db['categories'])

@app_financeiro.route('/analytics')
def financeiro_analytics():
    db = load_financeiro_db()
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')

    transactions = filtrar_financeiro_por_data(db.get('transactions', []), data_inicio, data_fim)
    transactions.sort(key=lambda x: x.get('data_gasto', ''))

    gastos_por_categoria = defaultdict(float)
    mensal_rec_desp = defaultdict(lambda: {"receita": 0, "despesa": 0})
    evolucao_datas = []
    evolucao_saldo = []
    saldo_acumulado = 0
    pagamentos_receita_data = defaultdict(float)
    mensal_categoria = defaultdict(lambda: defaultdict(float))

    for t in transactions:
        data_dt = t['data_gasto']
        mes_ano = data_dt[:7]
        valor = t['valor']

        if t['tipo'] == 'receber':
            saldo_acumulado += valor
            mensal_rec_desp[mes_ano]["receita"] += valor
            pagamentos_receita_data[t['forma_pagamento']] += valor
        else:
            saldo_acumulado -= valor
            mensal_rec_desp[mes_ano]["despesa"] += valor
            gastos_por_categoria[t['categoria']] += valor
            mensal_categoria[mes_ano][t['categoria']] += valor

        evolucao_datas.append(data_dt)
        evolucao_saldo.append(saldo_acumulado)

    meses_ordenados = sorted(mensal_rec_desp.keys())
    todas_categorias_gastos = list(gastos_por_categoria.keys())
    dados_mensais_cat = {
        cat: [mensal_categoria[mes][cat] for mes in meses_ordenados]
        for cat in todas_categorias_gastos
    }

    return render_template(
        'analytics.html',
        cat_labels=list(gastos_por_categoria.keys()),
        cat_values=list(gastos_por_categoria.values()),
        pag_labels=list(pagamentos_receita_data.keys()),
        pag_values=list(pagamentos_receita_data.values()),
        meses_labels=meses_ordenados,
        mensal_receitas=[mensal_rec_desp[m]["receita"] for m in meses_ordenados],
        mensal_despesas=[mensal_rec_desp[m]["despesa"] for m in meses_ordenados],
        evolucao_datas=evolucao_datas,
        evolucao_saldo=evolucao_saldo,
        dados_mensais_cat=dados_mensais_cat,
        categorias_lista=todas_categorias_gastos,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


# ============================================================================
# APLICAÇÃO ESTOQUE (PORTA 5001)
# ============================================================================

app_estoque = Flask(__name__, template_folder=os.path.join(RESOURCE_DIR, 'templates'))
app_estoque.secret_key = 'estoque_secret_key_2025'

def init_produtos_csv():
    if not os.path.exists(PRODUTOS_CSV):
        with open(PRODUTOS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['codigo_barras', 'nome', 'saldo', 'preco_venda', 'preco_compra'])
            writer.writerow(['7891234567890', 'Produto Exemplo 1', '10', '25.90', '15.50'])
            writer.writerow(['7891234567891', 'Produto Exemplo 2', '5', '49.90', '30.00'])

def init_estoque_db():
    if not os.path.exists(ESTOQUE_DB):
        data = {"movimentacoes": [], "vendas": [], "compras": []}
        with open(ESTOQUE_DB, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def load_produtos():
    produtos = []
    if os.path.exists(PRODUTOS_CSV):
        with open(PRODUTOS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                row['saldo'] = int(row['saldo'])
                row['preco_venda'] = float(row['preco_venda'])
                row['preco_compra'] = float(row['preco_compra'])
                produtos.append(row)
    return produtos

def save_produtos(produtos):
    with open(PRODUTOS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['codigo_barras', 'nome', 'saldo', 'preco_venda', 'preco_compra'])
        for p in produtos:
            writer.writerow([p['codigo_barras'], p['nome'], p['saldo'], p['preco_venda'], p['preco_compra']])

def load_estoque_db():
    with open(ESTOQUE_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_estoque_db(data):
    with open(ESTOQUE_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app_estoque.route('/')
def estoque_index():
    init_produtos_csv()
    init_estoque_db()
    produtos = load_produtos()
    
    total_produtos = len(produtos)
    valor_total = sum(p['saldo'] * p['preco_venda'] for p in produtos)
    produtos_baixo_estoque = [p for p in produtos if p['saldo'] < 5]
    
    return render_template('estoque/index.html',
                         produtos=produtos,
                         total_produtos=total_produtos,
                         valor_total=valor_total,
                         produtos_baixo_estoque=produtos_baixo_estoque)

@app_estoque.route('/produtos')
def estoque_produtos():
    init_produtos_csv()
    produtos = load_produtos()
    return render_template('estoque/produtos.html', produtos=produtos)

@app_estoque.route('/produtos/adicionar', methods=['GET', 'POST'])
def estoque_adicionar_produto():
    if request.method == 'POST':
        produtos = load_produtos()
        novo_produto = {
            'codigo_barras': request.form['codigo_barras'],
            'nome': request.form['nome'],
            'saldo': int(request.form['saldo']),
            'preco_venda': float(request.form['preco_venda']),
            'preco_compra': float(request.form['preco_compra'])
        }
        produtos.append(novo_produto)
        save_produtos(produtos)
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('estoque_produtos'))
    
    return render_template('estoque/adicionar_produto.html')

@app_estoque.route('/produtos/editar/<codigo>', methods=['GET', 'POST'])
def estoque_editar_produto(codigo):
    produtos = load_produtos()
    produto = next((p for p in produtos if p['codigo_barras'] == codigo), None)
    
    if not produto:
        flash('Produto não encontrado!', 'error')
        return redirect(url_for('estoque_produtos'))
    
    if request.method == 'POST':
        produto['nome'] = request.form['nome']
        produto['saldo'] = int(request.form['saldo'])
        produto['preco_venda'] = float(request.form['preco_venda'])
        produto['preco_compra'] = float(request.form['preco_compra'])
        save_produtos(produtos)
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('estoque_produtos'))
    
    return render_template('estoque/editar_produto.html', produto=produto)

@app_estoque.route('/produtos/excluir/<codigo>')
def estoque_excluir_produto(codigo):
    produtos = load_produtos()
    produtos = [p for p in produtos if p['codigo_barras'] != codigo]
    save_produtos(produtos)
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('estoque_produtos'))

@app_estoque.route('/venda', methods=['GET', 'POST'])
def estoque_venda():
    init_produtos_csv()
    init_estoque_db()
    produtos = load_produtos()
    
    if request.method == 'POST':
        codigo = request.form['codigo_barras']
        quantidade = int(request.form['quantidade'])
        
        produto = next((p for p in produtos if p['codigo_barras'] == codigo), None)
        if produto and produto['saldo'] >= quantidade:
            produto['saldo'] -= quantidade
            save_produtos(produtos)
            
            # Registrar venda
            db = load_estoque_db()
            venda = {
                'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'codigo_barras': codigo,
                'nome': produto['nome'],
                'quantidade': quantidade,
                'preco_unitario': produto['preco_venda'],
                'total': quantidade * produto['preco_venda']
            }
            db['vendas'].append(venda)
            save_estoque_db(db)
            
            flash(f'Venda realizada: {quantidade}x {produto["nome"]}', 'success')
        else:
            flash('Estoque insuficiente ou produto não encontrado!', 'error')
        
        return redirect(url_for('estoque_venda'))
    
    return render_template('estoque/venda.html', produtos=produtos)

@app_estoque.route('/compra', methods=['GET', 'POST'])
def estoque_compra():
    init_produtos_csv()
    init_estoque_db()
    produtos = load_produtos()
    
    if request.method == 'POST':
        codigo = request.form['codigo_barras']
        quantidade = int(request.form['quantidade'])
        
        produto = next((p for p in produtos if p['codigo_barras'] == codigo), None)
        if produto:
            produto['saldo'] += quantidade
            save_produtos(produtos)
            
            # Registrar compra
            db = load_estoque_db()
            compra = {
                'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'codigo_barras': codigo,
                'nome': produto['nome'],
                'quantidade': quantidade,
                'preco_unitario': produto['preco_compra'],
                'total': quantidade * produto['preco_compra']
            }
            db['compras'].append(compra)
            save_estoque_db(db)
            
            flash(f'Compra registrada: {quantidade}x {produto["nome"]}', 'success')
        else:
            flash('Produto não encontrado!', 'error')
        
        return redirect(url_for('estoque_compra'))
    
    return render_template('estoque/compra.html', produtos=produtos)

@app_estoque.route('/relatorios')
def estoque_relatorios():
    init_estoque_db()
    db = load_estoque_db()
    
    total_vendas = sum(v['total'] for v in db.get('vendas', []))
    total_compras = sum(c['total'] for c in db.get('compras', []))
    
    return render_template('estoque/relatorios.html',
                         vendas=db.get('vendas', []),
                         compras=db.get('compras', []),
                         total_vendas=total_vendas,
                         total_compras=total_compras)


# ============================================================================
# FUNÇÕES PARA INICIAR SERVIDORES EM THREADS
# ============================================================================

def run_login_server():
    """Executa o servidor de login na porta 5002"""
    from werkzeug.serving import make_server
    server = make_server('127.0.0.1', 5002, app_login, threaded=True)
    print("🔐 Servidor de Login iniciado na porta 5002")
    server.serve_forever()

def run_financeiro_server():
    """Executa o servidor financeiro na porta 5000"""
    from werkzeug.serving import make_server
    init_financeiro_db()
    server = make_server('127.0.0.1', 5000, app_financeiro, threaded=True)
    print("💰 Servidor Financeiro iniciado na porta 5000")
    server.serve_forever()

def run_estoque_server():
    """Executa o servidor de estoque na porta 5001"""
    from werkzeug.serving import make_server
    # Usa o sistema completo de estoque (estoque.py), compatível com templates/estoque/*
    import estoque as estoque_module
    from jinja2 import ChoiceLoader, FileSystemLoader

    # Persistir dados ao lado do executável e carregar templates do RESOURCE_DIR
    estoque_module.PRODUTOS_CSV = PRODUTOS_CSV
    estoque_module.ESTOQUE_DB = ESTOQUE_DB
    estoque_module.FINANCEIRO_DB = DB_FILE

    templates_root = os.path.join(RESOURCE_DIR, 'templates')
    estoque_module.app.jinja_loader = ChoiceLoader([
        FileSystemLoader(templates_root),
        estoque_module.app.jinja_loader,
    ])

    estoque_module.init_produtos_csv()
    estoque_module.init_estoque_db()
    server = make_server('127.0.0.1', 5001, estoque_module.app, threaded=True)
    print("📦 Servidor de Estoque iniciado na porta 5001")
    server.serve_forever()


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    global navegador_aberto
    
    print("=" * 60)
    print("🚀 SISTEMA INTEGRADO PEX III")
    print("=" * 60)
    print(f"📁 Diretório de dados: {BASE_DIR}")
    print("=" * 60)
    
    # Inicializar credenciais
    inicializar_credenciais()
    
    # Iniciar servidores em threads daemon
    print("\n⏳ Iniciando servidores...")
    
    thread_financeiro = threading.Thread(target=run_financeiro_server, daemon=True)
    thread_estoque = threading.Thread(target=run_estoque_server, daemon=True)
    thread_login = threading.Thread(target=run_login_server, daemon=True)
    
    thread_financeiro.start()
    thread_estoque.start()
    time.sleep(1)  # Aguardar os servidores secundários iniciarem
    thread_login.start()
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS SERVIDORES INICIADOS COM SUCESSO!")
    print("=" * 60)
    print("=" * 60)
    print("⚠️  Pressione Ctrl+C para encerrar todos os sistemas.")
    print("=" * 60)
    
    # Abrir navegador por padrão; para desabilitar defina PEX3_AUTO_OPEN=0
    if os.environ.get('PEX3_AUTO_OPEN', '1') == '1' and not navegador_aberto:
        time.sleep(2)
        try:
            webbrowser.open("http://127.0.0.1:5002")
            navegador_aberto = True
        except Exception as e:
            print(f"⚠️ Não foi possível abrir o navegador: {e}")
    
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
    main()
