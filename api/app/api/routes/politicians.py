"""
Endpoints relacionados a políticos.
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, status, HTTPException, Depends, Query

from app.schemas.politician import (
    PoliticianResponse,
    PoliticianListResponse,
    PoliticianFilters,
    PoliticalPosition
)
from app.schemas.political_event import PoliticalEventListResponse
from app.services import PoliticianService, PoliticianServiceError
from app.api.deps import get_pagination_params
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=PoliticianListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar políticos",
    description="Lista políticos com filtros opcionais (estado, partido, cargo)"
)
async def list_politicians(
    state: Optional[str] = Query(None, description="Filtrar por UF (ex: SP, RJ)"),
    party: Optional[str] = Query(None, description="Filtrar por partido (ex: PT, PSDB)"),
    position: Optional[PoliticalPosition] = Query(None, description="Filtrar por cargo"),
    name: Optional[str] = Query(None, description="Buscar por nome (parcial)"),
    is_active: bool = Query(True, description="Apenas políticos ativos"),
    pagination: dict = Depends(get_pagination_params)
):
    """
    Lista políticos com filtros e paginação.
    
    - **state**: Filtrar por UF (SP, RJ, etc)
    - **party**: Filtrar por partido (PT, PSDB, etc)
    - **position**: Filtrar por cargo (DEPUTADO_FEDERAL, SENADOR, etc)
    - **name**: Buscar por nome (busca parcial)
    - **is_active**: Apenas políticos ativos (padrão: true)
    """
    try:
        filters = PoliticianFilters(
            state=state,
            party=party,
            position=position,
            name=name,
            is_active=is_active
        )
        
        service = PoliticianService()
        politicians, total = await service.get_politicians(
            filters=filters,
            limit=pagination["limit"],
            offset=pagination["offset"]
        )
        
        return PoliticianListResponse(
            success=True,
            data=politicians,
            meta={
                "limit": pagination["limit"],
                "offset": pagination["offset"],
                "total": total
            }
        )
    
    except PoliticianServiceError as e:
        logger.error(f"Erro ao listar políticos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar políticos"
        )


@router.get(
    "/{politician_id}",
    response_model=PoliticianResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter político",
    description="Retorna dados detalhados de um político específico"
)
async def get_politician(politician_id: UUID):
    """
    Obtém dados completos de um político por ID.
    
    Inclui estatísticas como número de seguidores e eventos recentes.
    """
    try:
        service = PoliticianService()
        politician = await service.get_politician_by_id(politician_id)
        
        if not politician:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Político não encontrado"
            )
        
        return PoliticianResponse(**politician)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar político: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar político"
        )


@router.get(
    "/{politician_id}/history",
    response_model=PoliticalEventListResponse,
    status_code=status.HTTP_200_OK,
    summary="Histórico do político",
    description="Retorna histórico de ações do político (votações, gastos, etc)"
)
async def get_politician_history(
    politician_id: UUID,
    event_type: Optional[str] = Query(None, description="Tipo de evento (VOTACAO, DESPESA, etc)"),
    pagination: dict = Depends(get_pagination_params)
):
    """
    Obtém histórico de eventos de um político.
    
    - **event_type**: Filtrar por tipo de evento (VOTACAO, DESPESA, PROJETO_LEI, etc)
    
    Eventos são ordenados por data decrescente (mais recentes primeiro).
    """
    try:
        service = PoliticianService()
        events, total = await service.get_politician_history(
            politician_id=politician_id,
            event_type=event_type,
            limit=pagination["limit"],
            offset=pagination["offset"]
        )
        
        return PoliticalEventListResponse(
            success=True,
            data=events,
            meta={
                "limit": pagination["limit"],
                "offset": pagination["offset"],
                "total": total
            }
        )
    
    except PoliticianServiceError as e:
        logger.error(f"Erro ao buscar histórico: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar histórico"
        )

