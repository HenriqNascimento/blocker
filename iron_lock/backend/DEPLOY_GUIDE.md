# Implementar o IronLock na Nuvem

Você deve fazer o upload da pasta `iron_lock/backend` para o **GitHub** e conectar na **Vercel**.

## 1. Preparar Arquivos
1. Certifique-se de que a pasta `iron_lock/backend` contém `package.json`, `pages`, etc.

## 2. GitHub (Passo a Passo)
1. Crie um **Novo Repositório** no GitHub chamado `iron-lock-server`.
2. No seu computador, abra o terminal na pasta `iron_lock/backend`.
3. Execute:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/iron-lock-server.git
   git push -u origin main
   ```
   *(Se não tiver git instalado ou achar difícil, você pode criar o repositório no site do GitHub e fazer **Upload Files** arrastando os arquivos da pasta backend)*.

## 3. Vercel (Deploy)
1. Crie conta em [vercel.com](https://vercel.com).
2. Clique em **"Add New Project"**.
3. Selecione **"Import from GitHub"** e escolha o repositório `iron-lock-server`.
4. **IMPORTANTE: Variáveis de Ambiente**
   Na tela de configuração do projeto ("Configure Project"), procure a seção **"Environment Variables"** e adicione:

   | NAME | VALUE |
   |------|-------|
   | `SENDGRID_API_KEY` | `SG.PEp3...` (Sua chave completa) |
   | `FROM_EMAIL` | `seu_email@dominio.com` (Email VERIFICADO no SendGrid) |
   | `APP_SECRET` | `UmaSenhaSuperSecretaAleatoria123` (Para criptografar os links) |

5. Clique em **Deploy**.

## 4. Finalizar
1. Após o deploy, a Vercel vai te dar uma URL (ex: `https://iron-lock-server.vercel.app`).
2. Copie essa URL.
3. Agora precisamos atualizar o instalador do Windows para usar essa URL.

**Aguarde minhas instruções para atualizar o instalador.**
