# 🔐 Sistema de Autenticação - Instruções de Uso

## 📋 Visão Geral

O sistema agora possui autenticação integrada que protege o acesso aos sistemas Financeiro e de Estoque.

## 🚀 Como Iniciar

1. Execute o arquivo `iniciar_sistemas.py`
2. O navegador abrirá automaticamente na página de login: http://127.0.0.1:5002
3. Use as credenciais padrão na primeira execução

## 🔑 Credenciais Padrão

- **Usuário:** `admin`
- **Senha:** `admin`

⚠️ **IMPORTANTE:** Altere a senha no primeiro acesso por questões de segurança!

## 📂 Estrutura do Sistema

```
Porta 5002 - Sistema de Login (principal)
   ├── Página de Login
   ├── Dashboard (após autenticação)
   └── Alterar Senha
   
Porta 5000 - Sistema Financeiro
   └── (Iniciado automaticamente após login)
   
Porta 5001 - Sistema de Estoque
   └── (Iniciado automaticamente após login)
```

## 🔒 Segurança

### Arquivo de Credenciais

- As credenciais são armazenadas no arquivo `credentials.enc`
- A senha é criptografada usando hash SHA256
- **Nunca compartilhe este arquivo**

### Alterando a Senha

1. Faça login no sistema
2. No Dashboard, clique em **"Alterar Senha"**
3. Digite:
   - Senha atual
   - Nova senha (mínimo 4 caracteres)
   - Confirmação da nova senha
4. Clique em **"Alterar Senha"**

## 📱 Funcionalidades

### Dashboard

Após fazer login, você terá acesso ao Dashboard com:
- Informação do usuário logado
- Botão para alterar senha
- Links diretos para os sistemas Financeiro e de Estoque
- Botão de logout

### Logout

- Clique no botão **"Sair"** no Dashboard
- Isso encerrará sua sessão (mas os sistemas continuarão rodando em segundo plano)
- Para encerrar todos os sistemas, pressione **Ctrl+C** no terminal

## 🛠️ Solução de Problemas

### Esqueci a Senha

Se você esqueceu a senha:

1. Feche o sistema (Ctrl+C no terminal)
2. Delete o arquivo `credentials.enc`
3. Inicie o sistema novamente
4. As credenciais padrão (`admin/admin`) serão recriadas

### Erro ao Iniciar

Se houver erro ao iniciar os sistemas:

1. Verifique se as portas 5000, 5001 e 5002 estão disponíveis
2. Feche outros programas que possam estar usando essas portas
3. Tente novamente

### Sistema não Abre no Navegador

Se o navegador não abrir automaticamente:

- Abra manualmente: http://127.0.0.1:5002

## 💻 Comandos Úteis

### Iniciar Sistema
```bash
python iniciar_sistemas.py
```

### Parar Sistema
Pressione `Ctrl+C` no terminal onde o sistema está rodando

## 📝 Notas Importantes

1. **Não perca sua senha** - Guarde-a em local seguro
2. **Backup do arquivo credentials.enc** - Faça backup regularmente
3. **Senha forte** - Use senhas com letras, números e caracteres especiais
4. **Logout sempre** - Faça logout ao terminar de usar o sistema

## 🆘 Suporte

Para mais informações ou suporte:
- Email: [seu-email]
- GitHub: [seu-repositorio]

---

**Copyright © Delean Mafra - Todos os direitos reservados | Licença: CC BY-NC 4.0**
