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

app = Flask(__name__)
app.secret_key = 'estoque_secret_key_2025'

# Arquivos de dados
PRODUTOS_CSV = 'produtos.csv'
ESTOQUE_DB = 'estoque_db.json'
FINANCEIRO_DB = 'database.json'

# ============== FUNÇÕES AUXILIARES ==============

def init_produtos_csv():
    """Inicializa o arquivo CSV de produtos se não existir"""
    if not os.path.exists(PRODUTOS_CSV):
        with open(PRODUTOS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['codigo_barras', 'nome', 'saldo', 'preco_venda', 'preco_compra'])
            # Produtos de exemplo
            writer.writerow(['7891234567890', 'Produto Exemplo 1', '10', '25.90', '15.50'])
            writer.writerow(['7891234567891', 'Produto Exemplo 2', '5', '49.90', '30.00'])

def init_estoque_db():
    """Inicializa o arquivo JSON de movimentações se não existir"""
    if not os.path.exists(ESTOQUE_DB):
        data = {
            "vendas": [],
            "compras": [],
            "ajustes": []
        }
        with open(ESTOQUE_DB, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def load_produtos():
    """Carrega todos os produtos do CSV"""
    init_produtos_csv()
    produtos = []
    with open(PRODUTOS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            produtos.append({
                'codigo_barras': row['codigo_barras'],
                'nome': row['nome'],
                'saldo': float(row['saldo']),
                'preco_venda': float(row['preco_venda']),
                'preco_compra': float(row['preco_compra'])
            })
    return produtos

def save_produtos(produtos):
    """Salva todos os produtos no CSV"""
    with open(PRODUTOS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['codigo_barras', 'nome', 'saldo', 'preco_venda', 'preco_compra'])
        for p in produtos:
            writer.writerow([
                p['codigo_barras'],
                p['nome'],
                p['saldo'],
                p['preco_venda'],
                p['preco_compra']
            ])

def buscar_produto_por_codigo(codigo_barras):
    """Busca um produto pelo código de barras"""
    produtos = load_produtos()
    for p in produtos:
        if p['codigo_barras'] == codigo_barras:
            return p
    return None

def atualizar_saldo_produto(codigo_barras, quantidade, operacao='adicionar'):
    """Atualiza o saldo de um produto"""
    produtos = load_produtos()
    for p in produtos:
        if p['codigo_barras'] == codigo_barras:
            if operacao == 'adicionar':
                p['saldo'] = float(p['saldo']) + float(quantidade)
            elif operacao == 'subtrair':
                p['saldo'] = float(p['saldo']) - float(quantidade)
            elif operacao == 'definir':
                p['saldo'] = float(quantidade)
            break
    save_produtos(produtos)

def atualizar_preco_compra_produto(codigo_barras, novo_preco):
    """Atualiza o preço de compra de um produto"""
    produtos = load_produtos()
    for p in produtos:
        if p['codigo_barras'] == codigo_barras:
            p['preco_compra'] = float(novo_preco)
            break
    save_produtos(produtos)

def load_estoque_db():
    """Carrega o banco de dados de movimentações"""
    init_estoque_db()
    with open(ESTOQUE_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_estoque_db(data):
    """Salva o banco de dados de movimentações"""
    with open(ESTOQUE_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_financeiro_db():
    """Carrega o banco de dados financeiro"""
    with open(FINANCEIRO_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_financeiro_db(data):
    """Salva o banco de dados financeiro"""
    with open(FINANCEIRO_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def gerar_lancamento_financeiro(tipo, valor, descricao, categoria):
    """Gera um lançamento no sistema financeiro"""
    db = load_financeiro_db()
    
    novo_id = max([t['id'] for t in db['transactions']], default=0) + 1
    
    lancamento = {
        "id": novo_id,
        "tipo": tipo,  # 'pagar' para despesa, 'receber' para receita
        "data_gasto": datetime.now().strftime("%Y-%m-%d"),
        "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "valor": float(valor),
        "categoria": categoria,
        "forma_pagamento": "A Definir",
        "descricao": descricao
    }
    
    db['transactions'].append(lancamento)
    save_financeiro_db(db)
    return novo_id

def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# ============== ROTAS PRINCIPAIS ==============

@app.route('/')
def index():
    """Página inicial - Dashboard do estoque"""
    produtos = load_produtos()
    db = load_estoque_db()
    
    # Estatísticas
    total_produtos = len(produtos)
    total_itens = sum(p['saldo'] for p in produtos)
    valor_estoque = sum(p['saldo'] * p['preco_compra'] for p in produtos)
    valor_venda_potencial = sum(p['saldo'] * p['preco_venda'] for p in produtos)
    
    # Produtos com estoque baixo (menos de 5 unidades)
    produtos_baixo_estoque = [p for p in produtos if p['saldo'] < 5]
    
    # Últimas movimentações
    ultimas_vendas = sorted(db.get('vendas', []), key=lambda x: x['data'], reverse=True)[:5]
    ultimas_compras = sorted(db.get('compras', []), key=lambda x: x['data'], reverse=True)[:5]
    
    return render_template('estoque/index.html',
                          total_produtos=total_produtos,
                          total_itens=total_itens,
                          valor_estoque=valor_estoque,
                          valor_venda_potencial=valor_venda_potencial,
                          produtos_baixo_estoque=produtos_baixo_estoque,
                          ultimas_vendas=ultimas_vendas,
                          ultimas_compras=ultimas_compras)

# ============== ROTAS DE PRODUTOS ==============

@app.route('/produtos')
def listar_produtos():
    """Lista todos os produtos cadastrados"""
    produtos = load_produtos()
    busca = request.args.get('busca', '')
    
    if busca:
        produtos = [p for p in produtos if busca.lower() in p['nome'].lower() or busca in p['codigo_barras']]
    
    return render_template('estoque/produtos.html', produtos=produtos, busca=busca)

@app.route('/produtos/cadastrar', methods=['GET', 'POST'])
def cadastrar_produto():
    """Cadastra um novo produto"""
    if request.method == 'POST':
        codigo_barras = request.form['codigo_barras'].strip()
        nome = request.form['nome'].strip()
        saldo = float(request.form.get('saldo', 0))
        preco_venda = float(request.form['preco_venda'])
        preco_compra = float(request.form['preco_compra'])
        
        # Verifica se já existe produto com este código
        if buscar_produto_por_codigo(codigo_barras):
            flash('Já existe um produto com este código de barras!', 'error')
            return redirect(url_for('cadastrar_produto'))
        
        produtos = load_produtos()
        produtos.append({
            'codigo_barras': codigo_barras,
            'nome': nome,
            'saldo': saldo,
            'preco_venda': preco_venda,
            'preco_compra': preco_compra
        })
        save_produtos(produtos)
        
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    
    return render_template('estoque/form_produto.html', produto=None, acao='Cadastrar')

@app.route('/produtos/editar/<codigo_barras>', methods=['GET', 'POST'])
def editar_produto(codigo_barras):
    """Edita um produto existente"""
    produto = buscar_produto_por_codigo(codigo_barras)
    
    if not produto:
        flash('Produto não encontrado!', 'error')
        return redirect(url_for('listar_produtos'))
    
    if request.method == 'POST':
        produtos = load_produtos()
        for p in produtos:
            if p['codigo_barras'] == codigo_barras:
                p['nome'] = request.form['nome'].strip()
                p['preco_venda'] = float(request.form['preco_venda'])
                p['preco_compra'] = float(request.form['preco_compra'])
                break
        save_produtos(produtos)
        
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    
    return render_template('estoque/form_produto.html', produto=produto, acao='Editar')

@app.route('/produtos/excluir/<codigo_barras>', methods=['POST'])
def excluir_produto(codigo_barras):
    """Exclui um produto"""
    produtos = load_produtos()
    produtos = [p for p in produtos if p['codigo_barras'] != codigo_barras]
    save_produtos(produtos)
    
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('listar_produtos'))

# ============== ROTAS DE AJUSTE DE ESTOQUE ==============

@app.route('/ajuste-estoque', methods=['GET', 'POST'])
def ajuste_estoque():
    """Ajuste/Correção de saldo do estoque"""
    if request.method == 'POST':
        codigo_barras = request.form['codigo_barras'].strip()
        quantidade = float(request.form['quantidade'])
        tipo_ajuste = request.form['tipo_ajuste']  # 'entrada', 'saida', 'definir'
        motivo = request.form.get('motivo', '')
        
        produto = buscar_produto_por_codigo(codigo_barras)
        if not produto:
            flash('Produto não encontrado!', 'error')
            return redirect(url_for('ajuste_estoque'))
        
        saldo_anterior = produto['saldo']
        
        if tipo_ajuste == 'entrada':
            atualizar_saldo_produto(codigo_barras, quantidade, 'adicionar')
            novo_saldo = saldo_anterior + quantidade
        elif tipo_ajuste == 'saida':
            if quantidade > saldo_anterior:
                flash('Quantidade de saída maior que o saldo disponível!', 'error')
                return redirect(url_for('ajuste_estoque'))
            atualizar_saldo_produto(codigo_barras, quantidade, 'subtrair')
            novo_saldo = saldo_anterior - quantidade
        else:  # definir
            atualizar_saldo_produto(codigo_barras, quantidade, 'definir')
            novo_saldo = quantidade
        
        # Registra o ajuste
        db = load_estoque_db()
        ajuste = {
            'id': len(db.get('ajustes', [])) + 1,
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'codigo_barras': codigo_barras,
            'nome_produto': produto['nome'],
            'tipo_ajuste': tipo_ajuste,
            'quantidade': quantidade,
            'saldo_anterior': saldo_anterior,
            'saldo_novo': novo_saldo,
            'motivo': motivo
        }
        
        if 'ajustes' not in db:
            db['ajustes'] = []
        db['ajustes'].append(ajuste)
        save_estoque_db(db)
        
        flash(f'Estoque ajustado com sucesso! Novo saldo: {novo_saldo}', 'success')
        return redirect(url_for('ajuste_estoque'))
    
    return render_template('estoque/ajuste_estoque.html')

# ============== ROTAS DE COMPRAS ==============

@app.route('/compras')
def listar_compras():
    """Lista todas as compras realizadas"""
    db = load_estoque_db()
    compras = sorted(db.get('compras', []), key=lambda x: x['data'], reverse=True)
    
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    if data_inicio:
        compras = [c for c in compras if c['data'][:10] >= data_inicio]
    if data_fim:
        compras = [c for c in compras if c['data'][:10] <= data_fim]
    
    return render_template('estoque/compras.html', compras=compras, 
                          data_inicio=data_inicio, data_fim=data_fim)

@app.route('/compras/nova', methods=['GET', 'POST'])
def nova_compra():
    """Registra uma nova compra"""
    if request.method == 'POST':
        fornecedor = request.form.get('fornecedor', '')
        numero_nf = request.form.get('numero_nf', '')
        observacao = request.form.get('observacao', '')
        
        # Processa os itens da compra
        itens = []
        codigos = request.form.getlist('item_codigo[]')
        quantidades = request.form.getlist('item_quantidade[]')
        precos = request.form.getlist('item_preco[]')
        
        valor_total = 0
        
        for i, codigo in enumerate(codigos):
            if codigo.strip():
                produto = buscar_produto_por_codigo(codigo.strip())
                if produto:
                    qtd = float(quantidades[i]) if quantidades[i] else 0
                    preco = float(precos[i]) if precos[i] else produto['preco_compra']
                    subtotal = qtd * preco
                    
                    itens.append({
                        'codigo_barras': codigo.strip(),
                        'nome_produto': produto['nome'],
                        'quantidade': qtd,
                        'preco_unitario': preco,
                        'subtotal': subtotal
                    })
                    
                    valor_total += subtotal
                    
                    # Atualiza o estoque e o preço de compra
                    atualizar_saldo_produto(codigo.strip(), qtd, 'adicionar')
                    atualizar_preco_compra_produto(codigo.strip(), preco)
        
        if not itens:
            flash('Nenhum item válido na compra!', 'error')
            return redirect(url_for('nova_compra'))
        
        # Registra a compra
        db = load_estoque_db()
        compra = {
            'id': len(db.get('compras', [])) + 1,
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'fornecedor': fornecedor,
            'numero_nf': numero_nf,
            'itens': itens,
            'valor_total': valor_total,
            'observacao': observacao
        }
        
        if 'compras' not in db:
            db['compras'] = []
        db['compras'].append(compra)
        save_estoque_db(db)
        
        # Gera lançamento financeiro de despesa
        descricao_fin = f"Compra #{compra['id']}"
        if fornecedor:
            descricao_fin += f" - {fornecedor}"
        if numero_nf:
            descricao_fin += f" - NF: {numero_nf}"
        
        gerar_lancamento_financeiro('pagar', valor_total, descricao_fin, 'Compra de Produtos')
        
        flash(f'Compra registrada com sucesso! Total: R$ {valor_total:.2f}', 'success')
        return redirect(url_for('listar_compras'))
    
    return render_template('estoque/form_compra.html')

@app.route('/compras/detalhes/<int:compra_id>')
def detalhes_compra(compra_id):
    """Mostra detalhes de uma compra"""
    db = load_estoque_db()
    compra = next((c for c in db.get('compras', []) if c['id'] == compra_id), None)
    
    if not compra:
        flash('Compra não encontrada!', 'error')
        return redirect(url_for('listar_compras'))
    
    return render_template('estoque/detalhes_compra.html', compra=compra)

# ============== ROTAS DE VENDAS ==============

@app.route('/vendas')
def listar_vendas():
    """Lista todas as vendas realizadas"""
    db = load_estoque_db()
    vendas = sorted(db.get('vendas', []), key=lambda x: x['data'], reverse=True)
    
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    if data_inicio:
        vendas = [v for v in vendas if v['data'][:10] >= data_inicio]
    if data_fim:
        vendas = [v for v in vendas if v['data'][:10] <= data_fim]
    
    return render_template('estoque/vendas.html', vendas=vendas,
                          data_inicio=data_inicio, data_fim=data_fim)

@app.route('/vendas/nova', methods=['GET', 'POST'])
def nova_venda():
    """Registra uma nova venda"""
    if request.method == 'POST':
        cliente = request.form.get('cliente', '')
        observacao = request.form.get('observacao', '')
        desconto = float(request.form.get('desconto', 0))
        
        # Processa os itens da venda
        itens = []
        codigos = request.form.getlist('item_codigo[]')
        quantidades = request.form.getlist('item_quantidade[]')
        precos = request.form.getlist('item_preco[]')
        
        valor_bruto = 0
        
        for i, codigo in enumerate(codigos):
            if codigo.strip():
                produto = buscar_produto_por_codigo(codigo.strip())
                if produto:
                    qtd = float(quantidades[i]) if quantidades[i] else 0
                    preco = float(precos[i]) if precos[i] else produto['preco_venda']
                    
                    # Verifica estoque disponível
                    if qtd > produto['saldo']:
                        flash(f'Estoque insuficiente para {produto["nome"]}! Disponível: {produto["saldo"]}', 'error')
                        return redirect(url_for('nova_venda'))
                    
                    subtotal = qtd * preco
                    
                    itens.append({
                        'codigo_barras': codigo.strip(),
                        'nome_produto': produto['nome'],
                        'quantidade': qtd,
                        'preco_unitario': preco,
                        'preco_custo': produto['preco_compra'],
                        'subtotal': subtotal
                    })
                    
                    valor_bruto += subtotal
                    
                    # Atualiza o estoque
                    atualizar_saldo_produto(codigo.strip(), qtd, 'subtrair')
        
        if not itens:
            flash('Nenhum item válido na venda!', 'error')
            return redirect(url_for('nova_venda'))
        
        valor_total = valor_bruto - desconto
        
        # Calcula o lucro
        custo_total = sum(item['quantidade'] * item['preco_custo'] for item in itens)
        lucro = valor_total - custo_total
        
        # Registra a venda
        db = load_estoque_db()
        venda = {
            'id': len(db.get('vendas', [])) + 1,
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cliente': cliente,
            'itens': itens,
            'valor_bruto': valor_bruto,
            'desconto': desconto,
            'valor_total': valor_total,
            'custo_total': custo_total,
            'lucro': lucro,
            'observacao': observacao
        }
        
        if 'vendas' not in db:
            db['vendas'] = []
        db['vendas'].append(venda)
        save_estoque_db(db)
        
        # Gera lançamento financeiro de receita (contas a receber)
        descricao_fin = f"Venda #{venda['id']}"
        if cliente:
            descricao_fin += f" - {cliente}"
        
        gerar_lancamento_financeiro('receber', valor_total, descricao_fin, 'Venda de Produtos')
        
        flash(f'Venda registrada com sucesso! Total: R$ {valor_total:.2f}', 'success')
        return redirect(url_for('listar_vendas'))
    
    return render_template('estoque/form_venda.html')

@app.route('/vendas/detalhes/<int:venda_id>')
def detalhes_venda(venda_id):
    """Mostra detalhes de uma venda"""
    db = load_estoque_db()
    venda = next((v for v in db.get('vendas', []) if v['id'] == venda_id), None)
    
    if not venda:
        flash('Venda não encontrada!', 'error')
        return redirect(url_for('listar_vendas'))
    
    return render_template('estoque/detalhes_venda.html', venda=venda)

# ============== ROTAS DE API (AJAX) ==============

@app.route('/api/produto/<codigo_barras>')
def api_buscar_produto(codigo_barras):
    """API para buscar produto por código de barras"""
    produto = buscar_produto_por_codigo(codigo_barras)
    if produto:
        return jsonify({
            'success': True,
            'produto': produto
        })
    return jsonify({
        'success': False,
        'message': 'Produto não encontrado'
    })

@app.route('/api/produtos/buscar')
def api_buscar_produtos():
    """API para buscar produtos por nome ou código"""
    termo = request.args.get('termo', '')
    produtos = load_produtos()
    
    if termo:
        produtos = [p for p in produtos if termo.lower() in p['nome'].lower() or termo in p['codigo_barras']]
    
    return jsonify({
        'success': True,
        'produtos': produtos[:10]  # Limita a 10 resultados
    })

# ============== RELATÓRIOS ==============

@app.route('/relatorios')
def relatorios():
    """Página de relatórios"""
    return render_template('estoque/relatorios.html')

@app.route('/relatorios/movimentacao')
def relatorio_movimentacao():
    """Relatório de movimentação de estoque"""
    db = load_estoque_db()
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    vendas = db.get('vendas', [])
    compras = db.get('compras', [])
    ajustes = db.get('ajustes', [])
    
    if data_inicio:
        vendas = [v for v in vendas if v['data'][:10] >= data_inicio]
        compras = [c for c in compras if c['data'][:10] >= data_inicio]
        ajustes = [a for a in ajustes if a['data'][:10] >= data_inicio]
    
    if data_fim:
        vendas = [v for v in vendas if v['data'][:10] <= data_fim]
        compras = [c for c in compras if c['data'][:10] <= data_fim]
        ajustes = [a for a in ajustes if a['data'][:10] <= data_fim]
    
    total_vendas = sum(v['valor_total'] for v in vendas)
    total_compras = sum(c['valor_total'] for c in compras)
    total_lucro = sum(v.get('lucro', 0) for v in vendas)
    
    return render_template('estoque/relatorio_movimentacao.html',
                          vendas=vendas,
                          compras=compras,
                          ajustes=ajustes,
                          total_vendas=total_vendas,
                          total_compras=total_compras,
                          total_lucro=total_lucro,
                          data_inicio=data_inicio,
                          data_fim=data_fim)

# ============== INICIALIZAÇÃO ==============

def init_app():
    """Inicializa os arquivos necessários"""
    init_produtos_csv()
    init_estoque_db()
    
    # Verifica e adiciona categorias financeiras se necessário
    try:
        db = load_financeiro_db()
        categorias_existentes = [c['nome'] for c in db.get('categories', [])]
        
        novas_categorias = [
            {"nome": "Compra de Produtos", "tipo": "despesa"},
            {"nome": "Venda de Produtos", "tipo": "receita"}
        ]
        
        for cat in novas_categorias:
            if cat['nome'] not in categorias_existentes:
                db['categories'].append(cat)
        
        save_financeiro_db(db)
    except:
        pass  # Se o arquivo financeiro não existir, ignora

if __name__ == '__main__':
    init_app()
    app.run(debug=True, port=5001)
