"""
Cliente para API do Portal da Transparência.
Documentação: http://www.portaltransparencia.gov.br/api-de-dados
"""

from typing import Optional, Any
from datetime import date
import asyncio

import httpx

from app.config import settings
from app.utils.logger import setup_logger
from app.integrations.redis_client import cache

logger = setup_logger(__name__)


class TransparenciaAPIError(Exception):
    """Exceção para erros da API da Transparência."""
    pass


class TransparenciaAPI:
    """Cliente para API do Portal da Transparência."""
    
    def __init__(self):
        """Inicializa o cliente."""
        self.base_url = str(settings.transparencia_api_url)
        self.timeout = 30.0
        self._semaphore = asyncio.Semaphore(5)  # API mais limitada
    
    async def _request(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        retry: int = 3
    ) -> list[dict[str, Any]]:
        """
        Faz requisição para a API com retry.
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros query string
            retry: Número de tentativas
        
        Returns:
            Lista de resultados
        """
        url = f"{self.base_url}{endpoint}"
        
        async with self._semaphore:  # Rate limiting mais restrito
            for attempt in range(retry):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        logger.debug(f"Requisição Transparência API: {endpoint}", extra={"params": params})
                        
                        response = await client.get(url, params=params)
                        response.raise_for_status()
                        
                        data = response.json()
                        logger.debug(f"Resposta Transparência API: {endpoint} - Status {response.status_code}")
                        
                        return data if isinstance(data, list) else [data]
                
                except httpx.HTTPStatusError as e:
                    logger.warning(
                        f"Erro HTTP na Transparência API (tentativa {attempt + 1}/{retry}): {e.response.status_code}",
                        extra={"endpoint": endpoint}
                    )
                    
                    if e.response.status_code == 404:
                        return []  # Retorna lista vazia em vez de erro
                    
                    if attempt < retry - 1:
                        await asyncio.sleep(3 ** attempt)  # Backoff mais agressivo
                    else:
                        raise TransparenciaAPIError(f"Erro HTTP {e.response.status_code}: {endpoint}")
                
                except httpx.RequestError as e:
                    logger.warning(
                        f"Erro de conexão na Transparência API (tentativa {attempt + 1}/{retry}): {str(e)}",
                        extra={"endpoint": endpoint}
                    )
                    
                    if attempt < retry - 1:
                        await asyncio.sleep(3 ** attempt)
                    else:
                        raise TransparenciaAPIError(f"Erro de conexão: {str(e)}")
        
        return []
    
    @cache(ttl=21600, key_prefix="transparencia:gastos")
    async def get_gastos_parlamentares(
        self,
        cpf: str,
        ano: int,
        mes: Optional[int] = None,
        pagina: int = 1
    ) -> dict[str, Any]:
        """
        Busca gastos de parlamentares no Portal da Transparência.
        
        Args:
            cpf: CPF do parlamentar
            ano: Ano dos gastos
            mes: Mês dos gastos (opcional)
            pagina: Página dos resultados
        
        Returns:
            Dados dos gastos
        
        Note:
            Esta API pode ter limitações e nem sempre retorna dados
            completos para todos os parlamentares.
        """
        params = {
            "cpf": cpf.replace(".", "").replace("-", ""),  # Apenas números
            "anoMesPagamento": f"{ano}{mes:02d}" if mes else str(ano),
            "pagina": pagina
        }
        
        logger.info(f"Buscando gastos: CPF={cpf[:3]}***, ano={ano}, mes={mes}")
        
        try:
            # API da Transparência não tem endpoint específico para parlamentares
            # Seria necessário usar endpoints gerais de servidor público
            # Por ora, retornamos estrutura vazia
            
            logger.warning("API da Transparência: funcionalidade limitada para parlamentares")
            
            return {
                "dados": [],
                "mensagem": "API da Transparência tem dados limitados para parlamentares"
            }
            
        except TransparenciaAPIError as e:
            logger.error(f"Erro ao buscar gastos: {str(e)}")
            raise
    
    @cache(ttl=86400, key_prefix="transparencia:servidor")
    async def buscar_servidor_por_cpf(self, cpf: str) -> Optional[dict[str, Any]]:
        """
        Busca informações de servidor público por CPF.
        
        Args:
            cpf: CPF do servidor
        
        Returns:
            Dados do servidor ou None
        
        Note:
            Este endpoint pode ser usado para validar dados de parlamentares,
            mas a cobertura não é completa.
        """
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        
        logger.info(f"Buscando servidor por CPF: {cpf[:3]}***")
        
        try:
            # Endpoint de servidores civis
            resultado = await self._request(
                "/servidores",
                params={"cpf": cpf_limpo, "pagina": 1}
            )
            
            if resultado:
                logger.info(f"Servidor encontrado: {resultado[0].get('nome')}")
                return resultado[0]
            
            logger.info("Servidor não encontrado")
            return None
            
        except TransparenciaAPIError as e:
            logger.error(f"Erro ao buscar servidor: {str(e)}")
            return None
    
    def normalize_gasto(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Normaliza dados de gasto para formato padrão Brazyl.
        
        Args:
            data: Dados raw da API
        
        Returns:
            Dados normalizados
        """
        return {
            "descricao": data.get("descricao", ""),
            "valor": data.get("valor", 0),
            "data": data.get("data"),
            "favorecido": data.get("favorecido", {}).get("nome"),
            "fonte": "Portal da Transparência"
        }


class AvisaAPI:
    """
    Cliente para API Avisa (WhatsApp).
    
    Note:
        Implementação básica. Ajuste conforme documentação real da API Avisa.
    """
    
    def __init__(self):
        """Inicializa o cliente."""
        self.base_url = str(settings.avisa_api_url)
        self.token = settings.avisa_api_token
        self.timeout = 15.0
    
    async def send_message(
        self,
        phone: str,
        message: str,
        media_url: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Envia mensagem via WhatsApp.
        
        Args:
            phone: Número de telefone (+5511999999999)
            message: Texto da mensagem
            media_url: URL de mídia (imagem, vídeo) opcional
        
        Returns:
            Resposta da API
        """
        url = f"{self.base_url}/send"
        
        payload = {
            "phone": phone,
            "message": message
        }
        
        if media_url:
            payload["media_url"] = media_url
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Enviando mensagem WhatsApp para: {phone}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Mensagem enviada com sucesso: {data.get('id')}")
                
                return data
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar mensagem: {e.response.status_code}", exc_info=True)
            raise Exception(f"Erro ao enviar mensagem: {e.response.status_code}")
        
        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao enviar mensagem: {str(e)}", exc_info=True)
            raise Exception(f"Erro de conexão: {str(e)}")

