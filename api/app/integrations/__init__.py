"""
Integrations - clientes para APIs externas e serviços.
"""

from app.integrations.supabase_client import (
    SupabaseClient,
    SupabaseClientError,
    get_supabase,
)

from app.integrations.redis_client import (
    RedisClient,
    get_redis,
    cache,
)

from app.integrations.camara_api import (
    CamaraAPI,
    CamaraAPIError,
)

from app.integrations.senado_api import (
    SenadoAPI,
    SenadoAPIError,
)

from app.integrations.transparencia_api import (
    TransparenciaAPI,
    TransparenciaAPIError,
    AvisaAPI,
)

__all__ = [
    # Supabase
    "SupabaseClient",
    "SupabaseClientError",
    "get_supabase",
    # Redis
    "RedisClient",
    "get_redis",
    "cache",
    # Câmara
    "CamaraAPI",
    "CamaraAPIError",
    # Senado
    "SenadoAPI",
    "SenadoAPIError",
    # Transparência
    "TransparenciaAPI",
    "TransparenciaAPIError",
    # Avisa (WhatsApp)
    "AvisaAPI",
]
