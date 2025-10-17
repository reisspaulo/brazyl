"""
Schemas Pydantic para Eventos Políticos.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.notification import EventType


class PoliticalEventBase(BaseModel):
    """Schema base de evento político."""
    politician_id: UUID = Field(..., description="ID do político")
    event_type: EventType = Field(..., description="Tipo do evento")
    title: str = Field(..., min_length=5, max_length=500, description="Título do evento")
    description: Optional[str] = Field(None, description="Descrição detalhada")
    event_date: date = Field(..., description="Data do evento")
    amount: Optional[Decimal] = Field(None, description="Valor monetário (para despesas)")
    vote_result: Optional[str] = Field(
        None,
        pattern=r"^(SIM|NAO|ABSTENCAO|OBSTRUCAO)$",
        description="Resultado do voto"
    )
    source_url: Optional[str] = Field(None, description="URL da fonte oficial")


class PoliticalEventCreate(PoliticalEventBase):
    """Schema para criar evento político."""
    metadata: Optional[dict] = Field(
        default_factory=dict,
        description="Dados adicionais específicos do evento"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "politician_id": "770e8400-e29b-41d4-a716-446655440000",
                "event_type": "VOTACAO",
                "title": "Votação PL 1234/2024 - Meio Ambiente",
                "description": "Projeto de lei que estabelece novas regras para proteção ambiental.",
                "event_date": "2024-01-15",
                "vote_result": "SIM",
                "source_url": "https://camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=1234",
                "metadata": {
                    "project_number": "PL 1234/2024",
                    "session_number": "042.1.56.O"
                }
            }
        }


class PoliticalEventResponse(PoliticalEventBase):
    """Schema de resposta de evento político."""
    id: UUID
    metadata: Optional[dict] = None
    created_at: datetime
    
    # Dados do político (opcional)
    politician_name: Optional[str] = Field(None, description="Nome do político")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "990e8400-e29b-41d4-a716-446655440000",
                "politician_id": "770e8400-e29b-41d4-a716-446655440000",
                "politician_name": "João Silva",
                "event_type": "VOTACAO",
                "title": "Votação PL 1234/2024 - Meio Ambiente",
                "description": "Projeto de lei que estabelece novas regras para proteção ambiental.",
                "event_date": "2024-01-15",
                "vote_result": "SIM",
                "source_url": "https://camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=1234",
                "metadata": {
                    "project_number": "PL 1234/2024",
                    "session_number": "042.1.56.O"
                },
                "created_at": "2024-01-15T16:30:00Z"
            }
        }


class PoliticalEventListResponse(BaseModel):
    """Schema de resposta para lista de eventos políticos."""
    success: bool = True
    data: list[PoliticalEventResponse]
    meta: dict = Field(
        default_factory=lambda: {"page": 1, "limit": 20, "total": 0}
    )


class PoliticalEventFilters(BaseModel):
    """Filtros para busca de eventos políticos."""
    politician_id: Optional[UUID] = Field(None, description="Filtrar por político")
    event_type: Optional[EventType] = Field(None, description="Filtrar por tipo de evento")
    date_from: Optional[date] = Field(None, description="Data inicial")
    date_to: Optional[date] = Field(None, description="Data final")
    min_amount: Optional[Decimal] = Field(None, description="Valor mínimo (despesas)")
    max_amount: Optional[Decimal] = Field(None, description="Valor máximo (despesas)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "politician_id": "770e8400-e29b-41d4-a716-446655440000",
                "event_type": "VOTACAO",
                "date_from": "2024-01-01",
                "date_to": "2024-01-31"
            }
        }

