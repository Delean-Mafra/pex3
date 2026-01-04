from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime
from collections import defaultdict

pex3_app_dm = Flask(__name__)
pex3_DB_FILE_dm = 'database.json'

# Inicialização do Banco de Dados JSON
def pex3_init_db_dm():
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

def pex3_load_db_dm():
    with open(pex3_DB_FILE_dm, 'r', encoding='utf-8') as f:
        return json.load(f)

def pex3_save_db_dm(pex3_data_dm):
    with open(pex3_DB_FILE_dm, 'w', encoding='utf-8') as f:
        json.dump(pex3_data_dm, f, indent=4, ensure_ascii=False)

def pex3_filtrar_por_data_dm(pex3_transacoes_dm, pex3_data_inicio_dm, pex3_data_fim_dm):
    if not pex3_data_inicio_dm and not pex3_data_fim_dm:
        return pex3_transacoes_dm
    
    pex3_filtradas_dm = []
    for pex3_t_dm in pex3_transacoes_dm:
        pex3_data_t_dm = pex3_t_dm['data_gasto'] # Formato YYYY-MM-DD
        if pex3_data_inicio_dm and pex3_data_t_dm < pex3_data_inicio_dm:
            continue
        if pex3_data_fim_dm and pex3_data_t_dm > pex3_data_fim_dm:
            continue
        pex3_filtradas_dm.append(pex3_t_dm)
    return pex3_filtradas_dm

@pex3_app_dm.route('/')
def pex3_index_dm():
    pex3_db_dm = pex3_load_db_dm()
    pex3_data_inicio_dm = request.args.get('data_inicio', '')
    pex3_data_fim_dm = request.args.get('data_fim', '')
    
    pex3_transacoes_dm = pex3_filtrar_por_data_dm(pex3_db_dm['transactions'], pex3_data_inicio_dm, pex3_data_fim_dm)
    
    pex3_receitas_dm = sum(pex3_t_dm['valor'] for pex3_t_dm in pex3_transacoes_dm if pex3_t_dm['tipo'] == 'receber')
    pex3_despesas_dm = sum(pex3_t_dm['valor'] for pex3_t_dm in pex3_transacoes_dm if pex3_t_dm['tipo'] == 'pagar')
    
    return render_template('index.html', receitas=pex3_receitas_dm, despesas=pex3_despesas_dm, 
                           saldo=pex3_receitas_dm-pex3_despesas_dm, data_inicio=pex3_data_inicio_dm, data_fim=pex3_data_fim_dm)

@pex3_app_dm.route('/lancamentos')
def pex3_lancamentos_dm():
    pex3_db_dm = pex3_load_db_dm()
    pex3_data_inicio_dm = request.args.get('data_inicio', '')
    pex3_data_fim_dm = request.args.get('data_fim', '')
    
    pex3_transacoes_dm = pex3_filtrar_por_data_dm(pex3_db_dm['transactions'], pex3_data_inicio_dm, pex3_data_fim_dm)
    # Ordenar por data decrescente
    pex3_transacoes_dm.sort(key=lambda x: x['data_gasto'], reverse=True)
    
    return render_template('lancamentos.html', transactions=pex3_transacoes_dm, 
                           data_inicio=pex3_data_inicio_dm, data_fim=pex3_data_fim_dm)

@pex3_app_dm.route('/cadastrar/<pex3_tipo_dm>', methods=['GET', 'POST'])
def pex3_cadastrar_dm(pex3_tipo_dm):
    pex3_db_dm = pex3_load_db_dm()
    if request.method == 'POST':
        pex3_nova_transacao_dm = {
            "id": len(pex3_db_dm['transactions']) + 1,
            "tipo": pex3_tipo_dm,
            "data_gasto": request.form['data_gasto'],
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "valor": float(request.form['valor']),
            "categoria": request.form['categoria'],
            "forma_pagamento": request.form.get('forma_pagamento', 'N/A'),
            "descricao": request.form['descricao']
        }
        pex3_db_dm['transactions'].append(pex3_nova_transacao_dm)
        pex3_save_db_dm(pex3_db_dm)
        return redirect(url_for('pex3_lancamentos_dm'))
    
    if pex3_tipo_dm == 'receber':
        pex3_categorias_dm = [pex3_c_dm['nome'] for pex3_c_dm in pex3_db_dm['categories'] if pex3_c_dm['tipo'] in ['receita', 'ambos']]
    else:
        pex3_categorias_dm = [pex3_c_dm['nome'] for pex3_c_dm in pex3_db_dm['categories'] if pex3_c_dm['tipo'] in ['despesa', 'ambos']]
        
    return render_template('form_lancamento.html', tipo=pex3_tipo_dm, categorias=pex3_categorias_dm, metodos=pex3_db_dm['payment_methods'])

@pex3_app_dm.route('/categorias', methods=['GET', 'POST'])
def pex3_categorias_dm():
    pex3_db_dm = pex3_load_db_dm()
    if request.method == 'POST':
        pex3_db_dm['categories'].append({"nome": request.form['nome'], "tipo": request.form['tipo']})
        pex3_save_db_dm(pex3_db_dm)
        return redirect(url_for('pex3_categorias_dm'))
    return render_template('categorias.html', categorias=pex3_db_dm['categories'])

@pex3_app_dm.route('/analytics')
def pex3_analytics_dm():
    pex3_db_dm = pex3_load_db_dm()
    pex3_data_inicio_dm = request.args.get('data_inicio', '')
    pex3_data_fim_dm = request.args.get('data_fim', '')
    
    pex3_transactions_dm = pex3_filtrar_por_data_dm(pex3_db_dm['transactions'], pex3_data_inicio_dm, pex3_data_fim_dm)
    pex3_transactions_dm.sort(key=lambda x: x['data_gasto'])

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
    pex3_dados_mensais_cat_dm = {pex3_cat_dm: [pex3_mensal_categoria_dm[pex3_mes_dm][pex3_cat_dm] for pex3_mes_dm in pex3_meses_ordenados_dm] for pex3_cat_dm in pex3_todas_categorias_gastos_dm}

    return render_template('analytics.html', 
        cat_labels=list(pex3_gastos_por_categoria_dm.keys()), cat_values=list(pex3_gastos_por_categoria_dm.values()),
        pag_labels=list(pex3_pagamentos_receita_data_dm.keys()), pag_values=list(pex3_pagamentos_receita_data_dm.values()),
        meses_labels=pex3_meses_ordenados_dm, 
        mensal_receitas=[pex3_mensal_rec_desp_dm[pex3_m_dm]["receita"] for pex3_m_dm in pex3_meses_ordenados_dm],
        mensal_despesas=[pex3_mensal_rec_desp_dm[pex3_m_dm]["despesa"] for pex3_m_dm in pex3_meses_ordenados_dm],
        evolucao_datas=pex3_evolucao_datas_dm, evolucao_saldo=pex3_evolucao_saldo_dm,
        dados_mensais_cat=pex3_dados_mensais_cat_dm, categorias_lista=pex3_todas_categorias_gastos_dm,
        data_inicio=pex3_data_inicio_dm, data_fim=pex3_data_fim_dm)

if __name__ == '__main__':
    pex3_init_db_dm()
    pex3_app_dm.run(debug=True)