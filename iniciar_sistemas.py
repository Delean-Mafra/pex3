"""
Script para iniciar ambos os sistemas simultaneamente:
- Sistema Financeiro (porta 5000)
- Sistema de Estoque (porta 5001)
"""

import subprocess
import sys
import os
import time
import webbrowser

def main():
    print("=" * 50)
    print("🚀 Iniciando os Sistemas...")
    print("=" * 50)
    
    # Diretório atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Inicia o Sistema Financeiro (porta 5000)
    print("\n💰 Iniciando Sistema Financeiro na porta 5000...")
    financeiro = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, "financeiro.py")],
        cwd=current_dir
    )
    
    # Aguarda um pouco
    time.sleep(2)
    
    # Inicia o Sistema de Estoque (porta 5001)
    print("📦 Iniciando Sistema de Estoque na porta 5001...")
    estoque = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, "estoque.py")],
        cwd=current_dir
    )
    
    print("\n" + "=" * 50)
    print("✅ Sistemas iniciados com sucesso!")
    print("=" * 50)
    print("\n📍 Acesse:")
    print("   💰 Sistema Financeiro: http://127.0.0.1:5000")
    print("   📦 Sistema de Estoque:  http://127.0.0.1:5001")
    print("\n⚠️  Pressione Ctrl+C para encerrar ambos os sistemas.")
    print("=" * 50)
    
    # Abre o navegador (opcional)
    time.sleep(1)
    try:
        webbrowser.open("http://127.0.0.1:5000")
    except:
        pass
    
    try:
        # Mantém o script rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando os sistemas...")
        financeiro.terminate()
        estoque.terminate()
        print("✅ Sistemas encerrados.")

if __name__ == "__main__":
    main()
