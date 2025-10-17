"""
Service de Políticos - Lógica de negócio relacionada a políticos.
"""

from typing import Optional
from uuid import UUID

from app.integrations import get_supabase, SupabaseClientError
from app.integrations import CamaraAPI, SenadoAPI
from app.schemas.politician import PoliticianFilters, PoliticalPosition
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class PoliticianServiceError(Exception):
    """Exceção para erros do serviço de políticos."""
    pass


class PoliticianService:
    """Service para operações com políticos."""
    
    def __init__(self):
        """Inicializa o service."""
        self.supabase = get_supabase()
        self.camara = CamaraAPI()
        self.senado = SenadoAPI()
    
    async def get_politicians(
        self,
        filters: Optional[PoliticianFilters] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        Lista políticos com filtros.
        
        Args:
            filters: Filtros de busca
            limit: Limite de resultados
            offset: Offset para paginação
        
        Returns:
            Tupla (lista de políticos, total)
        """
        try:
            filter_dict = {}
            
            if filters:
                if filters.state:
                    filter_dict["state"] = filters.state
                if filters.party:
                    filter_dict["party"] = filters.party
                if filters.position:
                    filter_dict["position"] = filters.position.value
                if filters.name:
                    filter_dict["name"] = filters.name
                filter_dict["is_active"] = filters.is_active
            
            logger.info(f"Listando políticos: filtros={filter_dict}")
            
            politicians, total = await self.supabase.get_politicians(
                filters=filter_dict,
                limit=limit,
                offset=offset
            )
            
            # Adicionar contagem de seguidores (opcional, pode ser pesado)
            # for politician in politicians:
            #     politician['followers_count'] = await self._count_followers(politician['id'])
            
            return politicians, total
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao listar políticos: {str(e)}")
            raise PoliticianServiceError(f"Erro ao listar políticos: {str(e)}")
    
    async def get_politician_by_id(self, politician_id: UUID) -> Optional[dict]:
        """
        Obtém político por ID.
        
        Args:
            politician_id: ID do político
        
        Returns:
            Dados do político ou None
        """
        try:
            logger.info(f"Buscando político: {politician_id}")
            
            politician = await self.supabase.get_politician_by_id(str(politician_id))
            
            if politician:
                # Adicionar estatísticas
                politician["followers_count"] = await self._count_followers(str(politician_id))
                politician["recent_events_count"] = await self._count_recent_events(str(politician_id))
            
            return politician
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao buscar político: {str(e)}")
            return None
    
    async def get_politician_history(
        self,
        politician_id: UUID,
        event_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        Obtém histórico de eventos de um político.
        
        Args:
            politician_id: ID do político
            event_type: Tipo de evento (opcional)
            limit: Limite de resultados
            offset: Offset para paginação
        
        Returns:
            Tupla (lista de eventos, total)
        """
        try:
            logger.info(f"Buscando histórico do político {politician_id}")
            
            events, total = await self.supabase.get_political_events(
                politician_id=str(politician_id),
                event_type=event_type,
                limit=limit,
                offset=offset
            )
            
            return events, total
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao buscar histórico: {str(e)}")
            raise PoliticianServiceError(f"Erro ao buscar histórico: {str(e)}")
    
    async def sync_politician_from_api(
        self,
        external_id: str,
        position: PoliticalPosition
    ) -> dict:
        """
        Sincroniza dados de um político das APIs públicas.
        
        Args:
            external_id: ID externo (Câmara ou Senado)
            position: Cargo do político
        
        Returns:
            Dados do político sincronizado
        
        Raises:
            PoliticianServiceError: Se houver erro na sincronização
        """
        try:
            logger.info(f"Sincronizando político: {external_id} ({position})")
            
            # Buscar dados da API apropriada
            if position == PoliticalPosition.DEPUTADO_FEDERAL:
                raw_data = await self.camara.get_deputado(int(external_id))
                normalized_data = self.camara.normalize_deputado(raw_data)
            
            elif position == PoliticalPosition.SENADOR:
                raw_data = await self.senado.get_senador(int(external_id))
                normalized_data = self.senado.normalize_senador(raw_data)
            
            else:
                raise PoliticianServiceError(f"Tipo de político não suportado: {position}")
            
            # Verificar se já existe no banco
            existing = await self.supabase.client.table("politicians")\
                .select("id")\
                .eq("external_id", external_id)\
                .maybe_single()\
                .execute()
            
            if existing.data:
                # Atualizar existente
                logger.info(f"Atualizando político existente: {external_id}")
                
                politician = await self.supabase.client.table("politicians")\
                    .update(normalized_data)\
                    .eq("external_id", external_id)\
                    .execute()
                
                return politician.data[0]
            else:
                # Criar novo
                logger.info(f"Criando novo político: {external_id}")
                politician = await self.supabase.create_politician(normalized_data)
                return politician
        
        except (SupabaseClientError, Exception) as e:
            logger.error(f"Erro ao sincronizar político: {str(e)}")
            raise PoliticianServiceError(f"Erro ao sincronizar político: {str(e)}")
    
    async def _count_followers(self, politician_id: str) -> int:
        """Conta seguidores de um político."""
        try:
            response = await self.supabase.client.table("follows")\
                .select("id", count="exact")\
                .eq("politician_id", politician_id)\
                .execute()
            
            return response.count or 0
        except Exception:
            return 0
    
    async def _count_recent_events(self, politician_id: str, days: int = 30) -> int:
        """Conta eventos recentes de um político."""
        try:
            from datetime import datetime, timedelta
            
            date_limit = (datetime.now() - timedelta(days=days)).date()
            
            response = await self.supabase.client.table("political_events")\
                .select("id", count="exact")\
                .eq("politician_id", politician_id)\
                .gte("event_date", date_limit.isoformat())\
                .execute()
            
            return response.count or 0
        except Exception:
            return 0

