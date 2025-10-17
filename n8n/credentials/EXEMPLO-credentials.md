# Exemplos de Credenciais N8N

## Supabase

**Nome da Credencial**: `Brazyl Supabase`

**Tipo**: HTTP Request Auth / HTTP Header Auth

**Configuração**:
```
URL Base: https://your-project.supabase.co
Headers:
  - apikey: your-anon-key
  - Authorization: Bearer your-service-key
  - Content-Type: application/json
```

## FastAPI (Brazyl API)

**Nome da Credencial**: `Brazyl API`

**Tipo**: HTTP Request Auth / HTTP Header Auth

**Configuração**:
```
URL Base: https://api.brazyl.com (ou http://api:8000 para local)
Headers:
  - X-API-Key: your-api-key
  - Content-Type: application/json
```

## Avisa API (WhatsApp)

**Nome da Credencial**: `Avisa WhatsApp`

**Tipo**: HTTP Request Auth / HTTP Header Auth

**Configuração**:
```
URL Base: https://api.avisa.com.br
Headers:
  - Authorization: Bearer your-avisa-token
  - Content-Type: application/json
```

## Variáveis de Ambiente

Configurar no N8N (Settings > Environment Variables):

```
API_URL=https://api.brazyl.com
SUPABASE_URL=https://your-project.supabase.co
AVISA_URL=https://api.avisa.com.br
```

## Notas

- Nunca fazer commit de workflows com credenciais reais
- Usar variáveis de ambiente sempre que possível
- Rotacionar tokens periodicamente
- Usar credenciais diferentes para staging e produção

