"""
Configurações da aplicação usando Pydantic Settings.
Todas as variáveis de ambiente são carregadas e validadas aqui.
"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl


class Settings(BaseSettings):
    """Configurações globais da aplicação Brazyl."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    environment: Literal["dev", "staging", "prod"] = Field(
        default="dev",
        description="Ambiente de execução"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Nível de logging"
    )
    api_key: str = Field(
        ...,
        description="Chave de API para autenticação interna (N8N)"
    )
    
    # Supabase
    supabase_url: HttpUrl = Field(
        ...,
        description="URL do projeto Supabase"
    )
    supabase_anon_key: str = Field(
        ...,
        description="Chave anônima do Supabase"
    )
    supabase_service_key: str = Field(
        ...,
        description="Service role key do Supabase (admin)"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexão do Redis"
    )
    
    # Avisa API (WhatsApp)
    avisa_api_url: HttpUrl = Field(
        ...,
        description="URL base da API Avisa"
    )
    avisa_api_token: str = Field(
        ...,
        description="Token de autenticação da API Avisa"
    )
    
    # APIs Externas
    camara_api_url: HttpUrl = Field(
        default="https://dadosabertos.camara.leg.br/api/v2",
        description="URL da API da Câmara dos Deputados"
    )
    senado_api_url: HttpUrl = Field(
        default="https://legis.senado.leg.br/dadosabertos",
        description="URL da API do Senado Federal"
    )
    transparencia_api_url: HttpUrl = Field(
        default="http://www.portaltransparencia.gov.br/api-de-dados",
        description="URL da API do Portal da Transparência"
    )
    
    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5678"],
        description="Origens permitidas para CORS"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="Limite de requisições por minuto"
    )
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return self.environment == "dev"
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção."""
        return self.environment == "prod"


# Instância global de configurações
settings = Settings()

