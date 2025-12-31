# 📦 Guia de Compilação - Sistema Integrado PEX III

## 🎯 Visão Geral

Este guia explica como compilar o Sistema Integrado PEX III em um executável standalone (.exe) usando PyInstaller.

## 📋 Pré-requisitos

### 1. Python 3.12+
```bash
python --version
```

### 2. Dependências Instaladas
```bash
pip install flask
pip install pyinstaller
```

### 3. Windows SDK (para assinatura digital - opcional)
- Necessário apenas se quiser assinar o executável
- Download: https://developer.microsoft.com/windows/downloads/windows-sdk/

## 🚀 Processo de Compilação

### Passo 1: Preparar o Ambiente

Certifique-se de estar no diretório correto:
```bash
cd D:\Python\complementos\pex3
```

### Passo 2: Executar o Compilador

```bash
python version_compilador.py
```

O script irá:
1. ✅ Incrementar a versão automaticamente
2. ✅ Limpar arquivos antigos (build, dist)
3. ✅ Executar PyInstaller com todas as dependências
4. ✅ Incluir templates HTML/CSS/JS
5. ✅ Tentar assinar digitalmente (se certificado disponível)

### Passo 3: Preparar Distribuição

Após a compilação bem-sucedida:
```bash
python preparar_distribuicao.py
```

Este script irá:
1. ✅ Copiar arquivos de banco de dados (JSON/CSV) para `dist/`
2. ✅ Criar arquivo LEIA-ME.txt com instruções
3. ✅ Preparar estrutura completa para distribuição

## 📂 Estrutura de Arquivos

### Durante Compilação:
```
pex3/
├── iniciar_sistemas.py          # ← Arquivo principal compilado
├── financeiro.py                 # ← Incluído via imports
├── estoque.py                    # ← Incluído via imports
├── templates/                    # ← Empacotado no .exe
│   ├── *.html
│   └── estoque/*.html
├── version.txt                   # ← Info de versão
├── ico.png                       # ← Ícone do executável
└── version_compilador.py         # ← Script de compilação
```

### Após Compilação (pasta dist/):
```
dist/
├── Sistema Integrado - PEX III.exe   # ← Executável principal
├── database.json                      # ← Banco financeiro
├── estoque_db.json                    # ← Banco estoque
├── produtos.csv                       # ← Cadastro produtos
├── credentials.enc                    # ← Credenciais (se existir)
└── LEIA-ME.txt                        # ← Instruções
```

## 🔧 Configurações Importantes

### Arquivos Incluídos no Executável:
- ✅ Código Python (`.py`)
- ✅ Templates HTML/CSS/JS
- ✅ Bibliotecas Flask
- ✅ Ícone da aplicação

### Arquivos Externos (não compilados):
- ❌ `database.json` - Dados financeiros
- ❌ `estoque_db.json` - Dados de estoque
- ❌ `produtos.csv` - Produtos cadastrados
- ❌ `credentials.enc` - Credenciais de login

**Motivo:** Estes arquivos são o "banco de dados" e precisam ser editáveis pelo usuário.

## ⚙️ Parâmetros do PyInstaller

### Principais Flags Usadas:

```python
--onefile                    # Gera um único arquivo .exe
--name=Sistema Integrado     # Nome do executável
--version-file=version.txt   # Informações de versão
--icon=ico.png              # Ícone da aplicação
--add-data=templates;templates  # Incluir templates HTML
--console                    # Mostrar console (debug)
```

### Hidden Imports (dependências):
```python
--hidden-import=flask
--hidden-import=werkzeug
--hidden-import=jinja2
--hidden-import=hashlib
--hidden-import=json
--hidden-import=csv
```

### Módulos Excluídos (reduzir tamanho):
```python
--exclude-module=matplotlib
--exclude-module=numpy
--exclude-module=pandas
--exclude-module=tkinter
```

## 🐛 Solução de Problemas

### Erro: "No module named 'flask'"
```bash
pip install flask
```

### Erro: "PyInstaller not found"
```bash
pip install pyinstaller
```

### Erro: "Templates não encontrados"
- Verifique se a pasta `templates/` existe
- Certifique-se que o caminho está correto no script

### Executável muito grande (> 100MB)
- Normal para aplicações Flask
- Considere usar UPX para compressão:
```bash
pip install pyinstaller[upx]
```

### Erro ao executar o .exe
1. Execute via terminal para ver erros:
```bash
cd dist
"Sistema Integrado - PEX III.exe"
```

2. Verifique se os arquivos de dados existem
3. Verifique se as portas 5000, 5001, 5002 estão livres

## 📊 Tamanho Esperado

- **Executável:** ~40-60 MB
- **Com dados:** +1-5 MB (dependendo do volume)
- **Total distribuição:** ~50-70 MB

## 🔐 Assinatura Digital (Opcional)

### Requisitos:
1. Certificado de Code Signing (.pfx)
2. Windows SDK instalado
3. Arquivo `certificado-code-signing.pfx` na raiz

### Como Assinar:
O script `version_compilador.py` tenta assinar automaticamente se detectar:
- `signtool.exe` (Windows SDK)
- Arquivo de certificado presente

### Verificar Assinatura:
1. Clique direito no .exe
2. Propriedades > Assinaturas Digitais
3. Deve aparecer informações do certificado

## 📝 Checklist de Compilação

Antes de compilar:
- [ ] Todos os arquivos .py estão salvos
- [ ] Templates estão na pasta correta
- [ ] Ícone (ico.png) está presente
- [ ] version.txt configurado
- [ ] Dependências instaladas

Após compilar:
- [ ] Executável gerado em `dist/`
- [ ] Testar execução
- [ ] Verificar login funciona
- [ ] Verificar sistemas abrem
- [ ] Copiar arquivos de dados
- [ ] Testar com dados reais

## 🚀 Distribuição

### Criar Pacote de Distribuição:

1. **Comprimir pasta dist:**
```bash
# No PowerShell
Compress-Archive -Path dist\* -DestinationPath "Sistema-PEX3-v1.0.zip"
```

2. **Incluir no pacote:**
- ✅ Executável
- ✅ LEIA-ME.txt
- ✅ Arquivos de dados (vazios ou exemplo)
- ✅ Documentação adicional

3. **NÃO incluir:**
- ❌ Pasta build/
- ❌ Arquivos .spec
- ❌ __pycache__/
- ❌ Código fonte

## 🔄 Atualização de Versão

A versão é incrementada automaticamente no `version.txt`:
- Versão atual lida do arquivo
- Último número incrementado (+1)
- Gravado de volta

Formato: `1.0.0.X` onde X é incrementado.

## 📞 Suporte

### Logs de Compilação:
- Salvos automaticamente durante execução
- Verifique mensagens de erro no console

### Problemas Comuns:
1. **Módulo não encontrado:** Adicionar em `--hidden-import`
2. **Arquivo não incluído:** Adicionar em `--add-data`
3. **Erro de importação:** Verificar `--collect-all`

---

## 🎓 Comandos Resumidos

```bash
# 1. Limpar e compilar
python version_compilador.py

# 2. Preparar distribuição
python preparar_distribuicao.py

# 3. Testar executável
cd dist
"Sistema Integrado - PEX III.exe"

# 4. Criar pacote ZIP
Compress-Archive -Path dist\* -DestinationPath SistemaPEX3.zip
```

---

**Copyright © Delean Mafra - 2025**  
**Licença: CC BY-NC 4.0**
