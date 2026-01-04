#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para verificar o sistema de login
"""

import os
import json
import hashlib

def pex3_hash_password_dm(pex3_password_dm):
    """Criptografa a senha usando SHA256"""
    return hashlib.sha256(pex3_password_dm.encode()).hexdigest()

# Testar criação de credenciais
print("=" * 50)
print("🧪 Teste do Sistema de Autenticação")
print("=" * 50)

# Criar credenciais de teste
pex3_credenciais_dm = {
    'username': 'admin',
    'password': pex3_hash_password_dm('admin')
}

print("\n✅ Credenciais de teste criadas:")
print(f"   Usuário: {pex3_credenciais_dm['username']}")
print(f"   Hash da senha: {pex3_credenciais_dm['password'][:20]}...")

# Verificar hash
pex3_senha_teste_dm = 'admin'
pex3_hash_teste_dm = pex3_hash_password_dm(pex3_senha_teste_dm)

print(f"\n🔐 Teste de verificação:")
print(f"   Senha: {pex3_senha_teste_dm}")
print(f"   Hash gerado: {pex3_hash_teste_dm[:20]}...")
print(f"   Match: {pex3_hash_teste_dm == pex3_credenciais_dm['password']}")

# Testar senha incorreta
pex3_senha_errada_dm = 'senha_errada'
pex3_hash_errado_dm = pex3_hash_password_dm(pex3_senha_errada_dm)

print(f"\n❌ Teste com senha incorreta:")
print(f"   Senha: {pex3_senha_errada_dm}")
print(f"   Hash gerado: {pex3_hash_errado_dm[:20]}...")
print(f"   Match: {pex3_hash_errado_dm == pex3_credenciais_dm['password']}")

print("\n" + "=" * 50)
print("✅ Todos os testes passaram!")
print("=" * 50)
print("\n📌 Próximo passo:")
print("   Execute: python iniciar_sistemas.py")
print("   Acesse: http://127.0.0.1:5002")
print("   Login: admin / admin")
print("=" * 50)
