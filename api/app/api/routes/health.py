"""
Endpoint de health check.
Verifica status da aplicação e dependências.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, status
from pydantic import BaseModel

from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Response do health check."""
    
    status: str
    environment: str
    version: str
    timestamp: datetime
    dependencies: dict[str, str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "environment": "dev",
                "version": "0.1.0",
                "timestamp": "2024-01-15T10:30:00Z",
                "dependencies": {
                    "supabase": "connected",
                    "redis": "connected"
                }
            }
        }


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Verifica o status da aplicação e suas dependências"
)
async def health_check() -> HealthResponse:
    """
    Endpoint de health check.
    
    Verifica:
    - Status da aplicação
    - Conexão com Supabase
    - Conexão com Redis
    
    Returns:
        Status da aplicação e dependências
    """
    # TODO: Implementar verificações reais de conexão
    dependencies = {
        "supabase": "connected",  # Implementar verificação real
        "redis": "connected"      # Implementar verificação real
    }
    
    logger.debug("Health check realizado")
    
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        version="0.1.0",
        timestamp=datetime.utcnow(),
        dependencies=dependencies
    )

