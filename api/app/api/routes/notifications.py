"""
Endpoints relacionados a notificações.
"""

from uuid import UUID

from fastapi import APIRouter, status, HTTPException, Depends

from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationStatsResponse
)
from app.services import NotificationService, NotificationServiceError
from app.api.deps import verify_api_key, get_pagination_params
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar notificação",
    description="Cria uma nova notificação (uso interno - N8N)",
    dependencies=[Depends(verify_api_key)]
)
async def create_notification(notification_data: NotificationCreate):
    """
    Cria uma notificação.
    
    **Este endpoint é protegido por API Key (uso interno - N8N).**
    
    - **user_id**: ID do usuário que receberá a notificação
    - **politician_id**: ID do político relacionado (opcional)
    - **event_id**: ID do evento relacionado (opcional)
    - **title**: Título da notificação
    - **message**: Mensagem completa
    - **scheduled_for**: Data/hora de envio (se None, envia imediatamente)
    - **metadata**: Dados adicionais (opcional)
    """
    try:
        service = NotificationService()
        notification = await service.create_notification(notification_data)
        
        return NotificationResponse(**notification)
    
    except NotificationServiceError as e:
        logger.error(f"Erro ao criar notificação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/users/{user_id}",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar notificações do usuário",
    description="Lista notificações de um usuário"
)
async def get_user_notifications(
    user_id: UUID,
    pagination: dict = Depends(get_pagination_params)
):
    """
    Lista notificações de um usuário com paginação.
    
    Notificações são ordenadas por data de criação (mais recentes primeiro).
    """
    try:
        service = NotificationService()
        notifications, total = await service.get_user_notifications(
            user_id=user_id,
            limit=pagination["limit"],
            offset=pagination["offset"]
        )
        
        return NotificationListResponse(
            success=True,
            data=notifications,
            meta={
                "limit": pagination["limit"],
                "offset": pagination["offset"],
                "total": total
            }
        )
    
    except NotificationServiceError as e:
        logger.error(f"Erro ao listar notificações: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar notificações"
        )


@router.get(
    "/users/{user_id}/stats",
    response_model=NotificationStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Estatísticas de notificações",
    description="Retorna estatísticas de notificações de um usuário"
)
async def get_notification_stats(user_id: UUID):
    """
    Obtém estatísticas de notificações de um usuário.
    
    Inclui:
    - Total de notificações
    - Pendentes
    - Enviadas
    - Entregues
    - Falhadas
    - Data da última notificação
    """
    try:
        service = NotificationService()
        stats = await service.get_notification_stats(user_id)
        
        return NotificationStatsResponse(**stats)
    
    except NotificationServiceError as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter estatísticas de notificações"
        )


@router.post(
    "/process-pending",
    status_code=status.HTTP_200_OK,
    summary="Processar notificações pendentes",
    description="Processa e envia notificações pendentes agendadas (uso interno - Cron)",
    dependencies=[Depends(verify_api_key)]
)
async def process_pending_notifications():
    """
    Processa notificações pendentes que já passaram do horário agendado.
    
    **Este endpoint é protegido por API Key (uso interno - Cron Job).**
    
    Deve ser chamado periodicamente por um cron job (ex: a cada hora).
    """
    try:
        service = NotificationService()
        processed = await service.process_pending_notifications()
        
        return {
            "success": True,
            "processed": processed,
            "message": f"{processed} notificações processadas"
        }
    
    except NotificationServiceError as e:
        logger.error(f"Erro ao processar notificações: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar notificações pendentes"
        )

