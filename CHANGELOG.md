# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Planejado
- Sistema de pagamentos e planos
- Dashboard web para usuários
- App mobile (Flutter)
- Análise de dados e insights

## [0.1.0] - 2024-01-15

### Adicionado
- API REST completa com FastAPI
- Integração com Supabase (PostgreSQL)
- Integração com Redis para cache
- Cliente para API da Câmara dos Deputados
- Cliente para API do Senado Federal
- Cliente para Portal da Transparência
- Cliente para Avisa API (WhatsApp)
- Services layer com lógica de negócio
- Schemas Pydantic para validação
- Endpoints REST (users, politicians, follows, notifications)
- Script de população de políticos
- Scripts de teste para integrações
- Dockerfile otimizado
- Docker Compose para desenvolvimento
- Docker Stack para produção
- Workflows base do N8N
- Documentação completa da API
- Guia de contribuição
- Guia de deploy

### Estrutura de Banco de Dados
- Tabela `users` com planos FREE/BASIC/PREMIUM
- Tabela `politicians` com dados de deputados e senadores
- Tabela `political_events` para histórico
- Tabela `follows` para relacionamento user-politician
- Tabela `notifications` para notificações via WhatsApp
- Tabela `plans` para planos de assinatura

### Funcionalidades
- Cadastro de usuários via API
- Busca de políticos com filtros (estado, partido, cargo)
- Sistema de follows com limites por plano
- Notificações sobre eventos políticos
- População automática de políticos das APIs públicas
- Health check e monitoramento
- Cache com Redis
- Logs estruturados em JSON

### Tecnologias
- Python 3.11+
- FastAPI 0.109.0
- Pydantic 2.5.3
- Supabase (PostgreSQL)
- Redis 7
- Docker & Docker Swarm
- N8N para automação
- Traefik para proxy reverso

### Deploy
- Containerização com Docker
- Orquestração com Docker Swarm
- Deploy automatizado via script
- Health checks integrados
- Rollback automático em falhas

### Documentação
- README.md principal
- Documentação da API (OpenAPI/Swagger)
- Guia de deploy
- Guia de contribuição
- Documentação de workflows N8N

## [0.0.1] - 2024-01-01

### Adicionado
- Estrutura inicial do projeto
- Setup do repositório
- Definição de tecnologias

---

## Tipos de Mudanças

- `Added`: Novas funcionalidades
- `Changed`: Mudanças em funcionalidades existentes
- `Deprecated`: Funcionalidades obsoletas (serão removidas)
- `Removed`: Funcionalidades removidas
- `Fixed`: Correções de bugs
- `Security`: Correções de segurança

