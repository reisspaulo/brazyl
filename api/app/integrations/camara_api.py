"""
Cliente para API da Câmara dos Deputados.
Documentação: https://dadosabertos.camara.leg.br/swagger/api.html
"""

from typing import Optional, Any
from datetime import date
import asyncio

import httpx

from app.config import settings
from app.utils.logger import setup_logger
from app.integrations.redis_client import cache

logger = setup_logger(__name__)


class CamaraAPIError(Exception):
    """Exceção para erros da API da Câmara."""
    pass


class CamaraAPI:
    """Cliente para API da Câmara dos Deputados."""
    
    def __init__(self):
        """Inicializa o cliente."""
        self.base_url = str(settings.camara_api_url)
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
            endpoint: Endpoint da API (ex: /deputados)
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
                        logger.debug(f"Requisição Câmara API: {endpoint}", extra={"params": params})
                        
                        response = await client.get(url, params=params)
                        response.raise_for_status()
                        
                        data = response.json()
                        logger.debug(f"Resposta Câmara API: {endpoint} - Status {response.status_code}")
                        
                        return data
                
                except httpx.HTTPStatusError as e:
                    logger.warning(
                        f"Erro HTTP na Câmara API (tentativa {attempt + 1}/{retry}): {e.response.status_code}",
                        extra={"endpoint": endpoint, "status": e.response.status_code}
                    )
                    
                    if e.response.status_code == 404:
                        raise CamaraAPIError(f"Recurso não encontrado: {endpoint}")
                    
                    if attempt < retry - 1:
                        await asyncio.sleep(2 ** attempt)  # Backoff exponencial
                    else:
                        raise CamaraAPIError(f"Erro HTTP {e.response.status_code}: {endpoint}")
                
                except httpx.RequestError as e:
                    logger.warning(
                        f"Erro de conexão na Câmara API (tentativa {attempt + 1}/{retry}): {str(e)}",
                        extra={"endpoint": endpoint}
                    )
                    
                    if attempt < retry - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise CamaraAPIError(f"Erro de conexão: {str(e)}")
        
        raise CamaraAPIError(f"Falha após {retry} tentativas")
    
    @cache(ttl=3600, key_prefix="camara:deputados")
    async def get_deputados(
        self,
        uf: Optional[str] = None,
        partido: Optional[str] = None,
        nome: Optional[str] = None,
        pagina: int = 1,
        itens: int = 100
    ) -> dict[str, Any]:
        """
        Lista deputados federais.
        
        Args:
            uf: Sigla da UF (ex: SP, RJ)
            partido: Sigla do partido (ex: PT, PSDB)
            nome: Nome do deputado (busca parcial)
            pagina: Número da página
            itens: Itens por página (máx 100)
        
        Returns:
            Dados dos deputados
        
        Example:
            ```python
            camara = CamaraAPI()
            deputados = await camara.get_deputados(uf="SP", partido="PT")
            ```
        """
        params = {
            "pagina": pagina,
            "itens": min(itens, 100),
            "ordem": "ASC",
            "ordenarPor": "nome"
        }
        
        if uf:
            params["siglaUf"] = uf.upper()
        if partido:
            params["siglaPartido"] = partido.upper()
        if nome:
            params["nome"] = nome
        
        logger.info(f"Buscando deputados: UF={uf}, Partido={partido}")
        
        try:
            response = await self._request("/deputados", params=params)
            deputados = response.get("dados", [])
            
            logger.info(f"Encontrados {len(deputados)} deputados")
            return response
            
        except CamaraAPIError as e:
            logger.error(f"Erro ao buscar deputados: {str(e)}")
            raise
    
    @cache(ttl=3600, key_prefix="camara:deputado")
    async def get_deputado(self, deputado_id: int) -> dict[str, Any]:
        """
        Obtém detalhes de um deputado específico.
        
        Args:
            deputado_id: ID do deputado
        
        Returns:
            Dados completos do deputado
        """
        logger.info(f"Buscando deputado: {deputado_id}")
        
        try:
            response = await self._request(f"/deputados/{deputado_id}")
            deputado = response.get("dados", {})
            
            logger.info(f"Deputado encontrado: {deputado.get('nomeCivil')}")
            return deputado
            
        except CamaraAPIError as e:
            logger.error(f"Erro ao buscar deputado {deputado_id}: {str(e)}")
            raise
    
    @cache(ttl=1800, key_prefix="camara:votacoes")
    async def get_votacoes(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        pagina: int = 1,
        itens: int = 100
    ) -> dict[str, Any]:
        """
        Lista votações da Câmara.
        
        Args:
            data_inicio: Data inicial (YYYY-MM-DD)
            data_fim: Data final (YYYY-MM-DD)
            pagina: Número da página
            itens: Itens por página
        
        Returns:
            Dados das votações
        """
        params = {
            "pagina": pagina,
            "itens": min(itens, 100),
            "ordem": "DESC",
            "ordenarPor": "dataHoraRegistro"
        }
        
        if data_inicio:
            params["dataInicio"] = data_inicio.isoformat()
        if data_fim:
            params["dataFim"] = data_fim.isoformat()
        
        logger.info(f"Buscando votações: {data_inicio} a {data_fim}")
        
        try:
            response = await self._request("/votacoes", params=params)
            votacoes = response.get("dados", [])
            
            logger.info(f"Encontradas {len(votacoes)} votações")
            return response
            
        except CamaraAPIError as e:
            logger.error(f"Erro ao buscar votações: {str(e)}")
            raise
    
    async def get_voto_deputado(
        self,
        votacao_id: str,
        deputado_id: int
    ) -> Optional[dict[str, Any]]:
        """
        Obtém voto de um deputado em uma votação específica.
        
        Args:
            votacao_id: ID da votação
            deputado_id: ID do deputado
        
        Returns:
            Dados do voto ou None
        """
        logger.info(f"Buscando voto: votação={votacao_id}, deputado={deputado_id}")
        
        try:
            response = await self._request(f"/votacoes/{votacao_id}/votos")
            votos = response.get("dados", [])
            
            # Procura voto do deputado
            for voto in votos:
                if voto.get("deputado_", {}).get("id") == deputado_id:
                    logger.info(f"Voto encontrado: {voto.get('tipoVoto')}")
                    return voto
            
            logger.info(f"Voto não encontrado para deputado {deputado_id}")
            return None
            
        except CamaraAPIError as e:
            logger.error(f"Erro ao buscar voto: {str(e)}")
            return None
    
    @cache(ttl=21600, key_prefix="camara:despesas")
    async def get_despesas(
        self,
        deputado_id: int,
        ano: int,
        mes: Optional[int] = None,
        pagina: int = 1,
        itens: int = 100
    ) -> dict[str, Any]:
        """
        Lista despesas de um deputado.
        
        Args:
            deputado_id: ID do deputado
            ano: Ano das despesas
            mes: Mês das despesas (opcional)
            pagina: Número da página
            itens: Itens por página
        
        Returns:
            Dados das despesas
        """
        params = {
            "ano": ano,
            "pagina": pagina,
            "itens": min(itens, 100),
            "ordem": "DESC",
            "ordenarPor": "dataDocumento"
        }
        
        if mes:
            params["mes"] = mes
        
        logger.info(f"Buscando despesas: deputado={deputado_id}, ano={ano}, mes={mes}")
        
        try:
            response = await self._request(
                f"/deputados/{deputado_id}/despesas",
                params=params
            )
            despesas = response.get("dados", [])
            
            total = sum(d.get("valorDocumento", 0) for d in despesas)
            logger.info(f"Encontradas {len(despesas)} despesas (Total: R$ {total:.2f})")
            
            return response
            
        except CamaraAPIError as e:
            logger.error(f"Erro ao buscar despesas: {str(e)}")
            raise
    
    def normalize_deputado(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Normaliza dados do deputado para formato padrão Brazyl.
        
        Args:
            data: Dados raw da API
        
        Returns:
            Dados normalizados
        """
        return {
            "external_id": str(data.get("id")),
            "name": data.get("nomeCivil", ""),
            "parliamentary_name": data.get("ultimoStatus", {}).get("nome", data.get("nome", "")),
            "cpf": data.get("cpf"),
            "position": "DEPUTADO_FEDERAL",
            "party": data.get("ultimoStatus", {}).get("siglaPartido", ""),
            "state": data.get("ultimoStatus", {}).get("siglaUf", ""),
            "email": data.get("ultimoStatus", {}).get("email"),
            "photo_url": data.get("ultimoStatus", {}).get("urlFoto"),
            "biography": data.get("escolaridade"),  # Poderia ser melhorado
            "social_media": {
                "website": data.get("urlWebsite"),
                "twitter": None,  # API não fornece
                "facebook": None,
                "instagram": None
            }
        }

