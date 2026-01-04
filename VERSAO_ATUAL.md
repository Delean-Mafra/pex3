# Notas da Versão – Sistema Integrado PEX III

## 1. Visão Geral
Esta versão consolida todo o ecossistema desenvolvido para o Projeto de Extensão III (Ciência de Dados), entregando um pacote único com autenticação centralizada, módulos financeiros e de estoque integrados, documentação completa e processo de distribuição assinado digitalmente.

## 2. Principais Componentes
- **Autenticação (porta 5002)**: Login protegido por SHA256, sessões seguras, alteração de senha, dashboard com acesso aos módulos e instruções em `INSTRUCOES_LOGIN.md`/`CHANGELOG_LOGIN.md`.
- **Sistema Financeiro (porta 5000)**: Dashboard de receitas/despesas, lançamentos (receber/pagar), categorias, formas de pagamento, relatórios analíticos (Chart.js) e filtros por período, persistidos em `database.json`.
- **Sistema de Estoque (porta 5001)**: Cadastro de produtos (CSV), compras, vendas, ajustes, relatórios detalhados e integração lógica com o financeiro para manter consistência dos dados.
- **Relatório Web (`index.html`)**: Documento interativo de apresentação do projeto com descrição completa das etapas, resultados e bibliografia.
- **Geração Word (`gerar_relatorio_word.py`)**: Produz relatório em conformidade com a NBR-15287:2025 automaticamente.

## 3. Tecnologias e Bibliotecas
- **Backend**: Python 3.12, Flask, Werkzeug, Click, Itsdangerous, MarkupSafe, threading/subprocess para orquestração.
- **Frontend**: HTML5, CSS3, JavaScript ES6, Bootstrap 5.3, Bootstrap Icons, Chart.js, animações CSS personalizadas.
- **Persistência**: JSON (`database.json`, `estoque_db.json`), CSV (`produtos.csv`), arquivos auxiliares `.enc` para credenciais.
- **Automação/Build**: PyInstaller (via `version_compilador.py`), scripts de limpeza/distribuição (`preparar_distribuicao.py`), assinatura digital pelo `signtool` (certificado PFX com senha 123456Ab) e fallback para `osslsigncode`.
- **Documentação**: python-docx (relatório NBR), README.md, GUIA_COMPILACAO.md, Relatório HTML e PDF, versão textual em `relatorio_extensao.md`.

## 4. Estrutura e Persistência
- Diretório `templates/` inclui interfaces dos dois módulos (financeiro + estoque) e é empacotado no executável.
- Arquivos de dados ficam ao lado do EXE para permitir atualização do usuário final.
- Credenciais ficam em `credentials.enc`; a exclusão do arquivo restaura o login padrão (admin/admin).

## 5. Distribuição e Assinatura
- `version_compilador.py` incrementa `version.txt`, executa PyInstaller (modo onefile, debug opcional) e embute templates.
- Após o build, o binário `SistemaIntegrado_PEXIII.exe` é assinado automaticamente via `signtool /a /fd SHA256 /tr http://timestamp.digicert.com /td SHA256` usando `certificado-code-signing.pfx`.
- `preparar_distribuicao.py` copia bases JSON/CSV para `dist/` e gera instruções para o usuário final.

## 6. Funcionalidades Notáveis
1. Fluxo único de login que inicializa e monitora os três servidores internos.
2. Integração lógica entre estoque e financeiro (compras/ventas impactam o caixa).
3. Dashboards analíticos responsivos com múltiplas visualizações Chart.js.
4. Ferramentas de documentação automatizadas (HTML + DOCX em padrão ABNT).
5. Processo de distribuição reproduzível, versionado e com assinatura digital.

## 7. Execução e Portas
| Porta | Serviço   | Descrição                         |
|-------|-----------|-----------------------------------|
| 5002  | Login     | Autenticação, dashboard e senha   |
| 5000  | Financeiro| Dashboard, lançamentos, analytics |
| 5001  | Estoque   | Produtos, compras/vendas, reports |

### Passos rápidos
```powershell
# Executar modo desenvolvimento
python "PEX III.py"

# Gerar executável assinado
$env:PEX3_PFX_PASSWORD=''
python version_compilador.py
```

## 8. Próximos Passos Sugeridos
1. Implementar multiusuários e níveis de permissão.
2. Criar logs de auditoria e timeout automático de sessão.
3. Expandir integração financeira para lançar movimentos diretamente no módulo financeiro a partir do estoque.
4. Adicionar testes automatizados para os endpoints críticos dos dois módulos.

---
**Ano**: 2026  
**Autor**: Delean Mafra  
**DOI**: [https://doi.org/10.5281/zenodo.18122476](https://doi.org/10.5281/zenodo.18122476)  
**Licença**: CC BY-NC 4.0
