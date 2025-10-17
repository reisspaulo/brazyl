# Database Schema - Brazyl

## Estrutura do Banco de Dados

Este diretório contém os scripts SQL para o banco de dados PostgreSQL (Supabase) do projeto Brazyl.

## Arquivos

- `schema.sql` - Schema completo do banco de dados
- `seed_plans.sql` - Dados iniciais dos planos
- `migrations/` - Migrações futuras

## Como Aplicar

### Via Supabase Dashboard

1. Acesse o Supabase Dashboard
2. Vá em "SQL Editor"
3. Cole o conteúdo de `schema.sql`
4. Execute

### Via CLI do Supabase

```bash
supabase db push
```

## Tabelas Principais

### `users`
Usuários do sistema que interagem via WhatsApp.

### `politicians`
Políticos brasileiros (deputados federais, senadores, etc).

### `political_events`
Histórico de ações dos políticos (votações, gastos, projetos).

### `follows`
Relação entre usuários e políticos que eles seguem.

### `notifications`
Notificações enviadas aos usuários via WhatsApp.

### `plans`
Planos de assinatura (FREE, BASIC, PREMIUM).

## Enums

- `plan_type`: FREE, BASIC, PREMIUM
- `political_position`: DEPUTADO_FEDERAL, SENADOR, DEPUTADO_ESTADUAL, VEREADOR
- `event_type`: VOTACAO, DESPESA, PROJETO_LEI, PROPOSTA, DISCURSO
- `notification_status`: PENDING, SENT, DELIVERED, FAILED

