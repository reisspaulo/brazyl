"""
Schemas Pydantic para Notificações.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field


class NotificationStatus(str, Enum):
    """Status de entrega da notificação."""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class EventType(str, Enum):
    """Tipos de eventos políticos."""
    VOTACAO = "VOTACAO"
    DESPESA = "DESPESA"
    PROJETO_LEI = "PROJETO_LEI"
    PROPOSTA = "PROPOSTA"
    DISCURSO = "DISCURSO"


class NotificationBase(BaseModel):
    """Schema base de notificação."""
    user_id: UUID = Field(..., description="ID do usuário")
    title: str = Field(..., min_length=5, max_length=500, description="Título da notificação")
    message: str = Field(..., min_length=10, description="Mensagem completa")
    politician_id: Optional[UUID] = Field(None, description="ID do político relacionado")
    event_id: Optional[UUID] = Field(None, description="ID do evento relacionado")


class NotificationCreate(NotificationBase):
    """Schema para criar notificação (uso interno - N8N)."""
    scheduled_for: Optional[datetime] = Field(
        None,
        description="Quando a notificação deve ser enviada (se None, envia imediatamente)"
    )
    metadata: Optional[dict] = Field(
        default_factory=dict,
        description="Dados adicionais da notificação"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "politician_id": "770e8400-e29b-41d4-a716-446655440000",
                "event_id": "990e8400-e29b-41d4-a716-446655440000",
                "title": "Nova votação de João Silva",
                "message": "O deputado João Silva votou SIM no Projeto de Lei 1234/2024 sobre meio ambiente.",
                "scheduled_for": "2024-01-16T08:00:00Z",
                "metadata": {
                    "event_type": "VOTACAO",
                    "vote_result": "SIM",
                    "project_number": "PL 1234/2024"
                }
            }
        }


class NotificationUpdate(BaseModel):
    """Schema para atualizar status de notificação."""
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None


class NotificationResponse(NotificationBase):
    """Schema de resposta de notificação."""
    id: UUID
    status: NotificationStatus
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    
    # Dados relacionados (opcionais)
    politician_name: Optional[str] = Field(None, description="Nome do político")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "110e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "politician_id": "770e8400-e29b-41d4-a716-446655440000",
                "event_id": "990e8400-e29b-41d4-a716-446655440000",
                "title": "Nova votação de João Silva",
                "message": "O deputado João Silva votou SIM no Projeto de Lei 1234/2024.",
                "status": "DELIVERED",
                "scheduled_for": "2024-01-16T08:00:00Z",
                "sent_at": "2024-01-16T08:00:05Z",
                "delivered_at": "2024-01-16T08:00:10Z",
                "politician_name": "João Silva",
                "metadata": {
                    "event_type": "VOTACAO",
                    "vote_result": "SIM"
                },
                "created_at": "2024-01-15T20:00:00Z"
            }
        }


class NotificationListResponse(BaseModel):
    """Schema de resposta para lista de notificações."""
    success: bool = True
    data: list[NotificationResponse]
    meta: dict = Field(
        default_factory=lambda: {"page": 1, "limit": 20, "total": 0}
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [],
                "meta": {
                    "page": 1,
                    "limit": 20,
                    "total": 87
                }
            }
        }


class NotificationStatsResponse(BaseModel):
    """Estatísticas de notificações de um usuário."""
    total: int = Field(..., description="Total de notificações")
    pending: int = Field(..., description="Notificações pendentes")
    sent: int = Field(..., description="Notificações enviadas")
    delivered: int = Field(..., description="Notificações entregues")
    failed: int = Field(..., description="Notificações com falha")
    last_notification_at: Optional[datetime] = Field(None, description="Última notificação recebida")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 87,
                "pending": 5,
                "sent": 2,
                "delivered": 78,
                "failed": 2,
                "last_notification_at": "2024-01-15T14:30:00Z"
            }
        }

