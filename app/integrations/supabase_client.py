"""
Cliente Supabase para interações com o banco de dados.
Implementa padrão singleton e cache com Redis.
"""

import json
from typing import Optional, Any
from functools import wraps
import asyncio

from supabase import create_client, Client
from postgrest.exceptions import APIError

from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SupabaseClientError(Exception):
    """Exceção customizada para erros do Supabase."""
    pass


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator para tentar novamente em caso de falha.
    
    Args:
        max_retries: Número máximo de tentativas
        delay: Delay entre tentativas (em segundos)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (APIError, Exception) as e:
                    last_exception = e
                    logger.warning(
                        f"Tentativa {attempt + 1}/{max_retries} falhou: {str(e)}",
                        extra={"function": func.__name__, "attempt": attempt + 1}
                    )
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))  # Backoff exponencial
            
            logger.error(
                f"Todas as {max_retries} tentativas falharam",
                extra={"function": func.__name__},
                exc_info=True
            )
            raise SupabaseClientError(f"Falha após {max_retries} tentativas: {str(last_exception)}")
        
        return wrapper
    return decorator


class SupabaseClient:
    """
    Cliente singleton para interação com Supabase.
    """
    
    _instance: Optional["SupabaseClient"] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Implementa padrão singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa o cliente Supabase."""
        if self._client is None:
            try:
                self._client = create_client(
                    supabase_url=str(settings.supabase_url),
                    supabase_key=settings.supabase_service_key  # Service key para operações admin
                )
                logger.info("Cliente Supabase inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente Supabase: {str(e)}", exc_info=True)
                raise SupabaseClientError(f"Falha ao conectar com Supabase: {str(e)}")
    
    @property
    def client(self) -> Client:
        """Retorna o cliente Supabase."""
        if self._client is None:
            raise SupabaseClientError("Cliente Supabase não inicializado")
        return self._client
    
    # ========================================
    # USERS
    # ========================================
    
    @retry_on_failure(max_retries=3)
    async def get_user_by_whatsapp(self, whatsapp: str) -> Optional[dict]:
        """
        Busca usuário por número de WhatsApp.
        
        Args:
            whatsapp: Número de WhatsApp no formato +5511999999999
        
        Returns:
            Dados do usuário ou None se não encontrado
        """
        try:
            logger.info(f"Buscando usuário por WhatsApp: {whatsapp}")
            
            response = self.client.table("users")\
                .select("*, plans(*)")\
                .eq("whatsapp_number", whatsapp)\
                .maybe_single()\
                .execute()
            
            if response.data:
                logger.info(f"Usuário encontrado: {response.data.get('id')}")
                return response.data
            
            logger.info(f"Usuário não encontrado para WhatsApp: {whatsapp}")
            return None
            
        except APIError as e:
            logger.error(f"Erro ao buscar usuário: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao buscar usuário: {str(e)}")
    
    @retry_on_failure(max_retries=3)
    async def create_user(self, user_data: dict) -> dict:
        """
        Cria um novo usuário.
        
        Args:
            user_data: Dados do usuário
        
        Returns:
            Usuário criado
        """
        try:
            logger.info(f"Criando usuário: {user_data.get('name')}")
            
            response = self.client.table("users")\
                .insert(user_data)\
                .execute()
            
            if response.data:
                created_user = response.data[0]
                logger.info(f"Usuário criado com sucesso: {created_user.get('id')}")
                return created_user
            
            raise SupabaseClientError("Falha ao criar usuário: resposta vazia")
            
        except APIError as e:
            logger.error(f"Erro ao criar usuário: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao criar usuário: {str(e)}")
    
    @retry_on_failure(max_retries=3)
    async def update_user(self, user_id: str, user_data: dict) -> dict:
        """
        Atualiza dados de um usuário.
        
        Args:
            user_id: ID do usuário
            user_data: Dados a atualizar
        
        Returns:
            Usuário atualizado
        """
        try:
            logger.info(f"Atualizando usuário: {user_id}")
            
            response = self.client.table("users")\
                .update(user_data)\
                .eq("id", user_id)\
                .execute()
            
            if response.data:
                updated_user = response.data[0]
                logger.info(f"Usuário atualizado com sucesso: {user_id}")
                return updated_user
            
            raise SupabaseClientError(f"Usuário não encontrado: {user_id}")
            
        except APIError as e:
            logger.error(f"Erro ao atualizar usuário: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao atualizar usuário: {str(e)}")
    
    # ========================================
    # POLITICIANS
    # ========================================
    
    @retry_on_failure(max_retries=3)
    async def get_politicians(
        self,
        filters: Optional[dict] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        Busca políticos com filtros opcionais.
        
        Args:
            filters: Filtros (state, party, position, name, is_active)
            limit: Limite de resultados
            offset: Offset para paginação
        
        Returns:
            Tupla (lista de políticos, total)
        """
        try:
            filters = filters or {}
            logger.info(f"Buscando políticos com filtros: {filters}")
            
            query = self.client.table("politicians").select("*", count="exact")
            
            # Aplicar filtros
            if filters.get("state"):
                query = query.eq("state", filters["state"])
            if filters.get("party"):
                query = query.eq("party", filters["party"])
            if filters.get("position"):
                query = query.eq("position", filters["position"])
            if filters.get("name"):
                query = query.ilike("parliamentary_name", f"%{filters['name']}%")
            if "is_active" in filters:
                query = query.eq("is_active", filters["is_active"])
            
            # Paginação e ordenação
            response = query\
                .order("parliamentary_name")\
                .range(offset, offset + limit - 1)\
                .execute()
            
            total = response.count or 0
            politicians = response.data or []
            
            logger.info(f"Encontrados {len(politicians)} políticos (total: {total})")
            return politicians, total
            
        except APIError as e:
            logger.error(f"Erro ao buscar políticos: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao buscar políticos: {str(e)}")
    
    @retry_on_failure(max_retries=3)
    async def get_politician_by_id(self, politician_id: str) -> Optional[dict]:
        """
        Busca político por ID.
        
        Args:
            politician_id: ID do político
        
        Returns:
            Dados do político ou None
        """
        try:
            logger.info(f"Buscando político por ID: {politician_id}")
            
            response = self.client.table("politicians")\
                .select("*")\
                .eq("id", politician_id)\
                .maybe_single()\
                .execute()
            
            if response.data:
                logger.info(f"Político encontrado: {response.data.get('parliamentary_name')}")
                return response.data
            
            logger.warning(f"Político não encontrado: {politician_id}")
            return None
            
        except APIError as e:
            logger.error(f"Erro ao buscar político: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao buscar político: {str(e)}")
    
    @retry_on_failure(max_retries=3)
    async def create_politician(self, politician_data: dict) -> dict:
        """
        Cria um novo político.
        
        Args:
            politician_data: Dados do político
        
        Returns:
            Político criado
        """
        try:
            logger.info(f"Criando político: {politician_data.get('parliamentary_name')}")
            
            response = self.client.table("politicians")\
                .insert(politician_data)\
                .execute()
            
            if response.data:
                created = response.data[0]
                logger.info(f"Político criado: {created.get('id')}")
                return created
            
            raise SupabaseClientError("Falha ao criar político: resposta vazia")
            
        except APIError as e:
            logger.error(f"Erro ao criar político: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao criar político: {str(e)}")
    
    # ========================================
    # FOLLOWS
    # ========================================
    
    @retry_on_failure(max_retries=3)
    async def add_follow(self, user_id: str, politician_id: str) -> dict:
        """
        Adiciona um follow (usuário segue político).
        
        Args:
            user_id: ID do usuário
            politician_id: ID do político
        
        Returns:
            Follow criado
        """
        try:
            logger.info(f"Criando follow: user={user_id}, politician={politician_id}")
            
            response = self.client.table("follows")\
                .insert({"user_id": user_id, "politician_id": politician_id})\
                .execute()
            
            if response.data:
                follow = response.data[0]
                logger.info(f"Follow criado: {follow.get('id')}")
                return follow
            
            raise SupabaseClientError("Falha ao criar follow: resposta vazia")
            
        except APIError as e:
            # Verifica se é erro de duplicação
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                logger.warning(f"Follow já existe: user={user_id}, politician={politician_id}")
                raise SupabaseClientError("Você já segue este político")
            
            logger.error(f"Erro ao criar follow: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao criar follow: {str(e)}")
    
    @retry_on_failure(max_retries=3)
    async def remove_follow(self, follow_id: str) -> bool:
        """
        Remove um follow.
        
        Args:
            follow_id: ID do follow
        
        Returns:
            True se removido com sucesso
        """
        try:
            logger.info(f"Removendo follow: {follow_id}")
            
            response = self.client.table("follows")\
                .delete()\
                .eq("id", follow_id)\
                .execute()
            
            logger.info(f"Follow removido: {follow_id}")
            return True
            
        except APIError as e:
            logger.error(f"Erro ao remover follow: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao remover follow: {str(e)}")
    
    @retry_on_failure(max_retries=3)
    async def get_user_follows(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        Lista políticos seguidos por um usuário.
        
        Args:
            user_id: ID do usuário
            limit: Limite de resultados
            offset: Offset para paginação
        
        Returns:
            Tupla (lista de follows, total)
        """
        try:
            logger.info(f"Buscando follows do usuário: {user_id}")
            
            response = self.client.table("follows")\
                .select("*, politicians(*)", count="exact")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            total = response.count or 0
            follows = response.data or []
            
            logger.info(f"Encontrados {len(follows)} follows (total: {total})")
            return follows, total
            
        except APIError as e:
            logger.error(f"Erro ao buscar follows: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao buscar follows: {str(e)}")
    
    # ========================================
    # NOTIFICATIONS
    # ========================================
    
    @retry_on_failure(max_retries=3)
    async def create_notification(self, notification_data: dict) -> dict:
        """
        Cria uma notificação.
        
        Args:
            notification_data: Dados da notificação
        
        Returns:
            Notificação criada
        """
        try:
            logger.info(f"Criando notificação para usuário: {notification_data.get('user_id')}")
            
            response = self.client.table("notifications")\
                .insert(notification_data)\
                .execute()
            
            if response.data:
                notification = response.data[0]
                logger.info(f"Notificação criada: {notification.get('id')}")
                return notification
            
            raise SupabaseClientError("Falha ao criar notificação: resposta vazia")
            
        except APIError as e:
            logger.error(f"Erro ao criar notificação: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao criar notificação: {str(e)}")
    
    @retry_on_failure(max_retries=3)
    async def update_notification_status(
        self,
        notification_id: str,
        status: str,
        **kwargs
    ) -> dict:
        """
        Atualiza status de uma notificação.
        
        Args:
            notification_id: ID da notificação
            status: Novo status (PENDING, SENT, DELIVERED, FAILED)
            **kwargs: Campos adicionais (sent_at, delivered_at, error_message)
        
        Returns:
            Notificação atualizada
        """
        try:
            logger.info(f"Atualizando status da notificação {notification_id} para {status}")
            
            update_data = {"status": status, **kwargs}
            
            response = self.client.table("notifications")\
                .update(update_data)\
                .eq("id", notification_id)\
                .execute()
            
            if response.data:
                notification = response.data[0]
                logger.info(f"Notificação atualizada: {notification_id}")
                return notification
            
            raise SupabaseClientError(f"Notificação não encontrada: {notification_id}")
            
        except APIError as e:
            logger.error(f"Erro ao atualizar notificação: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao atualizar notificação: {str(e)}")
    
    # ========================================
    # POLITICAL EVENTS
    # ========================================
    
    @retry_on_failure(max_retries=3)
    async def get_political_events(
        self,
        politician_id: str,
        event_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        Busca eventos políticos de um político.
        
        Args:
            politician_id: ID do político
            event_type: Tipo de evento (opcional)
            limit: Limite de resultados
            offset: Offset para paginação
        
        Returns:
            Tupla (lista de eventos, total)
        """
        try:
            logger.info(f"Buscando eventos do político {politician_id}")
            
            query = self.client.table("political_events")\
                .select("*", count="exact")\
                .eq("politician_id", politician_id)
            
            if event_type:
                query = query.eq("event_type", event_type)
            
            response = query\
                .order("event_date", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            total = response.count or 0
            events = response.data or []
            
            logger.info(f"Encontrados {len(events)} eventos (total: {total})")
            return events, total
            
        except APIError as e:
            logger.error(f"Erro ao buscar eventos: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao buscar eventos: {str(e)}")
    
    @retry_on_failure(max_retries=3)
    async def create_political_event(self, event_data: dict) -> dict:
        """
        Cria um evento político.
        
        Args:
            event_data: Dados do evento
        
        Returns:
            Evento criado
        """
        try:
            logger.info(f"Criando evento político: {event_data.get('title')}")
            
            response = self.client.table("political_events")\
                .insert(event_data)\
                .execute()
            
            if response.data:
                event = response.data[0]
                logger.info(f"Evento criado: {event.get('id')}")
                return event
            
            raise SupabaseClientError("Falha ao criar evento: resposta vazia")
            
        except APIError as e:
            logger.error(f"Erro ao criar evento: {str(e)}", exc_info=True)
            raise SupabaseClientError(f"Erro ao criar evento: {str(e)}")


# Instância singleton global
_supabase_client: Optional[SupabaseClient] = None


def get_supabase() -> SupabaseClient:
    """
    Retorna a instância singleton do cliente Supabase.
    
    Returns:
        Instância do SupabaseClient
    
    Example:
        ```python
        from app.integrations.supabase_client import get_supabase
        
        supabase = get_supabase()
        user = await supabase.get_user_by_whatsapp("+5511999999999")
        ```
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    
    return _supabase_client

