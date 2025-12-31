"""
Script auxiliar para preparar o ambiente de execução do PEX III compilado
Copia apenas os arquivos de banco de dados (CSV e JSON) para a pasta dist
"""

import os
import shutil
from pathlib import Path

def main():
    print("=" * 60)
    print("📦 Preparando Ambiente de Execução - PEX III")
    print("=" * 60)
    
    # Diretórios
    base_dir = Path(__file__).parent
    dist_dir = base_dir / 'dist'
    
    # Verificar se dist existe
    if not dist_dir.exists():
        print("\n❌ Erro: Pasta 'dist' não encontrada!")
        print("   Execute primeiro: python version_compilador.py")
        input("\nPressione Enter para sair...")
        return
    
    # Criar estrutura de dados
    data_dir = dist_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Diretório de destino: {dist_dir}")
    print(f"📁 Diretório de dados: {data_dir}")
    
    # Arquivos a copiar (bancos de dados)
    arquivos_dados = [
        'database.json',
        'estoque_db.json',
        'produtos.csv',
        'credentials.enc'  # Arquivo de credenciais
    ]
    
    # Copiar arquivos de dados
    print("\n📋 Copiando arquivos de banco de dados...")
    copiados = 0
    
    for arquivo in arquivos_dados:
        origem = base_dir / arquivo
        destino = dist_dir / arquivo
        
        if origem.exists():
            try:
                shutil.copy2(origem, destino)
                print(f"   ✅ {arquivo}")
                copiados += 1
            except Exception as e:
                print(f"   ❌ Erro ao copiar {arquivo}: {e}")
        else:
            # Criar arquivo vazio se não existir
            if arquivo == 'credentials.enc':
                print(f"   ⚠️  {arquivo} não encontrado (será criado no primeiro uso)")
            else:
                print(f"   ⚠️  {arquivo} não encontrado (será criado no primeiro uso)")
    
    # Criar arquivo README na pasta dist
    readme_content = """# Sistema Integrado - PEX III

## 🚀 Como Executar

1. Execute o arquivo: `Sistema Integrado - PEX III.exe`
2. O navegador abrirá automaticamente em: http://127.0.0.1:5002
3. Use as credenciais padrão na primeira execução:
   - Usuário: admin
   - Senha: admin

## 📂 Arquivos do Sistema

### Executável Principal
- `Sistema Integrado - PEX III.exe` - Aplicação principal

### Bancos de Dados (não deletar!)
- `database.json` - Dados financeiros (lançamentos, categorias, formas de pagamento)
- `estoque_db.json` - Movimentações de estoque (compras, vendas, ajustes)
- `produtos.csv` - Cadastro de produtos
- `credentials.enc` - Credenciais de login (criptografadas)

## ⚠️ IMPORTANTE

### Backup dos Dados
Faça backup regular dos arquivos de dados (JSON e CSV) para evitar perda de informações.

### Segurança
- Altere a senha padrão no primeiro acesso
- Mantenha o arquivo `credentials.enc` seguro
- Não compartilhe suas credenciais

### Portas Utilizadas
- 5002 - Sistema de Login
- 5000 - Sistema Financeiro
- 5001 - Sistema de Estoque

Certifique-se de que essas portas estão disponíveis antes de executar.

## 🔒 Recuperar Senha

Se esquecer a senha:
1. Feche o sistema
2. Delete o arquivo `credentials.enc`
3. Reinicie o sistema (credenciais padrão serão recriadas)

## 📞 Suporte

Para mais informações, consulte a documentação completa do projeto.

---
**Copyright © Delean Mafra - 2025**
**Licença: CC BY-NC 4.0**
"""
    
    readme_path = dist_dir / 'LEIA-ME.txt'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"\n   ✅ README criado: LEIA-ME.txt")
    
    # Resumo
    print("\n" + "=" * 60)
    print("✅ Preparação Concluída!")
    print("=" * 60)
    print(f"\n📊 Resumo:")
    print(f"   • Arquivos de dados copiados: {copiados}")
    print(f"   • Diretório: {dist_dir}")
    print(f"\n🎯 Próximo passo:")
    print(f"   1. Navegue até: {dist_dir}")
    print(f"   2. Execute: Sistema Integrado - PEX III.exe")
    print("\n" + "=" * 60)
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
