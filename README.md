# Projeto de Extensão III - Ciência de Dados

## 💼 Visão Geral

Este repositório documenta o **Projeto de Extensão III** do curso de Tecnologia em Ciência de Dados (CST - UniAmérica Descomplica), desenvolvido no **3º semestre**. O projeto consiste na aplicação prática de técnicas de ciência de dados para resolver problemas reais enfrentados por uma organização parceira.

---

## 🎯 Objetivo Geral do Projeto

Aplicar técnicas de **análise, modelagem e visualização de dados** para identificar e resolver problemas reais em uma organização parceira, gerando impacto positivo através de soluções baseadas em dados e inteligência analítica.

---

## 🏢 A Organização Parceira

O projeto foi desenvolvido em parceria com uma **empresa de varejo/comércio** que enfrentava dificuldades significativas na gestão de suas despesas operacionais.

### 🔍 Problema Identificado

A organização utilizava **planilhas eletrônicas (Excel)** para registrar e controlar todas as suas despesas. Este método apresentava diversos problemas:

- ❌ **Falta de padronização** nos registros
- ❌ **Cálculos manuais** propensos a erros
- ❌ **Dificuldade em identificar padrões** de gastos
- ❌ **Análise temporal deficiente** 
- ❌ **Falta de visualizações** para tomada de decisão
- ❌ **Impossibilidade de consultas rápidas** e cruzamento de dados

---

## 💡 Solução Proposta: Financeiro Pro

Como resposta aos problemas identificados, foi desenvolvido o **Financeiro Pro** - uma aplicação web intuitiva para gestão de despesas e receitas com análise visual de dados.

### ✨ Funcionalidades Principais

#### 1. **Dashboard Resumido**
   - Visualização rápida de receitas totais, despesas totais e saldo
   - Filtro por período (data inicial e data final)
   - Cartões informativos com status de saldo (positivo/negativo)

#### 2. **Lançamento de Transações**
   - Interface intuitiva para registrar receitas e despesas
   - Campos estruturados:
     - Data da transação
     - Valor
     - Categoria (filtrada conforme o tipo)
     - Forma de pagamento (PIX, Cartão, Dinheiro, Outros)
     - Descrição/observação
   - Validação automática de dados

#### 3. **Gestão de Categorias**
   - Criação de categorias personalizadas
   - Classificação por tipo (receita, despesa ou ambos)
   - Categoria de origem consultável em lançamentos

#### 4. **Visualização de Lançamentos**
   - Tabela completa com histórico de todas as transações
   - Ordenação e filtro para análise detalhada
   - Informações de data de lançamento e criação

#### 5. **Dashboard Analytics Avançado**
   - **Gráfico 1:** Gasto por Categoria (Barras)
   - **Gráfico 2:** Receita vs Despesa Mensal (Barras lado a lado)
   - **Gráfico 3:** Evolução do Saldo Acumulado (Linha)
   - **Gráfico 4:** Receita por Forma de Pagamento (Pizza)
   - **Gráfico 5:** Gastos Mensais Detalhados por Categoria (Barras agrupadas)

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.x**
- **Flask** - Framework web
- **JSON** - Armazenamento de dados

### Frontend
- **HTML5** - Estrutura
- **Bootstrap 5.3** - Design responsivo
- **Chart.js** - Visualização de gráficos
- **Jinja2** - Templating

### Ferramentas
- **Git/GitHub** - Controle de versão
- **VSCode** - Ambiente de desenvolvimento

---

## 📁 Estrutura do Projeto

```
pex3/
├── financeiro.py              # Backend Flask principal
├── database.json              # Base de dados JSON
├── README.md                  # Este arquivo
├── LICENSE.md                 # Informações de licença
├── templates/
│   ├── base.html             # Template base (herança)
│   ├── index.html            # Dashboard resumido
│   ├── form_lancamento.html  # Formulário de transações
│   ├── lancamentos.html      # Visualização de histórico
│   ├── categorias.html       # Gestão de categorias
│   ├── analytics.html        # Dashboard com gráficos
│   └── ...
└── database.json             # Banco de dados
```

---

## 🚀 Como Usar

### Pré-requisitos
- Python 3.7+
- Flask (`pip install flask`)

### Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd pex3

# Instale as dependências
pip install flask

# Execute a aplicação
python financeiro.py
```

A aplicação estará disponível em `http://localhost:5000`

---

## 📊 Análises Realizadas

### Exploração de Dados
- Identificação de padrões de gasto por categoria
- Análise de distribuição de formas de pagamento
- Evolução temporal de receitas e despesas

### Insights Gerados
- Categorias com maior volume de gastos
- Sazonalidade nos padrões de receita
- Formas de pagamento mais utilizadas
- Tendências de saldo acumulado

### Recomendações Propostas
1. **Monitoramento contínuo** através dos dashboards
2. **Estabelecimento de limites** por categoria
3. **Análise mensal** de padrões de gasto
4. **Otimização de formas de pagamento** conforme frequência de uso

---

## 🎓 Competências Desenvolvidas

### Hard Skills
✅ Análise Exploratória de Dados (EDA)  
✅ Modelagem de Dados  
✅ Programação em Python  
✅ Desenvolvimento Web (Flask)  
✅ Visualização de Dados (Chart.js)  
✅ Design de Interfaces (Bootstrap)  
✅ Banco de Dados (JSON)  

### Soft Skills
✅ Pensamento Analítico e Resolução de Problemas  
✅ Comunicação Efetiva de Resultados  
✅ Trabalho em Equipe  
✅ Iniciativa e Autonomia  
✅ Flexibilidade e Adaptabilidade  
✅ Responsabilidade Ética em Dados  

---

## 📝 Documentação Complementar

- 📄 **Carta de Apresentação** - Formalização da parceria
- 📋 **Termo de Autorização** - Consentimento da organização
- 📊 **Roteiro de Atividades** - Cronograma do projeto

---

## 👨‍💼 Autor

**Delean P. Mafra**  
Aluno do CST em Ciência de Dados - 3º Semestre  
UniAmérica Descomplica  

---

## 📜 Licença

Este projeto está licenciado sob a **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.

Para mais informações, consulte o arquivo [LICENSE.md](LICENSE.md) ou visite:  
🔗 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.pt-br)

---

## 📞 Contato e Suporte

Para dúvidas, sugestões ou informações sobre o projeto, entre em contato através dos canais fornecidos na instituição.

**Copyright © Delean Mafra - Todos os direitos reservados.**

