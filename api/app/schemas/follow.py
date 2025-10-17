"""
Schemas Pydantic para Follows (Seguir Políticos).
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.politician import PoliticianResponse


class FollowBase(BaseModel):
    """Schema base de follow."""
    user_id: UUID = Field(..., description="ID do usuário")
    politician_id: UUID = Field(..., description="ID do político")


class FollowCreate(BaseModel):
    """Schema para criar um follow."""
    politician_id: UUID = Field(..., description="ID do político a seguir")
    
    class Config:
        json_schema_extra = {
            "example": {
                "politician_id": "770e8400-e29b-41d4-a716-446655440000"
            }
        }


class FollowResponse(BaseModel):
    """Schema de resposta de follow."""
    id: UUID
    user_id: UUID
    politician_id: UUID
    created_at: datetime
    
    # Dados do político seguido (opcional)
    politician: Optional[PoliticianResponse] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "politician_id": "770e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-01-15T10:00:00Z",
                "politician": {
                    "id": "770e8400-e29b-41d4-a716-446655440000",
                    "name": "João da Silva Santos",
                    "parliamentary_name": "João Silva",
                    "position": "DEPUTADO_FEDERAL",
                    "party": "PT",
                    "state": "SP"
                }
            }
        }


class FollowListResponse(BaseModel):
    """Schema de resposta para lista de follows."""
    success: bool = True
    data: list[FollowResponse]
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
                    "total": 5
                }
            }
        }


class FollowStatsResponse(BaseModel):
    """Estatísticas de follows de um usuário."""
    total_following: int = Field(..., description="Total de políticos seguidos")
    max_allowed: int = Field(..., description="Máximo permitido pelo plano")
    remaining: int = Field(..., description="Quantos ainda pode seguir")
    by_position: dict[str, int] = Field(
        default_factory=dict,
        description="Quantidade por cargo (ex: DEPUTADO_FEDERAL: 2)"
    )
    by_state: dict[str, int] = Field(
        default_factory=dict,
        description="Quantidade por estado (ex: SP: 3, RJ: 1)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_following": 5,
                "max_allowed": 10,
                "remaining": 5,
                "by_position": {
                    "DEPUTADO_FEDERAL": 3,
                    "SENADOR": 2
                },
                "by_state": {
                    "SP": 3,
                    "RJ": 1,
                    "MG": 1
                }
            }
        }

