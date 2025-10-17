"""
Schemas Pydantic para Usuários.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, field_validator


class PlanType(str, Enum):
    """Tipos de planos disponíveis."""
    FREE = "FREE"
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"


class UserPreferences(BaseModel):
    """Preferências do usuário."""
    notification_enabled: bool = Field(default=True, description="Se notificações estão ativas")
    notification_hour: int = Field(default=8, ge=0, le=23, description="Hora preferencial para notificações")
    event_types: list[str] = Field(default_factory=list, description="Tipos de eventos que deseja receber")


class UserBase(BaseModel):
    """Schema base de usuário."""
    whatsapp_number: str = Field(
        ...,
        description="Número de WhatsApp no formato +5511999999999",
        pattern=r"^\+55\d{2}9\d{8}$"
    )
    name: str = Field(..., min_length=3, max_length=255, description="Nome completo do usuário")
    email: Optional[EmailStr] = Field(None, description="E-mail do usuário")
    cpf: Optional[str] = Field(None, pattern=r"^\d{11}$", description="CPF apenas números")


class UserCreate(UserBase):
    """Schema para criação de usuário."""
    plan_type: PlanType = Field(default=PlanType.FREE, description="Tipo de plano inicial")
    preferences: Optional[UserPreferences] = Field(default_factory=UserPreferences)
    
    class Config:
        json_schema_extra = {
            "example": {
                "whatsapp_number": "+5511999999999",
                "name": "João da Silva",
                "email": "joao@example.com",
                "cpf": "12345678900",
                "plan_type": "FREE"
            }
        }


class UserUpdate(BaseModel):
    """Schema para atualização de usuário."""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    cpf: Optional[str] = Field(None, pattern=r"^\d{11}$")
    preferences: Optional[UserPreferences] = None
    is_active: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "João da Silva Souza",
                "email": "joao.novo@example.com",
                "preferences": {
                    "notification_enabled": True,
                    "notification_hour": 9,
                    "event_types": ["VOTACAO", "DESPESA"]
                }
            }
        }


class PlanResponse(BaseModel):
    """Schema de resposta de plano."""
    id: UUID
    name: str
    type: PlanType
    max_politicians: int
    notification_frequency: str
    price: float
    features: Optional[dict] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """Schema de resposta completo de usuário."""
    id: UUID
    plan: Optional[PlanResponse] = None
    is_active: bool
    preferences: UserPreferences
    created_at: datetime
    updated_at: datetime
    last_interaction_at: Optional[datetime] = None
    
    # Campos computados
    following_count: Optional[int] = Field(None, description="Quantidade de políticos seguidos")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "whatsapp_number": "+5511999999999",
                "name": "João da Silva",
                "email": "joao@example.com",
                "cpf": "12345678900",
                "plan": {
                    "id": "660e8400-e29b-41d4-a716-446655440000",
                    "name": "Gratuito",
                    "type": "FREE",
                    "max_politicians": 3,
                    "notification_frequency": "weekly",
                    "price": 0.0,
                    "features": {}
                },
                "is_active": True,
                "preferences": {
                    "notification_enabled": True,
                    "notification_hour": 8,
                    "event_types": ["VOTACAO"]
                },
                "following_count": 2,
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z",
                "last_interaction_at": "2024-01-15T14:30:00Z"
            }
        }


class UserListResponse(BaseModel):
    """Schema de resposta para lista de usuários."""
    success: bool = True
    data: list[UserResponse]
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
                    "total": 150
                }
            }
        }

