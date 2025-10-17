"""
Cliente para API do Senado Federal.
Documentação: https://legis.senado.leg.br/dadosabertos/docs
"""

from typing import Optional, Any
from datetime import date
import asyncio

import httpx

from app.config import settings
from app.utils.logger import setup_logger
from app.integrations.redis_client import cache

logger = setup_logger(__name__)


class SenadoAPIError(Exception):
    """Exceção para erros da API do Senado."""
    pass


class SenadoAPI:
    """Cliente para API do Senado Federal."""
    
    def __init__(self):
        """Inicializa o cliente."""
        self.base_url = str(settings.senado_api_url)
        self.timeout = 30.0
        self._semaphore = asyncio.Semaphore(10)  # Máx 10 requisições paralelas
    
    async def _request(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        retry: int = 3
    ) -> dict[str, Any]:
        """
        Faz requisição para a API com retry.
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros query string
            retry: Número de tentativas
        
        Returns:
            Resposta JSON
        """
        url = f"{self.base_url}{endpoint}"
        
        async with self._semaphore:  # Rate limiting
            for attempt in range(retry):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        logger.debug(f"Requisição Senado API: {endpoint}", extra={"params": params})
                        
                        response = await client.get(url, params=params)
                        response.raise_for_status()
                        
                        # API do Senado retorna XML por padrão, mas aceita JSON com header
                        headers = {"Accept": "application/json"}
                        response = await client.get(url, params=params, headers=headers)
                        response.raise_for_status()
                        
                        data = response.json()
                        logger.debug(f"Resposta Senado API: {endpoint} - Status {response.status_code}")
                        
                        return data
                
                except httpx.HTTPStatusError as e:
                    logger.warning(
                        f"Erro HTTP na Senado API (tentativa {attempt + 1}/{retry}): {e.response.status_code}",
                        extra={"endpoint": endpoint}
                    )
                    
                    if e.response.status_code == 404:
                        raise SenadoAPIError(f"Recurso não encontrado: {endpoint}")
                    
                    if attempt < retry - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise SenadoAPIError(f"Erro HTTP {e.response.status_code}: {endpoint}")
                
                except httpx.RequestError as e:
                    logger.warning(
                        f"Erro de conexão na Senado API (tentativa {attempt + 1}/{retry}): {str(e)}",
                        extra={"endpoint": endpoint}
                    )
                    
                    if attempt < retry - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise SenadoAPIError(f"Erro de conexão: {str(e)}")
        
        raise SenadoAPIError(f"Falha após {retry} tentativas")
    
    @cache(ttl=3600, key_prefix="senado:senadores")
    async def get_senadores(
        self,
        uf: Optional[str] = None,
        partido: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Lista senadores em exercício.
        
        Args:
            uf: Sigla da UF (ex: SP, RJ)
            partido: Sigla do partido (ex: PT, PSDB)
        
        Returns:
            Dados dos senadores
        """
        params = {}
        if uf:
            params["uf"] = uf.upper()
        if partido:
            params["partido"] = partido.upper()
        
        logger.info(f"Buscando senadores: UF={uf}, Partido={partido}")
        
        try:
            response = await self._request("/senador/lista/atual", params=params)
            
            # Estrutura da resposta do Senado é diferente
            senadores_data = response.get("ListaParlamentarEmExercicio", {}).get("Parlamentares", {}).get("Parlamentar", [])
            
            if not isinstance(senadores_data, list):
                senadores_data = [senadores_data] if senadores_data else []
            
            logger.info(f"Encontrados {len(senadores_data)} senadores")
            return {"dados": senadores_data}
            
        except SenadoAPIError as e:
            logger.error(f"Erro ao buscar senadores: {str(e)}")
            raise
    
    @cache(ttl=3600, key_prefix="senado:senador")
    async def get_senador(self, senador_id: int) -> dict[str, Any]:
        """
        Obtém detalhes de um senador específico.
        
        Args:
            senador_id: ID (código) do senador
        
        Returns:
            Dados completos do senador
        """
        logger.info(f"Buscando senador: {senador_id}")
        
        try:
            response = await self._request(f"/senador/{senador_id}")
            
            senador_data = response.get("DetalheParlamentar", {}).get("Parlamentar", {})
            
            logger.info(f"Senador encontrado: {senador_data.get('NomeCompletoParlamentar')}")
            return senador_data
            
        except SenadoAPIError as e:
            logger.error(f"Erro ao buscar senador {senador_id}: {str(e)}")
            raise
    
    @cache(ttl=1800, key_prefix="senado:votacoes")
    async def get_votacoes(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> dict[str, Any]:
        """
        Lista votações do Senado.
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
        
        Returns:
            Dados das votações
        """
        params = {}
        
        if data_inicio:
            params["dataInicio"] = data_inicio.strftime("%Y%m%d")
        if data_fim:
            params["dataFim"] = data_fim.strftime("%Y%m%d")
        
        logger.info(f"Buscando votações: {data_inicio} a {data_fim}")
        
        try:
            response = await self._request("/votacao/lista", params=params)
            
            votacoes_data = response.get("ListaVotacoes", {}).get("Votacoes", {}).get("Votacao", [])
            
            if not isinstance(votacoes_data, list):
                votacoes_data = [votacoes_data] if votacoes_data else []
            
            logger.info(f"Encontradas {len(votacoes_data)} votações")
            return {"dados": votacoes_data}
            
        except SenadoAPIError as e:
            logger.error(f"Erro ao buscar votações: {str(e)}")
            raise
    
    async def get_voto_senador(
        self,
        votacao_id: str,
        senador_id: int
    ) -> Optional[dict[str, Any]]:
        """
        Obtém voto de um senador em votação específica.
        
        Args:
            votacao_id: ID da votação
            senador_id: ID do senador
        
        Returns:
            Dados do voto ou None
        """
        logger.info(f"Buscando voto: votação={votacao_id}, senador={senador_id}")
        
        try:
            response = await self._request(f"/votacao/{votacao_id}")
            
            votacao_data = response.get("VotacaoDetalhe", {}).get("Votacao", {})
            votos = votacao_data.get("Votos", {}).get("Voto", [])
            
            if not isinstance(votos, list):
                votos = [votos] if votos else []
            
            # Procura voto do senador
            for voto in votos:
                if str(voto.get("CodigoParlamentar")) == str(senador_id):
                    logger.info(f"Voto encontrado: {voto.get('Voto')}")
                    return voto
            
            logger.info(f"Voto não encontrado para senador {senador_id}")
            return None
            
        except SenadoAPIError as e:
            logger.error(f"Erro ao buscar voto: {str(e)}")
            return None
    
    def normalize_senador(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Normaliza dados do senador para formato padrão Brazyl.
        
        Args:
            data: Dados raw da API
        
        Returns:
            Dados normalizados
        """
        identificacao = data.get("IdentificacaoParlamentar", {})
        
        return {
            "external_id": str(identificacao.get("CodigoParlamentar")),
            "name": identificacao.get("NomeCompletoParlamentar", ""),
            "parliamentary_name": identificacao.get("NomeParlamentar", ""),
            "cpf": None,  # API do Senado não fornece CPF
            "position": "SENADOR",
            "party": identificacao.get("SiglaPartidoParlamentar", ""),
            "state": identificacao.get("UfParlamentar", ""),
            "email": identificacao.get("EmailParlamentar"),
            "photo_url": identificacao.get("UrlFotoParlamentar"),
            "biography": None,  # Poderia buscar em outro endpoint
            "social_media": {
                "website": identificacao.get("UrlPaginaParlamentar"),
                "twitter": None,
                "facebook": None,
                "instagram": None
            }
        }

