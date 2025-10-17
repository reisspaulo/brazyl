# Deploy - Brazyl

## Estrutura

- `docker-compose.yml` - Para testes locais
- `brazyl-stack.yml` - Para produção (Docker Swarm)
- `.env.example` - Exemplo de variáveis de ambiente
- `deploy.sh` - Script automatizado de deploy

## Deploy Local (Desenvolvimento)

### Pré-requisitos
- Docker e Docker Compose instalados
- Arquivo `.env` configurado

### Passos

1. Configurar variáveis de ambiente:
```bash
cp .env.example .env
# Editar .env com suas credenciais
```

2. Iniciar serviços:
```bash
docker-compose up -d
```

3. Verificar logs:
```bash
docker-compose logs -f api
```

4. Acessar:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- N8N: http://localhost:5678 (admin/admin123)
- Redis: localhost:6379

5. Parar serviços:
```bash
docker-compose down
```

## Deploy Produção (Docker Swarm)

### Pré-requisitos
- Docker Swarm inicializado
- Traefik configurado (proxy reverso)
- Domínios apontados (api.brazyl.com, n8n.brazyl.com)
- Certificados SSL (Let's Encrypt via Traefik)

### Inicializar Swarm (se necessário)

```bash
docker swarm init
```

### Criar rede Traefik

```bash
docker network create --driver=overlay traefik-public
```

### Deploy Traefik (se ainda não tiver)

Ver documentação do Traefik para Docker Swarm.

### Deploy da Stack

1. Configurar variáveis:
```bash
cp .env.example .env
# Editar .env com valores de produção
source .env
```

2. Build e push da imagem (se usar registry):
```bash
cd ../api
docker build -t brazyl/api:latest .
docker tag brazyl/api:latest registry.example.com/brazyl/api:latest
docker push registry.example.com/brazyl/api:latest
```

3. Deploy da stack:
```bash
docker stack deploy -c brazyl-stack.yml brazyl
```

4. Verificar status:
```bash
docker stack ps brazyl
docker service ls
docker service logs brazyl_api
```

### Atualizar Deploy

```bash
# Build nova imagem
docker build -t brazyl/api:latest ../api

# Push para registry
docker push registry.example.com/brazyl/api:latest

# Atualizar serviço (rolling update)
docker service update --image registry.example.com/brazyl/api:latest brazyl_api
```

### Rollback

```bash
docker service rollback brazyl_api
```

### Remover Stack

```bash
docker stack rm brazyl
```

## Script Automatizado

O script `deploy.sh` automatiza o processo de deploy.

### Uso

```bash
# Deploy para staging
./deploy.sh staging

# Deploy para produção
./deploy.sh production

# Deploy com build local (sem registry)
./deploy.sh production --local
```

## Monitoramento

### Health Check

```bash
curl https://api.brazyl.com/health
```

### Logs

```bash
# Logs da API
docker service logs -f brazyl_api

# Logs do Redis
docker service logs brazyl_redis

# Logs do N8N
docker service logs brazyl_n8n
```

### Métricas

```bash
# CPU e memória dos serviços
docker stats

# Status dos serviços
docker service ps brazyl_api
```

## Troubleshooting

### Serviço não inicia

```bash
# Ver logs de erro
docker service logs brazyl_api

# Ver tasks com falha
docker service ps brazyl_api --filter "desired-state=running"

# Inspecionar serviço
docker service inspect brazyl_api
```

### Problemas de rede

```bash
# Verificar redes
docker network ls
docker network inspect traefik-public

# Testar conectividade entre serviços
docker exec -it <container_id> ping redis
```

### Rollback de emergência

```bash
docker service rollback brazyl_api
```

## Backup

### Redis

```bash
# Backup manual
docker exec <redis_container> redis-cli SAVE
docker cp <redis_container>:/data/dump.rdb ./backup/

# Restaurar
docker cp ./backup/dump.rdb <redis_container>:/data/
docker restart <redis_container>
```

### N8N

```bash
# Backup workflows
docker cp <n8n_container>:/home/node/.n8n ./backup/n8n/

# Restaurar
docker cp ./backup/n8n/ <n8n_container>:/home/node/.n8n
docker restart <n8n_container>
```

## Escalabilidade

### Escalar API

```bash
# Aumentar replicas
docker service scale brazyl_api=4

# Reduzir replicas
docker service scale brazyl_api=2
```

### Recursos

Ajustar limites em `brazyl-stack.yml`:

```yaml
resources:
  limits:
    cpus: '1.0'
    memory: 1G
  reservations:
    cpus: '0.5'
    memory: 512M
```

## Segurança

1. Usar secrets do Docker Swarm para credenciais sensíveis
2. Ativar TLS em todas as conexões
3. Configurar firewall para expor apenas portas 80/443
4. Usar API Key forte para endpoints internos
5. Manter imagens atualizadas
6. Fazer auditorias regulares de segurança

## Custos Estimados

### VPS Mínimo
- 2 vCPU, 4GB RAM, 80GB SSD
- ~$20-40/mês

### Serviços Externos
- Supabase: Free tier ou $25/mês
- Domínio: ~$12/ano
- Certificado SSL: Grátis (Let's Encrypt)

