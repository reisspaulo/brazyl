"""
Endpoints relacionados a usuários.
"""

from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends, Query

from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.follow import FollowListResponse
from app.services import UserService, UserServiceError, FollowService, FollowServiceError
from app.api.deps import get_pagination_params
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar usuário",
    description="Cria um novo usuário no sistema"
)
async def create_user(user_data: UserCreate):
    """
    Cria um novo usuário.
    
    - **whatsapp_number**: Número WhatsApp no formato +5511999999999
    - **name**: Nome completo do usuário
    - **email**: Email (opcional)
    - **cpf**: CPF apenas números (opcional)
    - **plan_type**: Tipo de plano (FREE, BASIC, PREMIUM)
    """
    try:
        service = UserService()
        user = await service.create_user(user_data)
        
        return UserResponse(**user)
    
    except UserServiceError as e:
        logger.warning(f"Erro ao criar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter usuário",
    description="Retorna dados de um usuário específico"
)
async def get_user(user_id: UUID):
    """
    Obtém dados de um usuário por ID.
    """
    try:
        service = UserService()
        user = await service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Adicionar contagem de follows
        follow_service = FollowService()
        _, total_follows = await follow_service.get_user_follows(user_id, limit=1)
        user["following_count"] = total_follows
        
        return UserResponse(**user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar usuário"
        )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar usuário",
    description="Atualiza dados de um usuário"
)
async def update_user(user_id: UUID, user_data: UserUpdate):
    """
    Atualiza dados de um usuário.
    
    Apenas os campos fornecidos serão atualizados.
    """
    try:
        service = UserService()
        user = await service.update_user(user_id, user_data)
        
        return UserResponse(**user)
    
    except UserServiceError as e:
        logger.warning(f"Erro ao atualizar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{user_id}/follows",
    response_model=FollowListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar políticos seguidos",
    description="Lista todos os políticos seguidos por um usuário"
)
async def get_user_follows(
    user_id: UUID,
    pagination: dict = Depends(get_pagination_params)
):
    """
    Lista políticos seguidos por um usuário com paginação.
    """
    try:
        service = FollowService()
        follows, total = await service.get_user_follows(
            user_id,
            limit=pagination["limit"],
            offset=pagination["offset"]
        )
        
        return FollowListResponse(
            success=True,
            data=follows,
            meta={
                "limit": pagination["limit"],
                "offset": pagination["offset"],
                "total": total
            }
        )
    
    except FollowServiceError as e:
        logger.error(f"Erro ao listar follows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar políticos seguidos"
        )


@router.get(
    "/{user_id}/limits",
    status_code=status.HTTP_200_OK,
    summary="Verificar limites do usuário",
    description="Retorna informações sobre limites do plano do usuário"
)
async def get_user_limits(user_id: UUID):
    """
    Verifica limites do usuário baseado no plano.
    
    Retorna quantos políticos pode seguir e quantos já está seguindo.
    """
    try:
        service = UserService()
        limits = await service.check_user_limits(user_id)
        
        return {
            "success": True,
            "data": limits
        }
    
    except UserServiceError as e:
        logger.error(f"Erro ao verificar limites: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao verificar limites"
        )

