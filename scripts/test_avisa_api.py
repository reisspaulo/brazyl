#!/usr/bin/env python3
"""
Script para testar integração com API Avisa (WhatsApp).

Uso:
    python test_avisa_api.py +5511999999999 "Mensagem de teste"
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from app.integrations.transparencia_api import AvisaAPI
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def test_send_message(phone: str, message: str):
    """Testa envio de mensagem via Avisa API."""
    logger.info(f"Testando envio de mensagem para: {phone}")
    logger.info(f"Mensagem: {message}")
    
    avisa = AvisaAPI()
    
    try:
        response = await avisa.send_message(phone, message)
        
        logger.info("Mensagem enviada com sucesso!")
        logger.info(f"Response: {response}")
        
        return True
    
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}", exc_info=True)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Testa envio de mensagem via API Avisa"
    )
    
    parser.add_argument(
        "phone",
        help="Número de WhatsApp (+5511999999999)"
    )
    
    parser.add_argument(
        "message",
        help="Mensagem a enviar"
    )
    
    args = parser.parse_args()
    
    success = asyncio.run(test_send_message(args.phone, args.message))
    
    if success:
        logger.info("Teste concluído com sucesso!")
        sys.exit(0)
    else:
        logger.error("Teste falhou!")
        sys.exit(1)


if __name__ == "__main__":
    main()

