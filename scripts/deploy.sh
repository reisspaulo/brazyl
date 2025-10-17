#!/bin/bash
# Script de deploy automatizado para Brazyl
# Uso: ./deploy.sh [staging|production] [--local]

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
ENVIRONMENT=$1
USE_LOCAL=false

if [ "$2" = "--local" ]; then
    USE_LOCAL=true
fi

# Validate environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    log_error "Ambiente inválido. Use: staging ou production"
    echo "Uso: ./deploy.sh [staging|production] [--local]"
    exit 1
fi

log_info "Iniciando deploy para ${ENVIRONMENT}..."

# Check if .env exists
ENV_FILE="deploy/.env"
if [ ! -f "$ENV_FILE" ]; then
    log_error "Arquivo ${ENV_FILE} não encontrado!"
    log_info "Copie deploy/.env.example para deploy/.env e configure as variáveis"
    exit 1
fi

# Load environment variables
set -a
source "$ENV_FILE"
set +a

log_info "Variáveis de ambiente carregadas"

# Build Docker image
log_info "Building Docker image..."
cd api
docker build -t brazyl/api:latest -t brazyl/api:${ENVIRONMENT} .
cd ..

log_info "Imagem construída com sucesso"

# Push to registry (if not local)
if [ "$USE_LOCAL" = false ]; then
    if [ -z "$REGISTRY_URL" ]; then
        log_warn "REGISTRY_URL não configurado, usando imagem local"
    else
        log_info "Fazendo push para registry..."
        
        # Login to registry
        if [ -n "$REGISTRY_USER" ] && [ -n "$REGISTRY_PASSWORD" ]; then
            echo "$REGISTRY_PASSWORD" | docker login "$REGISTRY_URL" -u "$REGISTRY_USER" --password-stdin
        fi
        
        # Tag and push
        docker tag brazyl/api:latest ${REGISTRY_URL}/brazyl/api:latest
        docker tag brazyl/api:${ENVIRONMENT} ${REGISTRY_URL}/brazyl/api:${ENVIRONMENT}
        
        docker push ${REGISTRY_URL}/brazyl/api:latest
        docker push ${REGISTRY_URL}/brazyl/api:${ENVIRONMENT}
        
        log_info "Imagem enviada para registry"
    fi
fi

# Deploy to Docker Swarm
log_info "Fazendo deploy da stack..."

if [ "$ENVIRONMENT" = "staging" ]; then
    STACK_NAME="brazyl-staging"
else
    STACK_NAME="brazyl"
fi

docker stack deploy -c deploy/brazyl-stack.yml "$STACK_NAME"

log_info "Stack ${STACK_NAME} deployed"

# Wait for services to be ready
log_info "Aguardando serviços ficarem prontos..."
sleep 10

# Check service status
log_info "Status dos serviços:"
docker stack ps "$STACK_NAME" --no-trunc

# Health check
log_info "Verificando health da API..."
sleep 20

if [ "$ENVIRONMENT" = "production" ]; then
    HEALTH_URL="https://api.brazyl.com/health"
else
    HEALTH_URL="https://api-staging.brazyl.com/health"
fi

if [ "$USE_LOCAL" = true ]; then
    HEALTH_URL="http://localhost:8000/health"
fi

MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s "$HEALTH_URL" > /dev/null; then
        log_info "API está saudável!"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_warn "Health check falhou (tentativa $RETRY_COUNT/$MAX_RETRIES)"
        
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            sleep 10
        fi
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_error "API não passou no health check após $MAX_RETRIES tentativas"
    log_error "Verifique os logs com: docker service logs ${STACK_NAME}_api"
    exit 1
fi

# Show logs
log_info "Últimas linhas dos logs da API:"
docker service logs --tail 20 "${STACK_NAME}_api"

log_info "Deploy concluído com sucesso!"
log_info "Para ver logs: docker service logs -f ${STACK_NAME}_api"
log_info "Para verificar status: docker stack ps ${STACK_NAME}"
log_info "Para fazer rollback: docker service rollback ${STACK_NAME}_api"

exit 0

