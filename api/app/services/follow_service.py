"""
Service de Follows - Lógica de negócio para seguir políticos.
"""

from typing import Optional
from uuid import UUID

from app.integrations import get_supabase, SupabaseClientError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class FollowServiceError(Exception):
    """Exceção para erros do serviço de follows."""
    pass


class FollowService:
    """Service para operações de seguir políticos."""
    
    def __init__(self):
        """Inicializa o service."""
        self.supabase = get_supabase()
    
    async def follow_politician(
        self,
        user_id: UUID,
        politician_id: UUID
    ) -> dict:
        """
        Segue um político.
        
        Args:
            user_id: ID do usuário
            politician_id: ID do político
        
        Returns:
            Follow criado
        
        Raises:
            FollowServiceError: Se não puder seguir
        """
        try:
            logger.info(f"Seguindo político: user={user_id}, politician={politician_id}")
            
            # Verificar se usuário existe
            user = await self.supabase.client.table("users")\
                .select("id, plans(max_politicians)")\
                .eq("id", str(user_id))\
                .maybe_single()\
                .execute()
            
            if not user.data:
                raise FollowServiceError("Usuário não encontrado")
            
            # Verificar se político existe
            politician = await self.supabase.get_politician_by_id(str(politician_id))
            if not politician:
                raise FollowServiceError("Político não encontrado")
            
            # Verificar limite do plano
            max_politicians = user.data.get("plans", {}).get("max_politicians", 0)
            
            # Contar seguidores atuais
            follows, total = await self.supabase.get_user_follows(str(user_id), limit=1)
            
            if total >= max_politicians:
                raise FollowServiceError(
                    f"Limite de {max_politicians} políticos atingido. "
                    f"Faça upgrade do seu plano para seguir mais."
                )
            
            # Criar follow
            follow = await self.supabase.add_follow(str(user_id), str(politician_id))
            
            logger.info(f"Follow criado com sucesso: {follow['id']}")
            return follow
        
        except SupabaseClientError as e:
            if "já segue" in str(e).lower():
                raise FollowServiceError("Você já segue este político")
            
            logger.error(f"Erro ao seguir político: {str(e)}")
            raise FollowServiceError(f"Erro ao seguir político: {str(e)}")
    
    async def unfollow_politician(self, follow_id: UUID) -> bool:
        """
        Deixa de seguir um político.
        
        Args:
            follow_id: ID do follow
        
        Returns:
            True se removido com sucesso
        
        Raises:
            FollowServiceError: Se houver erro
        """
        try:
            logger.info(f"Removendo follow: {follow_id}")
            
            # Verificar se follow existe
            follow = await self.supabase.client.table("follows")\
                .select("id")\
                .eq("id", str(follow_id))\
                .maybe_single()\
                .execute()
            
            if not follow.data:
                raise FollowServiceError("Follow não encontrado")
            
            # Remover follow
            await self.supabase.remove_follow(str(follow_id))
            
            logger.info(f"Follow removido com sucesso: {follow_id}")
            return True
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao remover follow: {str(e)}")
            raise FollowServiceError(f"Erro ao remover follow: {str(e)}")
    
    async def get_user_follows(
        self,
        user_id: UUID,
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
            logger.info(f"Listando follows do usuário: {user_id}")
            
            follows, total = await self.supabase.get_user_follows(
                str(user_id),
                limit=limit,
                offset=offset
            )
            
            return follows, total
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao listar follows: {str(e)}")
            raise FollowServiceError(f"Erro ao listar follows: {str(e)}")
    
    async def get_follow_stats(self, user_id: UUID) -> dict:
        """
        Obtém estatísticas de follows de um usuário.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Estatísticas de follows
        """
        try:
            logger.info(f"Obtendo estatísticas de follows: {user_id}")
            
            # Buscar todos os follows (sem paginação para stats)
            follows, total = await self.supabase.get_user_follows(
                str(user_id),
                limit=1000,  # Assumindo que ninguém segue mais de 1000
                offset=0
            )
            
            # Buscar max_politicians do plano
            user = await self.supabase.client.table("users")\
                .select("plans(max_politicians)")\
                .eq("id", str(user_id))\
                .single()\
                .execute()
            
            max_allowed = user.data.get("plans", {}).get("max_politicians", 0)
            
            # Calcular estatísticas
            by_position = {}
            by_state = {}
            
            for follow in follows:
                politician = follow.get("politicians", {})
                
                position = politician.get("position", "UNKNOWN")
                state = politician.get("state", "XX")
                
                by_position[position] = by_position.get(position, 0) + 1
                by_state[state] = by_state.get(state, 0) + 1
            
            return {
                "total_following": total,
                "max_allowed": max_allowed,
                "remaining": max(0, max_allowed - total),
                "by_position": by_position,
                "by_state": by_state
            }
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            raise FollowServiceError(f"Erro ao obter estatísticas: {str(e)}")

