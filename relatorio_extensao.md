# Relatório de Projeto de Extensão III
## Análise da Situação - Ciência de Dados

**Centro Universitário União das Américas Descomplica**  
**Curso de Tecnologia em Ciência de Dados**  
**Ano 2026**

---

## 1. Introdução e Apresentação

Iniciei meu projeto preenchendo a **CARTA DE APRESENTAÇÃO** e escolhi a organização **Mercado Dal- Bo Ltda** para visitar e me apresentar. Após a autorização da organização, com o preenchimento do **TERMO DE AUTORIZAÇÃO PARA REALIZAÇÃO DAS ATIVIDADES EXTENSIONISTAS**, dei início ao projeto.

### Sobre o Projeto

Este projeto de extensão me proporcionou a oportunidade de me envolver diretamente com o uso de dados para resolver problemas reais enfrentados pela organização parceira. O foco foi na coleta, análise e interpretação de dados, visando a tomada de decisões mais informada e eficiente.

### Objetivos do Projeto

- Realizar uma análise detalhada dos problemas e necessidades da instituição
- Identificar questões que possam ser abordadas com técnicas de ciência de dados
- Aplicar modelagem preditiva, visualização e análise de dados
- Propor intervenções baseadas em insights provenientes da análise
- Conectar teoria e prática através de soluções com impacto positivo

---

## 2. Análise Crítica da Situação-Problema

### 2.1 Identificação dos Problemas

Identifiquei e documentei os seguintes problemas na instituição, com foco na análise de dados:

#### Problema 1: Falta de Controle Financeiro

A organização não possuía um sistema adequado para gerenciar suas finanças. Os registros de receitas e despesas eram feitos de forma manual ou em planilhas desorganizadas, dificultando a visualização do fluxo de caixa e a tomada de decisões financeiras.

**Impactos identificados:**
- Ausência de categorização de gastos
- Dificuldade em identificar padrões de despesas
- Impossibilidade de gerar relatórios analíticos
- Falta de visibilidade sobre a saúde financeira

#### Problema 2: Gestão de Estoque Ineficiente

O controle de estoque era precário, resultando em perdas por falta de produtos ou excesso de itens parados. Não havia registro adequado de compras e vendas, nem integração com o controle financeiro.

**Impactos identificados:**
- Desconhecimento do saldo real de produtos
- Falta de histórico de movimentações
- Ausência de alertas para estoque baixo
- Dificuldade em calcular lucro por produto

### 2.2 Aplicação de Técnicas de Análise

Apliquei técnicas de análise exploratória de dados para compreender a fundo as questões identificadas:

1. **Coleta de Dados:** Coletei informações sobre as transações financeiras, movimentações de estoque, produtos comercializados e fluxo de caixa histórico da organização.

2. **Análise Exploratória:** Realizei análise exploratória para identificar padrões de gastos, sazonalidade nas vendas e produtos com maior rotatividade.

3. **Identificação de Padrões:** Identifiquei padrões de comportamento nos dados que indicavam oportunidades de melhoria nos processos.

---

## 3. Identificação dos Fatores-Chave e Solução

### 3.1 Fatores Críticos Identificados

Identifiquei as variáveis e fatores críticos que influenciam os problemas, utilizando metodologias de análise:

| Fator | Impacto | Solução Proposta |
|-------|---------|------------------|
| Registro manual de transações | Alto - Erros e perda de dados | Sistema digital automatizado |
| Falta de categorização | Médio - Análise prejudicada | Categorias personalizáveis |
| Ausência de relatórios | Alto - Decisões sem dados | Dashboard analítico |
| Estoque descontrolado | Alto - Perdas financeiras | Sistema de gestão integrado |
| Sem integração financeira | Médio - Visão fragmentada | Integração automática |

### 3.2 Solução Desenvolvida

Desenvolvi um sistema integrado composto por dois módulos principais que se comunicam entre si:

#### 💰 Sistema Financeiro (Porta 5000)

Sistema completo para gestão financeira com:
- Dashboard com visão geral de receitas e despesas
- Cadastro de lançamentos (contas a pagar/receber)
- Categorização personalizável
- Filtros por período
- Relatórios analíticos
- Formas de pagamento configuráveis

**Acesso:** http://127.0.0.1:5000

#### 📦 Sistema de Estoque (Porta 5001)

Sistema completo para controle de estoque com:
- Cadastro de produtos com código de barras
- Controle de compras e vendas
- Ajuste de estoque por inventário
- Cálculo automático de lucro
- Alertas de estoque baixo
- Integração com sistema financeiro

**Acesso:** http://127.0.0.1:5001

### 3.3 Integração Entre Sistemas

A principal inovação é a **integração automática** entre os sistemas. Quando uma compra é registrada no sistema de estoque, automaticamente é gerado um lançamento de despesa no sistema financeiro. Da mesma forma, quando uma venda é realizada, é gerado um lançamento de receita (contas a receber). Isso garante consistência dos dados e visão unificada da saúde financeira do negócio.

---

## 4. Tecnologias e Arquitetura

### 4.1 Stack Tecnológico

- **Python 3.x** - Linguagem de programação principal
- **Flask** - Framework web para backend
- **HTML5/CSS3/JavaScript** - Frontend
- **Bootstrap 5** - Framework CSS responsivo
- **JSON** - Banco de dados de transações
- **CSV** - Banco de dados de produtos

### 4.2 Estrutura do Projeto

```
pex3/
├── financeiro.py          # Sistema Financeiro (Flask)
├── estoque.py             # Sistema de Estoque (Flask)
├── iniciar_sistemas.py    # Script para iniciar ambos
├── database.json          # Banco de dados financeiro
├── estoque_db.json        # Banco de dados de movimentações
├── produtos.csv           # Cadastro de produtos
├── templates/
│   ├── base.html              # Template base financeiro
│   ├── index.html             # Dashboard financeiro
│   ├── lancamentos.html       # Lista de lançamentos
│   ├── form_lancamento.html   # Formulário de lançamento
│   ├── categorias.html        # Gestão de categorias
│   ├── analytics.html         # Relatórios analíticos
│   └── estoque/
│       ├── base_estoque.html  # Template base estoque
│       ├── index.html         # Dashboard estoque
│       ├── produtos.html      # Lista de produtos
│       ├── form_produto.html  # Cadastro de produto
│       ├── compras.html       # Lista de compras
│       ├── form_compra.html   # Nova compra
│       ├── vendas.html        # Lista de vendas
│       ├── form_venda.html    # Nova venda
│       └── relatorios.html    # Relatórios
```

### 4.3 Modelo de Dados

#### database.json (Financeiro)

```json
{
  "transactions": [
    {
      "id": 1,
      "tipo": "receber",
      "data_gasto": "2025-12-30",
      "valor": 200.0,
      "categoria": "Venda",
      "forma_pagamento": "PIX",
      "descricao": "..."
    }
  ],
  "categories": [...],
  "payment_methods": [...]
}
```

#### produtos.csv (Estoque)

```csv
codigo_barras;nome;saldo;preco_venda;preco_compra
7891234567890;Arroz;50;12.90;8.50
7891234567891;Feijão;30;9.90;6.20
```

---

## 5. Competências Desenvolvidas

### 5.1 Competências Técnicas

#### Análise de Dados e Estatística
Desenvolvi a capacidade de compreender, interpretar e manipular dados em diferentes contextos, aplicando técnicas estatísticas para extrair insights relevantes.

#### Modelagem e Algoritmos
Adquiri competência em criar modelos de dados e estruturas algorítmicas para resolver problemas específicos de negócio.

#### Visualização de Dados
Desenvolvi habilidade para comunicar insights de forma visual e acessível, por meio de dashboards e relatórios interativos.

#### Ferramentas de Ciência de Dados
Obtive conhecimento prático em Python, Flask, JSON, CSV e bibliotecas para desenvolvimento de aplicações orientadas a dados.

### 5.2 Soft Skills Desenvolvidas

| Soft Skill | Descrição |
|------------|-----------|
| **Pensamento Analítico** | Desenvolvi habilidade para compreender problemas complexos e propor soluções baseadas em dados e evidências. |
| **Trabalho em Equipe** | Exercitei a capacidade de colaborar com membros da organização para entender suas necessidades de dados. |
| **Iniciativa e Autonomia** | Demonstrei proatividade e independência na coleta, análise de dados e desenvolvimento da solução. |
| **Comunicação Eficaz** | Aprimorei a competência em transmitir insights de dados de maneira clara e compreensível para não-técnicos. |
| **Flexibilidade** | Desenvolvi habilidade para me ajustar a diferentes ferramentas, contextos e requisitos durante o projeto. |
| **Responsabilidade Ética** | Mantive compromisso com o uso responsável de dados, respeitando privacidade e boas práticas. |

---

## 6. Temas Envolvidos no Projeto

### Exploração e Limpeza de Dados
Apliquei técnicas para organizar, limpar e preparar dados para análise, garantindo a qualidade das informações processadas pelo sistema.

### Visualização de Dados
Utilizei ferramentas e técnicas para criar visualizações eficazes que comunicam resultados de forma clara nos dashboards.

### Estatística Aplicada
Empreguei conceitos estatísticos para interpretar dados financeiros e de estoque, apoiando a tomada de decisão.

### Análise de Dados para Negócios
Desenvolvi soluções de análise de dados para otimização de processos e suporte a decisões estratégicas da organização.

---

## 7. Resultados e Conclusão

### 7.1 Resultados Alcançados

**Entregas do Projeto:**

- ✅ **Sistema Financeiro Completo:** Aplicação web funcional para gestão de finanças
- ✅ **Sistema de Estoque Integrado:** Controle completo de produtos, compras e vendas
- ✅ **Integração Automática:** Comunicação entre sistemas para consistência de dados
- ✅ **Dashboards Analíticos:** Visualizações para tomada de decisão
- ✅ **Documentação:** Código comentado e relatório detalhado

### 7.2 Benefícios para a Organização

| Antes | Depois |
|-------|--------|
| Controle manual em planilhas | Sistema digital automatizado |
| Dados dispersos e inconsistentes | Base de dados centralizada e integrada |
| Sem visibilidade financeira | Dashboard com visão em tempo real |
| Estoque descontrolado | Controle preciso com alertas |
| Decisões sem dados | Decisões baseadas em dados |

### 7.3 Conclusão

Este projeto de extensão me permitiu aplicar na prática os conhecimentos adquiridos no curso de Ciência de Dados, desenvolvendo uma solução real que traz impacto positivo para a organização parceira. A experiência de identificar problemas, analisar dados e propor soluções baseadas em evidências foi fundamental para meu desenvolvimento profissional.

O sistema desenvolvido resolve problemas concretos de gestão financeira e controle de estoque, automatizando processos que antes eram manuais e propensos a erros. A integração entre os módulos garante consistência dos dados e oferece uma visão unificada da saúde do negócio.

---

**Centro Universitário União das Américas Descomplica**  
**Curso de Tecnologia em Ciência de Dados**  
**Projeto de Extensão III - Análise da Situação**  
**Ano: 2026**  

**DOI:** [https://doi.org/10.5281/zenodo.18143148](https://doi.org/10.5281/zenodo.18143148)

**Copyright © Delean Mafra - Todos os direitos reservados | Licença: CC BY-NC 4.0**
