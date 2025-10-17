"""
Cliente Redis para cache e armazenamento temporário.
"""

import json
from typing import Optional, Any
from functools import wraps

import redis.asyncio as redis
from redis.exceptions import RedisError

from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RedisClient:
    """Cliente singleton para Redis."""
    
    _instance: Optional["RedisClient"] = None
    _redis: Optional[redis.Redis] = None
    
    def __new__(cls):
        """Implementa padrão singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa conexão com Redis."""
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("Cliente Redis inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar Redis: {str(e)}", exc_info=True)
                # Não levanta exceção - Redis é opcional
                self._redis = None
    
    @property
    def is_available(self) -> bool:
        """Verifica se Redis está disponível."""
        return self._redis is not None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Salva valor no Redis.
        
        Args:
            key: Chave
            value: Valor (será serializado em JSON)
            ttl: Time to live em segundos (opcional)
        
        Returns:
            True se salvou com sucesso
        """
        if not self.is_available:
            logger.debug("Redis não disponível, operação ignorada")
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            
            if ttl:
                await self._redis.setex(key, ttl, serialized)
            else:
                await self._redis.set(key, serialized)
            
            logger.debug(f"Cache salvo: {key} (TTL: {ttl}s)")
            return True
            
        except (RedisError, Exception) as e:
            logger.warning(f"Erro ao salvar no Redis: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Recupera valor do Redis.
        
        Args:
            key: Chave
        
        Returns:
            Valor deserializado ou None
        """
        if not self.is_available:
            return None
        
        try:
            value = await self._redis.get(key)
            
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            
            logger.debug(f"Cache miss: {key}")
            return None
            
        except (RedisError, Exception) as e:
            logger.warning(f"Erro ao ler do Redis: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Remove valor do Redis.
        
        Args:
            key: Chave
        
        Returns:
            True se removeu com sucesso
        """
        if not self.is_available:
            return False
        
        try:
            await self._redis.delete(key)
            logger.debug(f"Cache removido: {key}")
            return True
            
        except (RedisError, Exception) as e:
            logger.warning(f"Erro ao remover do Redis: {str(e)}")
            return False
    
    async def close(self):
        """Fecha conexão com Redis."""
        if self._redis:
            await self._redis.close()
            logger.info("Conexão Redis fechada")


# Instância singleton
_redis_client: Optional[RedisClient] = None


def get_redis() -> RedisClient:
    """
    Retorna instância singleton do cliente Redis.
    
    Returns:
        Instância do RedisClient
    """
    global _redis_client
    
    if _redis_client is None:
        _redis_client = RedisClient()
    
    return _redis_client


def cache(ttl: int = 3600, key_prefix: str = "brazyl"):
    """
    Decorator para cache de funções assíncronas.
    
    Args:
        ttl: Time to live em segundos (padrão: 1 hora)
        key_prefix: Prefixo da chave de cache
    
    Example:
        ```python
        @cache(ttl=1800, key_prefix="politicians")
        async def get_politician(politician_id: str):
            # Função será cacheada por 30 minutos
            ...
        ```
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis_client = get_redis()
            
            # Gera chave única baseada em função e argumentos
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Tenta obter do cache
            cached_value = await redis_client.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Retornando valor do cache: {cache_key}")
                return cached_value
            
            # Executa função
            result = await func(*args, **kwargs)
            
            # Salva no cache
            await redis_client.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator

