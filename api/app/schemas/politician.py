"""
Schemas Pydantic para Políticos.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr


class PoliticalPosition(str, Enum):
    """Cargos políticos."""
    DEPUTADO_FEDERAL = "DEPUTADO_FEDERAL"
    SENADOR = "SENADOR"
    DEPUTADO_ESTADUAL = "DEPUTADO_ESTADUAL"
    VEREADOR = "VEREADOR"


class SocialMedia(BaseModel):
    """Redes sociais do político."""
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None
    website: Optional[str] = None


class PoliticianBase(BaseModel):
    """Schema base de político."""
    name: str = Field(..., min_length=3, max_length=255, description="Nome completo")
    parliamentary_name: str = Field(..., min_length=2, max_length=255, description="Nome parlamentar")
    position: PoliticalPosition = Field(..., description="Cargo político")
    party: str = Field(..., min_length=2, max_length=50, description="Partido político")
    state: str = Field(..., pattern=r"^[A-Z]{2}$", description="UF do estado")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = Field(None, description="URL da foto oficial")
    biography: Optional[str] = Field(None, max_length=5000, description="Biografia")
    social_media: Optional[SocialMedia] = Field(default_factory=SocialMedia)


class PoliticianCreate(PoliticianBase):
    """Schema para criação de político (uso interno)."""
    external_id: Optional[str] = Field(None, description="ID da API pública (Câmara/Senado)")
    cpf: Optional[str] = Field(None, pattern=r"^\d{11}$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "external_id": "204534",
                "name": "João da Silva Santos",
                "parliamentary_name": "João Silva",
                "cpf": "12345678900",
                "position": "DEPUTADO_FEDERAL",
                "party": "PT",
                "state": "SP",
                "email": "joao@camara.leg.br",
                "phone": "+5561999999999",
                "photo_url": "https://example.com/photo.jpg",
                "biography": "Deputado federal por São Paulo desde 2019.",
                "social_media": {
                    "twitter": "@joaosilva",
                    "instagram": "@joaosilvaoficial"
                }
            }
        }


class PoliticianUpdate(BaseModel):
    """Schema para atualização de político."""
    parliamentary_name: Optional[str] = Field(None, min_length=2, max_length=255)
    party: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    biography: Optional[str] = Field(None, max_length=5000)
    social_media: Optional[SocialMedia] = None
    is_active: Optional[bool] = None


class PoliticianResponse(PoliticianBase):
    """Schema de resposta de político."""
    id: UUID
    external_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Campos computados
    followers_count: Optional[int] = Field(None, description="Número de seguidores no Brazyl")
    recent_events_count: Optional[int] = Field(None, description="Eventos recentes (últimos 30 dias)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "external_id": "204534",
                "name": "João da Silva Santos",
                "parliamentary_name": "João Silva",
                "position": "DEPUTADO_FEDERAL",
                "party": "PT",
                "state": "SP",
                "email": "joao@camara.leg.br",
                "phone": "+5561999999999",
                "photo_url": "https://example.com/photo.jpg",
                "biography": "Deputado federal por São Paulo desde 2019.",
                "social_media": {
                    "twitter": "@joaosilva",
                    "instagram": "@joaosilvaoficial"
                },
                "is_active": True,
                "followers_count": 1250,
                "recent_events_count": 45,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        }


class PoliticianListResponse(BaseModel):
    """Schema de resposta para lista de políticos."""
    success: bool = True
    data: list[PoliticianResponse]
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
                    "total": 513
                }
            }
        }


class PoliticianFilters(BaseModel):
    """Filtros para busca de políticos."""
    state: Optional[str] = Field(None, pattern=r"^[A-Z]{2}$", description="Filtrar por UF")
    party: Optional[str] = Field(None, min_length=2, max_length=50, description="Filtrar por partido")
    position: Optional[PoliticalPosition] = Field(None, description="Filtrar por cargo")
    name: Optional[str] = Field(None, min_length=2, description="Buscar por nome (parcial)")
    is_active: bool = Field(True, description="Apenas políticos ativos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "SP",
                "party": "PT",
                "position": "DEPUTADO_FEDERAL",
                "name": "João",
                "is_active": True
            }
        }

