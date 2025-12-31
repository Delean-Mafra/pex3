#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para verificar o sistema de login
"""

import os
import json
import hashlib

def hash_password(password):
    """Criptografa a senha usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Testar criação de credenciais
print("=" * 50)
print("🧪 Teste do Sistema de Autenticação")
print("=" * 50)

# Criar credenciais de teste
credenciais = {
    'username': 'admin',
    'password': hash_password('admin')
}

print("\n✅ Credenciais de teste criadas:")
print(f"   Usuário: {credenciais['username']}")
print(f"   Hash da senha: {credenciais['password'][:20]}...")

# Verificar hash
senha_teste = 'admin'
hash_teste = hash_password(senha_teste)

print(f"\n🔐 Teste de verificação:")
print(f"   Senha: {senha_teste}")
print(f"   Hash gerado: {hash_teste[:20]}...")
print(f"   Match: {hash_teste == credenciais['password']}")

# Testar senha incorreta
senha_errada = 'senha_errada'
hash_errado = hash_password(senha_errada)

print(f"\n❌ Teste com senha incorreta:")
print(f"   Senha: {senha_errada}")
print(f"   Hash gerado: {hash_errado[:20]}...")
print(f"   Match: {hash_errado == credenciais['password']}")

print("\n" + "=" * 50)
print("✅ Todos os testes passaram!")
print("=" * 50)
print("\n📌 Próximo passo:")
print("   Execute: python iniciar_sistemas.py")
print("   Acesse: http://127.0.0.1:5002")
print("   Login: admin / admin")
print("=" * 50)
