# Brazyl - Acompanhe Políticos Brasileiros via WhatsApp

Sistema que permite cidadãos brasileiros acompanharem a atuação de políticos (deputados e senadores) através do WhatsApp, recebendo notificações sobre votações, gastos e atividades parlamentares.

## Visão Geral

O Brazyl é um MVP (Minimum Viable Product) que democratiza o acesso à informação política, tornando simples e acessível acompanhar o que seus representantes estão fazendo no Congresso Nacional.

### Funcionalidades Principais

- Cadastro de usuários via WhatsApp
- Busca e filtro de políticos (por estado, partido, cargo)
- Seguir até 3 políticos (plano gratuito)
- Notificações sobre:
  - Votações em projetos de lei
  - Despesas parlamentares
  - Propostas e discursos
- Planos: FREE (3 políticos), BASIC (10 políticos), PREMIUM (ilimitado)

## Tecnologias

### Backend
- **FastAPI** (Python 3.11+) - API REST
- **Supabase** (PostgreSQL) - Banco de dados
- **Redis** - Cache e filas
- **N8N** - Automação e orquestração de workflows

### Integrações
- **Avisa API** - Envio de mensagens WhatsApp
- **API Câmara dos Deputados** - Dados de deputados federais
- **API Senado Federal** - Dados de senadores
- **Portal da Transparência** - Gastos públicos

### Deploy
- **Docker** - Containerização
- **Docker Swarm** - Orquestração em produção
- **Traefik** - Proxy reverso e SSL

## Estrutura do Projeto

```
Brazyl/
├── api/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/           # Rotas REST
│   │   ├── models/        # Modelos de dados
│   │   ├── schemas/       # Schemas Pydantic
│   │   ├── services/      # Lógica de negócio
│   │   ├── integrations/  # Clientes APIs
│   │   └── utils/         # Utilitários
│   ├── tests/             # Testes automatizados
│   ├── Dockerfile
│   └── requirements.txt
│
├── database/              # Scripts SQL
│   ├── schema.sql         # Schema completo
│   └── migrations/        # Migrações
│
├── n8n/                   # Workflows N8N
│   ├── workflows/         # JSONs dos workflows
│   └── credentials/       # Templates de credenciais
│
├── scripts/               # Scripts utilitários
│   ├── populate_politicians.py
│   ├── test_supabase.py
│   └── deploy.sh
│
├── deploy/                # Configurações de deploy
│   ├── docker-compose.yml
│   ├── brazyl-stack.yml
│   └── README.md
│
└── docs/                  # Documentação
    ├── API.md
    ├── DEPLOYMENT.md
    └── CONTRIBUTING.md
```

## Quick Start

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Conta Supabase (free tier)
- Token da API Avisa (WhatsApp)

### Instalação Local

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/brazyl.git
cd brazyl
```

2. **Configure variáveis de ambiente**
```bash
cd api
# Crie o arquivo .env com as seguintes variáveis:
```

```bash
# Configurações da Aplicação
API_KEY=your_api_key_here
DEBUG=false
LOG_LEVEL=INFO

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_key_here

# Redis
REDIS_URL=redis://localhost:6379

# Avisa API (WhatsApp)
AVISA_API_URL=https://api.avisa.ai
AVISA_API_TOKEN=your_avisa_token_here

# Configurações de Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Configurações de Cache
CACHE_TTL=300
CACHE_MAX_SIZE=1000
```

3. **Instale dependências**
```bash
pip install -r requirements.txt
```

4. **Execute o banco de dados** (aplicar schema no Supabase)
```sql
-- Copiar e executar: database/schema.sql
```

5. **Inicie a API**
```bash
uvicorn app.main:app --reload
```

6. **Acesse a documentação**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Com Docker

```bash
cd deploy
docker-compose up -d
```

Serviços disponíveis:
- API: http://localhost:8000
- N8N: http://localhost:5678
- Redis: localhost:6379

## Uso

### Cadastrar Usuário (API)

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "whatsapp_number": "+5511999999999",
    "name": "João Silva",
    "email": "joao@example.com"
  }'
```

### Buscar Políticos

```bash
curl "http://localhost:8000/politicians?state=SP&party=PT&limit=10"
```

### Seguir Político

```bash
curl -X POST "http://localhost:8000/follows?user_id=<user_uuid>" \
  -H "Content-Type: application/json" \
  -d '{
    "politician_id": "<politician_uuid>"
  }'
```

## População de Dados

Para popular o banco com políticos reais:

```bash
cd scripts
python populate_politicians.py --verbose

# Ou apenas deputados
python populate_politicians.py --only-deputados

# Modo dry-run (simular)
python populate_politicians.py --dry-run
```

## Testes

```bash
cd api
pytest
pytest --cov=app tests/
```

## Deploy em Produção

Ver [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) para guia completo.

Resumo:

```bash
# Build e deploy
./scripts/deploy.sh production

# Verificar status
docker stack ps brazyl

# Ver logs
docker service logs -f brazyl_api
```

## Contribuindo

Contribuições são bem-vindas! Ver [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

Passos básicos:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Roadmap

### v0.1.0 (MVP - Atual)
- [x] API REST completa
- [x] Integração Supabase
- [x] Integração APIs públicas
- [x] Workflows N8N base
- [x] Deploy Docker

### v0.5.0 (Beta)
- [ ] WhatsApp bot funcionanal completo
- [ ] Sistema de pagamentos (planos)
- [ ] Dashboard web para usuários
- [ ] Testes automatizados completos
- [ ] Monitoramento e alertas

### v1.0.0 (Lançamento)
- [ ] App mobile (Flutter)
- [ ] Notificações push
- [ ] Análise de dados e insights
- [ ] Gamificação (badges, rankings)
- [ ] Integração redes sociais

## Licença

Este projeto está sob a licença MIT. Ver arquivo [LICENSE](LICENSE) para mais detalhes.

## Autores

- Seu Nome - [@seu_twitter](https://twitter.com/seu_twitter)

## Agradecimentos

- APIs públicas do governo brasileiro
- Comunidade FastAPI
- Equipe Supabase
- Projeto N8N

## Contato

- Email: contato@brazyl.com
- Website: https://brazyl.com
- Twitter: [@brazyl_oficial](https://twitter.com/brazyl_oficial)

---

Feito com ❤️ para a democracia brasileira

