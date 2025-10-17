"""
Dependências compartilhadas entre rotas.
Autenticação, validação, conexões, etc.
"""

from typing import Annotated
from fastapi import Header, HTTPException, status

from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def verify_api_key(x_api_key: Annotated[str, Header()]) -> str:
    """
    Valida API Key no header da requisição.
    Usado para autenticar chamadas do N8N e outros serviços internos.
    
    Args:
        x_api_key: API Key fornecida no header X-API-Key
    
    Returns:
        API Key validada
    
    Raises:
        HTTPException: Se a API Key for inválida
    
    Example:
        ```python
        @router.post("/internal-endpoint")
        async def internal_endpoint(api_key: str = Depends(verify_api_key)):
            # Endpoint protegido
            pass
        ```
    """
    if x_api_key != settings.api_key:
        logger.warning("Tentativa de acesso com API Key inválida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )
    
    return x_api_key


def get_pagination_params(
    limit: int = 20,
    offset: int = 0
) -> dict[str, int]:
    """
    Extrai e valida parâmetros de paginação.
    
    Args:
        limit: Número máximo de itens por página (padrão: 20, máx: 100)
        offset: Número de itens a pular (padrão: 0)
    
    Returns:
        Dicionário com limit e offset validados
    
    Raises:
        HTTPException: Se os parâmetros forem inválidos
    
    Example:
        ```python
        @router.get("/items")
        async def list_items(pagination: dict = Depends(get_pagination_params)):
            limit = pagination["limit"]
            offset = pagination["offset"]
        ```
    """
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit deve estar entre 1 e 100"
        )
    
    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Offset deve ser maior ou igual a 0"
        )
    
    return {"limit": limit, "offset": offset}

