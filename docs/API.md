# Documentação da API - Brazyl

## Base URL

- **Produção**: `https://api.brazyl.com`
- **Staging**: `https://api-staging.brazyl.com`
- **Local**: `http://localhost:8000`

## Autenticação

### Endpoints Públicos
Maioria dos endpoints de consulta não requerem autenticação.

### Endpoints Protegidos
Endpoints internos (usados pelo N8N) requerem API Key no header:

```http
X-API-Key: your-api-key-here
```

## Endpoints

### Health Check

#### GET /health

Verifica status da aplicação e dependências.

**Response**
```json
{
  "status": "healthy",
  "environment": "prod",
  "version": "0.1.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "dependencies": {
    "supabase": "connected",
    "redis": "connected"
  }
}
```

---

### Usuários

#### POST /users

Cria um novo usuário.

**Request Body**
```json
{
  "whatsapp_number": "+5511999999999",
  "name": "João Silva",
  "email": "joao@example.com",
  "cpf": "12345678900",
  "plan_type": "FREE"
}
```

**Response** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "whatsapp_number": "+5511999999999",
  "name": "João Silva",
  "email": "joao@example.com",
  "plan": {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "name": "Gratuito",
    "type": "FREE",
    "max_politicians": 3
  },
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### GET /users/{user_id}

Obtém dados de um usuário.

**Response** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "whatsapp_number": "+5511999999999",
  "name": "João Silva",
  "following_count": 2,
  "plan": { ... }
}
```

#### PATCH /users/{user_id}

Atualiza dados do usuário.

**Request Body** (campos opcionais)
```json
{
  "name": "João da Silva Santos",
  "email": "joao.novo@example.com"
}
```

#### GET /users/{user_id}/follows

Lista políticos seguidos pelo usuário.

**Query Parameters**
- `limit` (default: 20, max: 100)
- `offset` (default: 0)

**Response** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "politician": {
        "id": "770e8400-e29b-41d4-a716-446655440000",
        "name": "João Silva",
        "party": "PT",
        "state": "SP"
      },
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "meta": {
    "limit": 20,
    "offset": 0,
    "total": 2
  }
}
```

---

### Políticos

#### GET /politicians

Lista políticos com filtros.

**Query Parameters**
- `state`: UF (ex: SP, RJ)
- `party`: Partido (ex: PT, PSDB)
- `position`: Cargo (DEPUTADO_FEDERAL, SENADOR)
- `name`: Nome (busca parcial)
- `is_active`: boolean (default: true)
- `limit`: int (default: 20, max: 100)
- `offset`: int (default: 0)

**Example**
```
GET /politicians?state=SP&party=PT&limit=10
```

**Response** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "name": "João Silva Santos",
      "parliamentary_name": "João Silva",
      "position": "DEPUTADO_FEDERAL",
      "party": "PT",
      "state": "SP",
      "followers_count": 1250,
      "photo_url": "https://...",
      "social_media": {
        "twitter": "@joaosilva"
      }
    }
  ],
  "meta": {
    "limit": 10,
    "offset": 0,
    "total": 25
  }
}
```

#### GET /politicians/{politician_id}

Obtém detalhes de um político.

**Response** `200 OK` - Similar ao item da lista acima

#### GET /politicians/{politician_id}/history

Histórico de eventos do político.

**Query Parameters**
- `event_type`: VOTACAO, DESPESA, PROJETO_LEI, etc
- `limit`: int
- `offset`: int

**Response** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "event_type": "VOTACAO",
      "title": "Votação PL 1234/2024 - Meio Ambiente",
      "vote_result": "SIM",
      "event_date": "2024-01-15",
      "source_url": "https://..."
    }
  ],
  "meta": { ... }
}
```

---

### Follows

#### POST /follows

Segue um político.

**Query Parameter**
- `user_id`: UUID do usuário

**Request Body**
```json
{
  "politician_id": "770e8400-e29b-41d4-a716-446655440000"
}
```

**Response** `201 Created`
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "politician_id": "770e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:00:00Z"
}
```

**Erros**
- `403 Forbidden`: Limite de políticos atingido
- `409 Conflict`: Já segue este político

#### DELETE /follows/{follow_id}

Deixa de seguir um político.

**Response** `204 No Content`

#### GET /follows/stats/{user_id}

Estatísticas de follows do usuário.

**Response** `200 OK`
```json
{
  "total_following": 5,
  "max_allowed": 10,
  "remaining": 5,
  "by_position": {
    "DEPUTADO_FEDERAL": 3,
    "SENADOR": 2
  },
  "by_state": {
    "SP": 3,
    "RJ": 2
  }
}
```

---

### Notificações

#### POST /notifications
🔒 **Protegido por API Key**

Cria uma notificação (uso interno - N8N).

**Headers**
```
X-API-Key: your-api-key
```

**Request Body**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "politician_id": "770e8400-e29b-41d4-a716-446655440000",
  "title": "Nova votação de João Silva",
  "message": "O deputado João Silva votou SIM no PL 1234/2024",
  "scheduled_for": "2024-01-16T08:00:00Z",
  "metadata": {
    "event_type": "VOTACAO",
    "vote_result": "SIM"
  }
}
```

#### GET /notifications/users/{user_id}

Lista notificações do usuário.

**Query Parameters**
- `limit`: int
- `offset`: int

#### GET /notifications/users/{user_id}/stats

Estatísticas de notificações.

#### POST /notifications/process-pending
🔒 **Protegido por API Key**

Processa notificações pendentes (cron job).

---

## Códigos de Status

- `200 OK`: Sucesso
- `201 Created`: Recurso criado
- `204 No Content`: Sucesso sem conteúdo
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: API Key inválida
- `403 Forbidden`: Ação não permitida (ex: limite atingido)
- `404 Not Found`: Recurso não encontrado
- `409 Conflict`: Conflito (ex: já existe)
- `422 Unprocessable Entity`: Validação falhou
- `500 Internal Server Error`: Erro do servidor

## Paginação

Endpoints de listagem suportam paginação:

**Parâmetros**
- `limit`: Itens por página (default: 20, max: 100)
- `offset`: Número de itens a pular (default: 0)

**Response Meta**
```json
{
  "meta": {
    "limit": 20,
    "offset": 0,
    "total": 150
  }
}
```

## Rate Limiting

- 60 requisições por minuto por IP
- Headers de resposta:
  - `X-RateLimit-Limit`: Limite total
  - `X-RateLimit-Remaining`: Requisições restantes
  - `X-RateLimit-Reset`: Timestamp do reset

## Exemplos com cURL

### Criar usuário
```bash
curl -X POST https://api.brazyl.com/users \
  -H "Content-Type: application/json" \
  -d '{
    "whatsapp_number": "+5511999999999",
    "name": "João Silva",
    "email": "joao@example.com"
  }'
```

### Buscar políticos de SP
```bash
curl "https://api.brazyl.com/politicians?state=SP&limit=5"
```

### Seguir político
```bash
curl -X POST "https://api.brazyl.com/follows?user_id=<uuid>" \
  -H "Content-Type: application/json" \
  -d '{"politician_id": "<uuid>"}'
```

## SDKs e Libraries

### Python
```python
import httpx

API_URL = "https://api.brazyl.com"

async with httpx.AsyncClient() as client:
    response = await client.get(f"{API_URL}/politicians?state=SP")
    politicians = response.json()
```

### JavaScript/Node.js
```javascript
const API_URL = "https://api.brazyl.com";

const response = await fetch(`${API_URL}/politicians?state=SP`);
const politicians = await response.json();
```

## Suporte

- Email: api@brazyl.com
- Discord: https://discord.gg/brazyl
- Issues: https://github.com/seu-usuario/brazyl/issues

