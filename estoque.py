"""
Sistema de Controle de Estoque, Compra e Venda
Desenvolvido em Flask com banco de dados CSV (produtos) e JSON (movimentações)
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import csv
import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

pex3_app_dm = Flask(__name__)
pex3_app_dm.secret_key = 'estoque_secret_key_2025'

# Arquivos de dados
pex3_PRODUTOS_CSV_dm = 'produtos.csv'
pex3_ESTOQUE_DB_dm = 'estoque_db.json'
pex3_FINANCEIRO_DB_dm = 'database.json'

# ============== FUNÇÕES AUXILIARES ==============

def pex3_init_produtos_csv_dm():
    """Inicializa o arquivo CSV de produtos se não existir"""
    if not os.path.exists(pex3_PRODUTOS_CSV_dm):
        with open(pex3_PRODUTOS_CSV_dm, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['codigo_barras', 'nome', 'saldo', 'preco_venda', 'preco_compra'])
            # Produtos de exemplo
            writer.writerow(['7891234567890', 'Produto Exemplo 1', '10', '25.90', '15.50'])
            writer.writerow(['7891234567891', 'Produto Exemplo 2', '5', '49.90', '30.00'])

def pex3_init_estoque_db_dm():
    """Inicializa o arquivo JSON de movimentações se não existir"""
    if not os.path.exists(pex3_ESTOQUE_DB_dm):
        pex3_data_dm = {
            "vendas": [],
            "compras": [],
            "ajustes": []
        }
        with open(pex3_ESTOQUE_DB_dm, 'w', encoding='utf-8') as f:
            json.dump(pex3_data_dm, f, indent=4, ensure_ascii=False)

def pex3_load_produtos_dm():
    """Carrega todos os produtos do CSV"""
    pex3_init_produtos_csv_dm()
    pex3_produtos_dm = []
    with open(pex3_PRODUTOS_CSV_dm, 'r', encoding='utf-8') as f:
        pex3_reader_dm = csv.DictReader(f, delimiter=';')
        for pex3_row_dm in pex3_reader_dm:
            pex3_produtos_dm.append({
                'codigo_barras': pex3_row_dm['codigo_barras'],
                'nome': pex3_row_dm['nome'],
                'saldo': float(pex3_row_dm['saldo']),
                'preco_venda': float(pex3_row_dm['preco_venda']),
                'preco_compra': float(pex3_row_dm['preco_compra'])
            })
    return pex3_produtos_dm

def pex3_save_produtos_dm(pex3_produtos_dm):
    """Salva todos os produtos no CSV"""
    with open(pex3_PRODUTOS_CSV_dm, 'w', newline='', encoding='utf-8') as f:
        pex3_writer_dm = csv.writer(f, delimiter=';')
        pex3_writer_dm.writerow(['codigo_barras', 'nome', 'saldo', 'preco_venda', 'preco_compra'])
        for pex3_p_dm in pex3_produtos_dm:
            pex3_writer_dm.writerow([
                pex3_p_dm['codigo_barras'],
                pex3_p_dm['nome'],
                pex3_p_dm['saldo'],
                pex3_p_dm['preco_venda'],
                pex3_p_dm['preco_compra']
            ])

def pex3_buscar_produto_por_codigo_dm(pex3_codigo_barras_dm):
    """Busca um produto pelo código de barras"""
    pex3_produtos_dm = pex3_load_produtos_dm()
    for pex3_p_dm in pex3_produtos_dm:
        if pex3_p_dm['codigo_barras'] == pex3_codigo_barras_dm:
            return pex3_p_dm
    return None

def pex3_atualizar_saldo_produto_dm(pex3_codigo_barras_dm, pex3_quantidade_dm, pex3_operacao_dm='adicionar'):
    """Atualiza o saldo de um produto"""
    pex3_produtos_dm = pex3_load_produtos_dm()
    for pex3_p_dm in pex3_produtos_dm:
        if pex3_p_dm['codigo_barras'] == pex3_codigo_barras_dm:
            if pex3_operacao_dm == 'adicionar':
                pex3_p_dm['saldo'] = float(pex3_p_dm['saldo']) + float(pex3_quantidade_dm)
            elif pex3_operacao_dm == 'subtrair':
                pex3_p_dm['saldo'] = float(pex3_p_dm['saldo']) - float(pex3_quantidade_dm)
            elif pex3_operacao_dm == 'definir':
                pex3_p_dm['saldo'] = float(pex3_quantidade_dm)
            break
    pex3_save_produtos_dm(pex3_produtos_dm)

def pex3_atualizar_preco_compra_produto_dm(pex3_codigo_barras_dm, pex3_novo_preco_dm):
    """Atualiza o preço de compra de um produto"""
    pex3_produtos_dm = pex3_load_produtos_dm()
    for pex3_p_dm in pex3_produtos_dm:
        if pex3_p_dm['codigo_barras'] == pex3_codigo_barras_dm:
            pex3_p_dm['preco_compra'] = float(pex3_novo_preco_dm)
            break
    pex3_save_produtos_dm(pex3_produtos_dm)

def pex3_load_estoque_db_dm():
    """Carrega o banco de dados de movimentações"""
    pex3_init_estoque_db_dm()
    with open(pex3_ESTOQUE_DB_dm, 'r', encoding='utf-8') as f:
        return json.load(f)

def pex3_save_estoque_db_dm(pex3_data_dm):
    """Salva o banco de dados de movimentações"""
    with open(pex3_ESTOQUE_DB_dm, 'w', encoding='utf-8') as f:
        json.dump(pex3_data_dm, f, indent=4, ensure_ascii=False)

def pex3_load_financeiro_db_dm():
    """Carrega o banco de dados financeiro"""
    with open(pex3_FINANCEIRO_DB_dm, 'r', encoding='utf-8') as f:
        return json.load(f)

def pex3_save_financeiro_db_dm(pex3_data_dm):
    """Salva o banco de dados financeiro"""
    with open(pex3_FINANCEIRO_DB_dm, 'w', encoding='utf-8') as f:
        json.dump(pex3_data_dm, f, indent=4, ensure_ascii=False)

def pex3_gerar_lancamento_financeiro_dm(pex3_tipo_dm, pex3_valor_dm, pex3_descricao_dm, pex3_categoria_dm, pex3_forma_pagamento_dm="A Definir"):
    """Gera um lançamento no sistema financeiro"""
    pex3_db_dm = pex3_load_financeiro_db_dm()
    
    pex3_novo_id_dm = max([pex3_t_dm['id'] for pex3_t_dm in pex3_db_dm['transactions']], default=0) + 1
    
    pex3_lancamento_dm = {
        "id": pex3_novo_id_dm,
        "tipo": pex3_tipo_dm,  # 'pagar' para despesa, 'receber' para receita
        "data_gasto": datetime.now().strftime("%Y-%m-%d"),
        "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "valor": float(pex3_valor_dm),
        "categoria": pex3_categoria_dm,
        "forma_pagamento": pex3_forma_pagamento_dm,
        "descricao": pex3_descricao_dm
    }
    
    pex3_db_dm['transactions'].append(pex3_lancamento_dm)
    pex3_save_financeiro_db_dm(pex3_db_dm)
    return pex3_novo_id_dm

def pex3_formatar_moeda_dm(pex3_valor_dm):
    """Formata valor para moeda brasileira"""
    return f"R$ {pex3_valor_dm:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# ============== ROTAS PRINCIPAIS ==============

@pex3_app_dm.route('/')
def pex3_index_dm():
    """Página inicial - Dashboard do estoque"""
    pex3_produtos_dm = pex3_load_produtos_dm()
    pex3_db_dm = pex3_load_estoque_db_dm()
    
    # Estatísticas
    pex3_total_produtos_dm = len(pex3_produtos_dm)
    pex3_total_itens_dm = sum(pex3_p_dm['saldo'] for pex3_p_dm in pex3_produtos_dm)
    pex3_valor_estoque_dm = sum(pex3_p_dm['saldo'] * pex3_p_dm['preco_compra'] for pex3_p_dm in pex3_produtos_dm)
    pex3_valor_venda_potencial_dm = sum(pex3_p_dm['saldo'] * pex3_p_dm['preco_venda'] for pex3_p_dm in pex3_produtos_dm)
    
    # Produtos com estoque baixo (menos de 5 unidades)
    pex3_produtos_baixo_estoque_dm = [pex3_p_dm for pex3_p_dm in pex3_produtos_dm if pex3_p_dm['saldo'] < 5]
    
    # Últimas movimentações
    pex3_ultimas_vendas_dm = sorted(pex3_db_dm.get('vendas', []), key=lambda x: x['data'], reverse=True)[:5]
    pex3_ultimas_compras_dm = sorted(pex3_db_dm.get('compras', []), key=lambda x: x['data'], reverse=True)[:5]
    
    return render_template('estoque/index.html',
                          total_produtos=pex3_total_produtos_dm,
                          total_itens=pex3_total_itens_dm,
                          valor_estoque=pex3_valor_estoque_dm,
                          valor_venda_potencial=pex3_valor_venda_potencial_dm,
                          produtos_baixo_estoque=pex3_produtos_baixo_estoque_dm,
                          ultimas_vendas=pex3_ultimas_vendas_dm,
                          ultimas_compras=pex3_ultimas_compras_dm)

# ============== ROTAS DE PRODUTOS ==============

@pex3_app_dm.route('/produtos')
def pex3_listar_produtos_dm():
    """Lista todos os produtos cadastrados"""
    pex3_produtos_dm = pex3_load_produtos_dm()
    pex3_busca_dm = request.args.get('busca', '')
    
    if pex3_busca_dm:
        pex3_produtos_dm = [pex3_p_dm for pex3_p_dm in pex3_produtos_dm if pex3_busca_dm.lower() in pex3_p_dm['nome'].lower() or pex3_busca_dm in pex3_p_dm['codigo_barras']]
    
    return render_template('estoque/produtos.html', produtos=pex3_produtos_dm, busca=pex3_busca_dm)

@pex3_app_dm.route('/produtos/cadastrar', methods=['GET', 'POST'])
def pex3_cadastrar_produto_dm():
    """Cadastra um novo produto"""
    if request.method == 'POST':
        pex3_codigo_barras_dm = request.form['codigo_barras'].strip()
        pex3_nome_dm = request.form['nome'].strip()
        pex3_saldo_dm = float(request.form.get('saldo', 0))
        pex3_preco_venda_dm = float(request.form['preco_venda'])
        pex3_preco_compra_dm = float(request.form['preco_compra'])
        
        # Verifica se já existe produto com este código
        if pex3_buscar_produto_por_codigo_dm(pex3_codigo_barras_dm):
            flash('Já existe um produto com este código de barras!', 'error')
            return redirect(url_for('pex3_cadastrar_produto_dm'))
        
        pex3_produtos_dm = pex3_load_produtos_dm()
        pex3_produtos_dm.append({
            'codigo_barras': pex3_codigo_barras_dm,
            'nome': pex3_nome_dm,
            'saldo': pex3_saldo_dm,
            'preco_venda': pex3_preco_venda_dm,
            'preco_compra': pex3_preco_compra_dm
        })
        pex3_save_produtos_dm(pex3_produtos_dm)
        
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('pex3_listar_produtos_dm'))
    
    return render_template('estoque/form_produto.html', produto=None, acao='Cadastrar')

@pex3_app_dm.route('/produtos/editar/<pex3_codigo_barras_dm>', methods=['GET', 'POST'])
def pex3_editar_produto_dm(pex3_codigo_barras_dm):
    """Edita um produto existente"""
    pex3_produto_dm = pex3_buscar_produto_por_codigo_dm(pex3_codigo_barras_dm)
    
    if not pex3_produto_dm:
        flash('Produto não encontrado!', 'error')
        return redirect(url_for('pex3_listar_produtos_dm'))
    
    if request.method == 'POST':
        pex3_produtos_dm = pex3_load_produtos_dm()
        for pex3_p_dm in pex3_produtos_dm:
            if pex3_p_dm['codigo_barras'] == pex3_codigo_barras_dm:
                pex3_p_dm['nome'] = request.form['nome'].strip()
                pex3_p_dm['preco_venda'] = float(request.form['preco_venda'])
                pex3_p_dm['preco_compra'] = float(request.form['preco_compra'])
                break
        pex3_save_produtos_dm(pex3_produtos_dm)
        
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('pex3_listar_produtos_dm'))
    
    return render_template('estoque/form_produto.html', produto=pex3_produto_dm, acao='Editar')

@pex3_app_dm.route('/produtos/excluir/<pex3_codigo_barras_dm>', methods=['POST'])
def pex3_excluir_produto_dm(pex3_codigo_barras_dm):
    """Exclui um produto"""
    pex3_produtos_dm = pex3_load_produtos_dm()
    pex3_produtos_dm = [pex3_p_dm for pex3_p_dm in pex3_produtos_dm if pex3_p_dm['codigo_barras'] != pex3_codigo_barras_dm]
    pex3_save_produtos_dm(pex3_produtos_dm)
    
    flash('Produto exluído com sucesso!', 'success')
    return redirect(url_for('pex3_listar_produtos_dm'))

# ============== ROTAS DE AJUSTE DE ESTOQUE ==============

@pex3_app_dm.route('/ajuste-estoque', methods=['GET', 'POST'])
def pex3_ajuste_estoque_dm():
    """Ajuste/Correção de saldo do estoque"""
    if request.method == 'POST':
        pex3_codigo_barras_dm = request.form['codigo_barras'].strip()
        pex3_quantidade_dm = float(request.form['quantidade'])
        pex3_tipo_ajuste_dm = request.form['tipo_ajuste']  # 'entrada', 'saida', 'definir'
        pex3_motivo_dm = request.form.get('motivo', '')
        
        pex3_produto_dm = pex3_buscar_produto_por_codigo_dm(pex3_codigo_barras_dm)
        if not pex3_produto_dm:
            flash('Produto não encontrado!', 'error')
            return redirect(url_for('pex3_ajuste_estoque_dm'))
        
        pex3_saldo_anterior_dm = pex3_produto_dm['saldo']
        
        if pex3_tipo_ajuste_dm == 'entrada':
            pex3_atualizar_saldo_produto_dm(pex3_codigo_barras_dm, pex3_quantidade_dm, 'adicionar')
            pex3_novo_saldo_dm = pex3_saldo_anterior_dm + pex3_quantidade_dm
        elif pex3_tipo_ajuste_dm == 'saida':
            if pex3_quantidade_dm > pex3_saldo_anterior_dm:
                flash('Quantidade de saída maior que o saldo disponível!', 'error')
                return redirect(url_for('pex3_ajuste_estoque_dm'))
            pex3_atualizar_saldo_produto_dm(pex3_codigo_barras_dm, pex3_quantidade_dm, 'subtrair')
            pex3_novo_saldo_dm = pex3_saldo_anterior_dm - pex3_quantidade_dm
        else:  # definir
            pex3_atualizar_saldo_produto_dm(pex3_codigo_barras_dm, pex3_quantidade_dm, 'definir')
            pex3_novo_saldo_dm = pex3_quantidade_dm
        
        # Registra o ajuste
        pex3_db_dm = pex3_load_estoque_db_dm()
        pex3_ajuste_dm = {
            'id': len(pex3_db_dm.get('ajustes', [])) + 1,
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'codigo_barras': pex3_codigo_barras_dm,
            'nome_produto': pex3_produto_dm['nome'],
            'tipo_ajuste': pex3_tipo_ajuste_dm,
            'quantidade': pex3_quantidade_dm,
            'saldo_anterior': pex3_saldo_anterior_dm,
            'saldo_novo': pex3_novo_saldo_dm,
            'motivo': pex3_motivo_dm
        }
        
        if 'ajustes' not in pex3_db_dm:
            pex3_db_dm['ajustes'] = []
        pex3_db_dm['ajustes'].append(pex3_ajuste_dm)
        pex3_save_estoque_db_dm(pex3_db_dm)
        
        flash(f'Estoque ajustado com sucesso! Novo saldo: {pex3_novo_saldo_dm}', 'success')
        return redirect(url_for('pex3_ajuste_estoque_dm'))
    
    return render_template('estoque/ajuste_estoque.html')

# ============== ROTAS DE COMPRAS ==============

@pex3_app_dm.route('/compras')
def pex3_listar_compras_dm():
    """Lista todas as compras realizadas"""
    pex3_db_dm = pex3_load_estoque_db_dm()
    pex3_compras_dm = sorted(pex3_db_dm.get('compras', []), key=lambda x: x['data'], reverse=True)
    
    pex3_data_inicio_dm = request.args.get('data_inicio', '')
    pex3_data_fim_dm = request.args.get('data_fim', '')
    
    if pex3_data_inicio_dm:
        pex3_compras_dm = [pex3_c_dm for pex3_c_dm in pex3_compras_dm if pex3_c_dm['data'][:10] >= pex3_data_inicio_dm]
    if pex3_data_fim_dm:
        pex3_compras_dm = [pex3_c_dm for pex3_c_dm in pex3_compras_dm if pex3_c_dm['data'][:10] <= pex3_data_fim_dm]
    
    return render_template('estoque/compras.html', compras=pex3_compras_dm, 
                          data_inicio=pex3_data_inicio_dm, data_fim=pex3_data_fim_dm)

@pex3_app_dm.route('/compras/nova', methods=['GET', 'POST'])
def pex3_nova_compra_dm():
    """Registra uma nova compra"""
    if request.method == 'POST':
        pex3_fornecedor_dm = request.form.get('fornecedor', '')
        pex3_numero_nf_dm = request.form.get('numero_nf', '')
        pex3_observacao_dm = request.form.get('observacao', '')
        pex3_forma_pagamento_dm = request.form.get('forma_pagamento', 'A Definir')
        
        # Processa os itens da compra
        pex3_itens_dm = []
        pex3_codigos_dm = request.form.getlist('item_codigo[]')
        pex3_quantidades_dm = request.form.getlist('item_quantidade[]')
        pex3_precos_dm = request.form.getlist('item_preco[]')
        
        pex3_valor_total_dm = 0
        
        for pex3_i_dm, pex3_codigo_dm in enumerate(pex3_codigos_dm):
            if pex3_codigo_dm.strip():
                pex3_produto_dm = pex3_buscar_produto_por_codigo_dm(pex3_codigo_dm.strip())
                if pex3_produto_dm:
                    pex3_qtd_dm = float(pex3_quantidades_dm[pex3_i_dm]) if pex3_quantidades_dm[pex3_i_dm] else 0
                    pex3_preco_dm = float(pex3_precos_dm[pex3_i_dm]) if pex3_precos_dm[pex3_i_dm] else pex3_produto_dm['preco_compra']
                    pex3_subtotal_dm = pex3_qtd_dm * pex3_preco_dm
                    
                    pex3_itens_dm.append({
                        'codigo_barras': pex3_codigo_dm.strip(),
                        'nome_produto': pex3_produto_dm['nome'],
                        'quantidade': pex3_qtd_dm,
                        'preco_unitario': pex3_preco_dm,
                        'subtotal': pex3_subtotal_dm
                    })
                    
                    pex3_valor_total_dm += pex3_subtotal_dm
                    
                    # Atualiza o estoque e o preço de compra
                    pex3_atualizar_saldo_produto_dm(pex3_codigo_dm.strip(), pex3_qtd_dm, 'adicionar')
                    pex3_atualizar_preco_compra_produto_dm(pex3_codigo_dm.strip(), pex3_preco_dm)
        
        if not pex3_itens_dm:
            flash('Nenhum item válido na compra!', 'error')
            return redirect(url_for('pex3_nova_compra_dm'))
        
        # Registra a compra
        pex3_db_dm = pex3_load_estoque_db_dm()
        pex3_compra_dm = {
            'id': len(pex3_db_dm.get('compras', [])) + 1,
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'fornecedor': pex3_fornecedor_dm,
            'numero_nf': pex3_numero_nf_dm,
            'itens': pex3_itens_dm,
            'valor_total': pex3_valor_total_dm,
            'forma_pagamento': pex3_forma_pagamento_dm,
            'observacao': pex3_observacao_dm
        }
        
        if 'compras' not in pex3_db_dm:
            pex3_db_dm['compras'] = []
        pex3_db_dm['compras'].append(pex3_compra_dm)
        pex3_save_estoque_db_dm(pex3_db_dm)
        
        # Gera lançamento financeiro de despesa
        pex3_descricao_fin_dm = f"Compra #{pex3_compra_dm['id']}"
        if pex3_fornecedor_dm:
            pex3_descricao_fin_dm += f" - {pex3_fornecedor_dm}"
        if pex3_numero_nf_dm:
            pex3_descricao_fin_dm += f" - NF: {pex3_numero_nf_dm}"
        
        pex3_gerar_lancamento_financeiro_dm('pagar', pex3_valor_total_dm, pex3_descricao_fin_dm, 'Compra de Produtos', pex3_forma_pagamento_dm)
        
        flash(f'Compra registrada com sucesso! Total: R$ {pex3_valor_total_dm:.2f}', 'success')
        return redirect(url_for('pex3_listar_compras_dm'))
    
    return render_template('estoque/form_compra.html')

@pex3_app_dm.route('/compras/detalhes/<int:pex3_compra_id_dm>')
def pex3_detalhes_compra_dm(pex3_compra_id_dm):
    """Mostra detalhes de uma compra"""
    pex3_db_dm = pex3_load_estoque_db_dm()
    pex3_compra_dm = next((pex3_c_dm for pex3_c_dm in pex3_db_dm.get('compras', []) if pex3_c_dm['id'] == pex3_compra_id_dm), None)
    
    if not pex3_compra_dm:
        flash('Compra não encontrada!', 'error')
        return redirect(url_for('pex3_listar_compras_dm'))
    
    return render_template('estoque/detalhes_compra.html', compra=pex3_compra_dm)

# ============== ROTAS DE VENDAS ==============

@pex3_app_dm.route('/vendas')
def pex3_listar_vendas_dm():
    """Lista todas as vendas realizadas"""
    pex3_db_dm = pex3_load_estoque_db_dm()
    pex3_vendas_dm = sorted(pex3_db_dm.get('vendas', []), key=lambda x: x['data'], reverse=True)
    
    pex3_data_inicio_dm = request.args.get('data_inicio', '')
    pex3_data_fim_dm = request.args.get('data_fim', '')
    
    if pex3_data_inicio_dm:
        pex3_vendas_dm = [pex3_v_dm for pex3_v_dm in pex3_vendas_dm if pex3_v_dm['data'][:10] >= pex3_data_inicio_dm]
    if pex3_data_fim_dm:
        pex3_vendas_dm = [pex3_v_dm for pex3_v_dm in pex3_vendas_dm if pex3_v_dm['data'][:10] <= pex3_data_fim_dm]
    
    return render_template('estoque/vendas.html', vendas=pex3_vendas_dm,
                          data_inicio=pex3_data_inicio_dm, data_fim=pex3_data_fim_dm)

@pex3_app_dm.route('/vendas/nova', methods=['GET', 'POST'])
def pex3_nova_venda_dm():
    """Registra uma nova venda"""
    if request.method == 'POST':
        pex3_cliente_dm = request.form.get('cliente', '')
        pex3_observacao_dm = request.form.get('observacao', '')
        pex3_desconto_dm = float(request.form.get('desconto', 0))
        pex3_forma_pagamento_dm = request.form.get('forma_pagamento', 'A Definir')
        
        # Processa os itens da venda
        pex3_itens_dm = []
        pex3_codigos_dm = request.form.getlist('item_codigo[]')
        pex3_quantidades_dm = request.form.getlist('item_quantidade[]')
        pex3_precos_dm = request.form.getlist('item_preco[]')
        
        pex3_valor_bruto_dm = 0
        
        for pex3_i_dm, pex3_codigo_dm in enumerate(pex3_codigos_dm):
            if pex3_codigo_dm.strip():
                pex3_produto_dm = pex3_buscar_produto_por_codigo_dm(pex3_codigo_dm.strip())
                if pex3_produto_dm:
                    pex3_qtd_dm = float(pex3_quantidades_dm[pex3_i_dm]) if pex3_quantidades_dm[pex3_i_dm] else 0
                    pex3_preco_dm = float(pex3_precos_dm[pex3_i_dm]) if pex3_precos_dm[pex3_i_dm] else pex3_produto_dm['preco_venda']
                    
                    # Verifica estoque disponível
                    if pex3_qtd_dm > pex3_produto_dm['saldo']:
                        flash(f'Estoque insuficiente para {pex3_produto_dm["nome"]}! Disponível: {pex3_produto_dm["saldo"]}', 'error')
                        return redirect(url_for('pex3_nova_venda_dm'))
                    
                    pex3_subtotal_dm = pex3_qtd_dm * pex3_preco_dm
                    
                    pex3_itens_dm.append({
                        'codigo_barras': pex3_codigo_dm.strip(),
                        'nome_produto': pex3_produto_dm['nome'],
                        'quantidade': pex3_qtd_dm,
                        'preco_unitario': pex3_preco_dm,
                        'preco_custo': pex3_produto_dm['preco_compra'],
                        'subtotal': pex3_subtotal_dm
                    })
                    
                    pex3_valor_bruto_dm += pex3_subtotal_dm
                    
                    # Atualiza o estoque
                    pex3_atualizar_saldo_produto_dm(pex3_codigo_dm.strip(), pex3_qtd_dm, 'subtrair')
        
        if not pex3_itens_dm:
            flash('Nenhum item válido na venda!', 'error')
            return redirect(url_for('pex3_nova_venda_dm'))
        
        pex3_valor_total_dm = pex3_valor_bruto_dm - pex3_desconto_dm
        
        # Calcula o lucro
        pex3_custo_total_dm = sum(pex3_item_dm['quantidade'] * pex3_item_dm['preco_custo'] for pex3_item_dm in pex3_itens_dm)
        pex3_lucro_dm = pex3_valor_total_dm - pex3_custo_total_dm
        
        # Registra a venda
        pex3_db_dm = pex3_load_estoque_db_dm()
        pex3_venda_dm = {
            'id': len(pex3_db_dm.get('vendas', [])) + 1,
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cliente': pex3_cliente_dm,
            'itens': pex3_itens_dm,
            'valor_bruto': pex3_valor_bruto_dm,
            'desconto': pex3_desconto_dm,
            'valor_total': pex3_valor_total_dm,
            'custo_total': pex3_custo_total_dm,
            'lucro': pex3_lucro_dm,
            'forma_pagamento': pex3_forma_pagamento_dm,
            'observacao': pex3_observacao_dm
        }
        
        if 'vendas' not in pex3_db_dm:
            pex3_db_dm['vendas'] = []
        pex3_db_dm['vendas'].append(pex3_venda_dm)
        pex3_save_estoque_db_dm(pex3_db_dm)
        
        # Gera lançamento financeiro de receita (contas a receber)
        pex3_descricao_fin_dm = f"Venda #{pex3_venda_dm['id']}"
        if pex3_cliente_dm:
            pex3_descricao_fin_dm += f" - {pex3_cliente_dm}"
        
        pex3_gerar_lancamento_financeiro_dm('receber', pex3_valor_total_dm, pex3_descricao_fin_dm, 'Venda de Produtos', pex3_forma_pagamento_dm)
        
        flash(f'Venda registrada com sucesso! Total: R$ {pex3_valor_total_dm:.2f}', 'success')
        return redirect(url_for('pex3_listar_vendas_dm'))
    
    return render_template('estoque/form_venda.html')

@pex3_app_dm.route('/vendas/detalhes/<int:pex3_venda_id_dm>')
def pex3_detalhes_venda_dm(pex3_venda_id_dm):
    """Mostra detalhes de uma venda"""
    pex3_db_dm = pex3_load_estoque_db_dm()
    pex3_venda_dm = next((pex3_v_dm for pex3_v_dm in pex3_db_dm.get('vendas', []) if pex3_v_dm['id'] == pex3_venda_id_dm), None)
    
    if not pex3_venda_dm:
        flash('Venda não encontrada!', 'error')
        return redirect(url_for('pex3_listar_vendas_dm'))
    
    return render_template('estoque/detalhes_venda.html', venda=pex3_venda_dm)

# ============== ROTAS DE API (AJAX) ==============

@pex3_app_dm.route('/api/produto/<pex3_codigo_barras_dm>')
def pex3_api_buscar_produto_dm(pex3_codigo_barras_dm):
    """API para buscar produto por código de barras"""
    pex3_produto_dm = pex3_buscar_produto_por_codigo_dm(pex3_codigo_barras_dm)
    if pex3_produto_dm:
        return jsonify({
            'success': True,
            'produto': pex3_produto_dm
        })
    return jsonify({
        'success': False,
        'message': 'Produto não encontrado'
    })

@pex3_app_dm.route('/api/produtos/buscar')
def pex3_api_buscar_produtos_dm():
    """API para buscar produtos por nome ou código"""
    pex3_termo_dm = request.args.get('termo', '')
    pex3_produtos_dm = pex3_load_produtos_dm()
    
    if pex3_termo_dm:
        pex3_produtos_dm = [pex3_p_dm for pex3_p_dm in pex3_produtos_dm if pex3_termo_dm.lower() in pex3_p_dm['nome'].lower() or pex3_termo_dm in pex3_p_dm['codigo_barras']]
    
    return jsonify({
        'success': True,
        'produtos': pex3_produtos_dm[:10]  # Limita a 10 resultados
    })

# ============== RELATÓRIOS ==============

@pex3_app_dm.route('/relatorios')
def pex3_relatorios_dm():
    """Página de relatórios"""
    return render_template('estoque/relatorios.html')

@pex3_app_dm.route('/relatorios/movimentacao')
def pex3_relatorio_movimentacao_dm():
    """Relatório de movimentação de estoque"""
    pex3_db_dm = pex3_load_estoque_db_dm()
    pex3_data_inicio_dm = request.args.get('data_inicio', '')
    pex3_data_fim_dm = request.args.get('data_fim', '')
    
    pex3_vendas_dm = pex3_db_dm.get('vendas', [])
    pex3_compras_dm = pex3_db_dm.get('compras', [])
    pex3_ajustes_dm = pex3_db_dm.get('ajustes', [])
    
    if pex3_data_inicio_dm:
        pex3_vendas_dm = [pex3_v_dm for pex3_v_dm in pex3_vendas_dm if pex3_v_dm['data'][:10] >= pex3_data_inicio_dm]
        pex3_compras_dm = [pex3_c_dm for pex3_c_dm in pex3_compras_dm if pex3_c_dm['data'][:10] >= pex3_data_inicio_dm]
        pex3_ajustes_dm = [pex3_a_dm for pex3_a_dm in pex3_ajustes_dm if pex3_a_dm['data'][:10] >= pex3_data_inicio_dm]
    
    if pex3_data_fim_dm:
        pex3_vendas_dm = [pex3_v_dm for pex3_v_dm in pex3_vendas_dm if pex3_v_dm['data'][:10] <= pex3_data_fim_dm]
        pex3_compras_dm = [pex3_c_dm for pex3_c_dm in pex3_compras_dm if pex3_c_dm['data'][:10] <= pex3_data_fim_dm]
        pex3_ajustes_dm = [pex3_a_dm for pex3_a_dm in pex3_ajustes_dm if pex3_a_dm['data'][:10] <= pex3_data_fim_dm]
    
    pex3_total_vendas_dm = sum(pex3_v_dm['valor_total'] for pex3_v_dm in pex3_vendas_dm)
    pex3_total_compras_dm = sum(pex3_c_dm['valor_total'] for pex3_c_dm in pex3_compras_dm)
    pex3_total_lucro_dm = sum(pex3_v_dm.get('lucro', 0) for pex3_v_dm in pex3_vendas_dm)
    
    return render_template('estoque/relatorio_movimentacao.html',
                          vendas=pex3_vendas_dm,
                          compras=pex3_compras_dm,
                          ajustes=pex3_ajustes_dm,
                          total_vendas=pex3_total_vendas_dm,
                          total_compras=pex3_total_compras_dm,
                          total_lucro=pex3_total_lucro_dm,
                          data_inicio=pex3_data_inicio_dm,
                          data_fim=pex3_data_fim_dm)

# ============== INICIALIZAÇÃO ==============

def pex3_init_app_dm():
    """Inicializa os arquivos necessários"""
    pex3_init_produtos_csv_dm()
    pex3_init_estoque_db_dm()
    
    # Verifica e adiciona categorias financeiras se necessário
    try:
        pex3_db_dm = pex3_load_financeiro_db_dm()
        pex3_categorias_existentes_dm = [pex3_c_dm['nome'] for pex3_c_dm in pex3_db_dm.get('categories', [])]
        
        pex3_novas_categorias_dm = [
            {"nome": "Compra de Produtos", "tipo": "despesa"},
            {"nome": "Venda de Produtos", "tipo": "receita"}
        ]
        
        for pex3_cat_dm in pex3_novas_categorias_dm:
            if pex3_cat_dm['nome'] not in pex3_categorias_existentes_dm:
                pex3_db_dm['categories'].append(pex3_cat_dm)
        
        pex3_save_financeiro_db_dm(pex3_db_dm)
    except:
        pass  # Se o arquivo financeiro não existir, ignora

if __name__ == '__main__':
    pex3_init_app_dm()
    pex3_app_dm.run(debug=True, port=5001)
