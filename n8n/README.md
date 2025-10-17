# Workflows N8N - Brazyl

## Estrutura

Este diretório contém os workflows do N8N para automação do Brazyl.

## Workflows Disponíveis

### 01-webhook-receiver.json
Recebe mensagens do WhatsApp via Avisa API e roteia para outros workflows.

### 02-cadastro-usuario.json
Fluxo de cadastro de novos usuários via WhatsApp.

### 03-menu-principal.json
Menu interativo principal do WhatsApp bot.

### 04-buscar-politicos.json
Permite usuários buscarem e pesquisarem políticos.

### 05-seguir-politico.json
Gerencia o follow/unfollow de políticos.

### 06-cron-votacoes.json
Cron job que busca votações recentes e cria notificações.

### 07-cron-notificacoes.json
Cron job que processa e envia notificações pendentes.

## Como Importar

1. Acesse o N8N: http://localhost:5678 (desenvolvimento) ou https://n8n.brazyl.com (produção)

2. Faça login com as credenciais configuradas

3. Vá em "Workflows" > "Import from File"

4. Selecione o arquivo JSON do workflow

5. Configure as credenciais necessárias:
   - **Supabase**: URL e Service Key
   - **FastAPI**: URL da API Brazyl e API Key
   - **Avisa API**: Token de autenticação

6. Ative o workflow

## Credenciais Necessárias

### Supabase
- Nome: `Brazyl Supabase`
- Type: HTTP Request Auth
- URL: `https://your-project.supabase.co`
- Headers:
  - `apikey`: Supabase anon key
  - `Authorization`: Bearer {service_key}

### FastAPI Internal
- Nome: `Brazyl API`
- Type: HTTP Request Auth
- URL: `https://api.brazyl.com` (ou `http://api:8000` local)
- Headers:
  - `X-API-Key`: API Key configurada no .env

### Avisa API
- Nome: `Avisa WhatsApp`
- Type: HTTP Request Auth
- URL: `https://api.avisa.com.br`
- Headers:
  - `Authorization`: Bearer {token}

## Testes

Após importar e configurar:

1. **Webhook Receiver**: Envie uma mensagem de teste para o número do WhatsApp configurado

2. **Cadastro**: Envie "oi" ou "olá" para iniciar o cadastro

3. **Menu**: Após cadastrado, envie "menu" para ver o menu principal

4. **Cron Jobs**: Execute manualmente clicando em "Execute Workflow"

## Estrutura dos Workflows

### Webhook Receiver
```
WhatsApp Message → Parse → Identificar Usuário → Router → Workflows específicos
```

### Cadastro
```
Start → Perguntar Nome → Perguntar Email → Criar Usuário → Mensagem Boas-vindas
```

### Menu Principal
```
Start → Mostrar Opções → Wait for Reply → Router para ações
```

### Buscar Políticos
```
Start → Perguntar Filtros → Buscar API → Formatar Resultados → Enviar WhatsApp
```

### Seguir Político
```
Start → Validar Limites → Criar Follow → Confirmar → Enviar WhatsApp
```

### Cron Votações
```
Trigger (6h) → Buscar APIs → Identificar Seguidos → Criar Notificações
```

### Cron Notificações
```
Trigger (8h) → Buscar Pendentes → Formatar → Enviar Avisa API → Atualizar Status
```

## Monitoramento

### Ver Execuções
- N8N > Workflows > [Workflow] > "Executions"

### Logs
- Cada nó tem logs detalhados
- Executões falhadas são destacadas em vermelho

### Alertas
- Configurar webhooks para notificações de falha
- Integrar com Slack ou email para alertas

## Troubleshooting

### Webhook não recebe mensagens
- Verificar URL do webhook na Avisa API
- Testar com curl: `curl -X POST {webhook_url} -d '{"test": true}'`

### Credenciais inválidas
- Reconfigurar credenciais no N8N
- Verificar se tokens não expiraram

### Workflow travado
- Verificar se há "Wait" nodes esperando resposta
- Limpar execuções antigas

### Erros de timeout
- Aumentar timeout nas configurações do nó HTTP Request
- Verificar conectividade com APIs externas

## Boas Práticas

1. **Versionamento**: Sempre fazer backup antes de modificar workflows

2. **Testes**: Testar workflows em ambiente de staging primeiro

3. **Logs**: Adicionar nós "Set" para logging intermediário

4. **Error Handling**: Usar nós "Error Trigger" para capturar falhas

5. **Performance**: Otimizar queries e usar cache quando possível

6. **Segurança**: Nunca fazer commit de workflows com credenciais hardcoded

