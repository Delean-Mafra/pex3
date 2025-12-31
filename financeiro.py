from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
DB_FILE = 'database.json'

# Inicialização do Banco de Dados JSON
def init_db():
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

def load_db():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def filtrar_por_data(transacoes, data_inicio, data_fim):
    if not data_inicio and not data_fim:
        return transacoes
    
    filtradas = []
    for t in transacoes:
        data_t = t['data_gasto'] # Formato YYYY-MM-DD
        if data_inicio and data_t < data_inicio:
            continue
        if data_fim and data_t > data_fim:
            continue
        filtradas.append(t)
    return filtradas

@app.route('/')
def index():
    db = load_db()
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    transacoes = filtrar_por_data(db['transactions'], data_inicio, data_fim)
    
    receitas = sum(t['valor'] for t in transacoes if t['tipo'] == 'receber')
    despesas = sum(t['valor'] for t in transacoes if t['tipo'] == 'pagar')
    
    return render_template('index.html', receitas=receitas, despesas=despesas, 
                           saldo=receitas-despesas, data_inicio=data_inicio, data_fim=data_fim)

@app.route('/lancamentos')
def lancamentos():
    db = load_db()
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    transacoes = filtrar_por_data(db['transactions'], data_inicio, data_fim)
    # Ordenar por data decrescente
    transacoes.sort(key=lambda x: x['data_gasto'], reverse=True)
    
    return render_template('lancamentos.html', transactions=transacoes, 
                           data_inicio=data_inicio, data_fim=data_fim)

@app.route('/cadastrar/<tipo>', methods=['GET', 'POST'])
def cadastrar(tipo):
    db = load_db()
    if request.method == 'POST':
        nova_transacao = {
            "id": len(db['transactions']) + 1,
            "tipo": tipo,
            "data_gasto": request.form['data_gasto'],
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "valor": float(request.form['valor']),
            "categoria": request.form['categoria'],
            "forma_pagamento": request.form.get('forma_pagamento', 'N/A'),
            "descricao": request.form['descricao']
        }
        db['transactions'].append(nova_transacao)
        save_db(db)
        return redirect(url_for('lancamentos'))
    
    if tipo == 'receber':
        categorias = [c['nome'] for c in db['categories'] if c['tipo'] in ['receita', 'ambos']]
    else:
        categorias = [c['nome'] for c in db['categories'] if c['tipo'] in ['despesa', 'ambos']]
        
    return render_template('form_lancamento.html', tipo=tipo, categorias=categorias, metodos=db['payment_methods'])

@app.route('/categorias', methods=['GET', 'POST'])
def categorias():
    db = load_db()
    if request.method == 'POST':
        db['categories'].append({"nome": request.form['nome'], "tipo": request.form['tipo']})
        save_db(db)
        return redirect(url_for('categorias'))
    return render_template('categorias.html', categorias=db['categories'])

@app.route('/analytics')
def analytics():
    db = load_db()
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    transactions = filtrar_por_data(db['transactions'], data_inicio, data_fim)
    transactions.sort(key=lambda x: x['data_gasto'])

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
    dados_mensais_cat = {cat: [mensal_categoria[mes][cat] for mes in meses_ordenados] for cat in todas_categorias_gastos}

    return render_template('analytics.html', 
        cat_labels=list(gastos_por_categoria.keys()), cat_values=list(gastos_por_categoria.values()),
        pag_labels=list(pagamentos_receita_data.keys()), pag_values=list(pagamentos_receita_data.values()),
        meses_labels=meses_ordenados, 
        mensal_receitas=[mensal_rec_desp[m]["receita"] for m in meses_ordenados],
        mensal_despesas=[mensal_rec_desp[m]["despesa"] for m in meses_ordenados],
        evolucao_datas=evolucao_datas, evolucao_saldo=evolucao_saldo,
        dados_mensais_cat=dados_mensais_cat, categorias_lista=todas_categorias_gastos,
        data_inicio=data_inicio, data_fim=data_fim)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)