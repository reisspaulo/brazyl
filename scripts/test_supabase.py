#!/usr/bin/env python3
"""
Script para testar conexão e operações básicas com Supabase.

Uso:
    python test_supabase.py
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from app.integrations import get_supabase, SupabaseClientError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def test_connection():
    """Testa conexão com Supabase."""
    logger.info("Testando conexão com Supabase...")
    
    try:
        supabase = get_supabase()
        logger.info("Cliente Supabase inicializado com sucesso!")
        
        return True
    
    except Exception as e:
        logger.error(f"Erro ao conectar com Supabase: {str(e)}", exc_info=True)
        return False


async def test_read_plans():
    """Testa leitura de planos."""
    logger.info("Testando leitura de planos...")
    
    try:
        supabase = get_supabase()
        
        response = supabase.client.table("plans")\
            .select("*")\
            .execute()
        
        plans = response.data or []
        
        logger.info(f"Encontrados {len(plans)} planos:")
        for plan in plans:
            logger.info(f"  - {plan['name']} ({plan['type']}): R$ {plan['price']}")
        
        return True
    
    except SupabaseClientError as e:
        logger.error(f"Erro ao ler planos: {str(e)}", exc_info=True)
        return False


async def test_count_politicians():
    """Testa contagem de políticos."""
    logger.info("Testando contagem de políticos...")
    
    try:
        supabase = get_supabase()
        
        response = supabase.client.table("politicians")\
            .select("id", count="exact")\
            .execute()
        
        total = response.count or 0
        
        logger.info(f"Total de políticos no banco: {total}")
        
        # Contar por posição
        positions = ["DEPUTADO_FEDERAL", "SENADOR"]
        
        for position in positions:
            response = supabase.client.table("politicians")\
                .select("id", count="exact")\
                .eq("position", position)\
                .execute()
            
            count = response.count or 0
            logger.info(f"  - {position}: {count}")
        
        return True
    
    except SupabaseClientError as e:
        logger.error(f"Erro ao contar políticos: {str(e)}", exc_info=True)
        return False


async def run_all_tests():
    """Executa todos os testes."""
    logger.info("=" * 50)
    logger.info("TESTANDO INTEGRAÇÃO COM SUPABASE")
    logger.info("=" * 50)
    
    results = {
        "connection": await test_connection(),
        "read_plans": await test_read_plans(),
        "count_politicians": await test_count_politicians()
    }
    
    logger.info("=" * 50)
    logger.info("RESULTADOS DOS TESTES")
    logger.info("=" * 50)
    
    for test_name, success in results.items():
        status = "OK" if success else "FALHOU"
        logger.info(f"{test_name}: {status}")
    
    logger.info("=" * 50)
    
    all_success = all(results.values())
    
    if all_success:
        logger.info("Todos os testes passaram!")
        return 0
    else:
        logger.error("Alguns testes falharam!")
        return 1


def main():
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

