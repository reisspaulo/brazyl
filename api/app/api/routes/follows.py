"""
Endpoints relacionados a seguir políticos.
"""

from uuid import UUID

from fastapi import APIRouter, status, HTTPException

from app.schemas.follow import FollowCreate, FollowResponse, FollowStatsResponse
from app.services import FollowService, FollowServiceError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=FollowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Seguir político",
    description="Adiciona um político à lista de seguidos do usuário"
)
async def follow_politician(
    user_id: UUID,
    follow_data: FollowCreate
):
    """
    Segue um político.
    
    - **user_id**: ID do usuário (passado como query parameter)
    - **politician_id**: ID do político a seguir
    
    Valida se o usuário atingiu o limite do plano antes de criar o follow.
    """
    try:
        service = FollowService()
        follow = await service.follow_politician(
            user_id=user_id,
            politician_id=follow_data.politician_id
        )
        
        return FollowResponse(**follow)
    
    except FollowServiceError as e:
        logger.warning(f"Erro ao seguir político: {str(e)}")
        
        # Verificar se é erro de limite
        if "limite" in str(e).lower() or "upgrade" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        
        # Verificar se já segue
        if "já segue" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{follow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deixar de seguir político",
    description="Remove um político da lista de seguidos"
)
async def unfollow_politician(follow_id: UUID):
    """
    Deixa de seguir um político.
    
    - **follow_id**: ID do follow a ser removido
    """
    try:
        service = FollowService()
        await service.unfollow_politician(follow_id)
        
        return None
    
    except FollowServiceError as e:
        logger.warning(f"Erro ao deixar de seguir político: {str(e)}")
        
        if "não encontrado" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/stats/{user_id}",
    response_model=FollowStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Estatísticas de follows",
    description="Retorna estatísticas sobre os políticos seguidos pelo usuário"
)
async def get_follow_stats(user_id: UUID):
    """
    Obtém estatísticas de follows de um usuário.
    
    Inclui:
    - Total de políticos seguidos
    - Máximo permitido pelo plano
    - Quantos ainda pode seguir
    - Distribuição por cargo
    - Distribuição por estado
    """
    try:
        service = FollowService()
        stats = await service.get_follow_stats(user_id)
        
        return FollowStatsResponse(**stats)
    
    except FollowServiceError as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter estatísticas"
        )

