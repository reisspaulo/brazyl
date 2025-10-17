#!/usr/bin/env python3
"""
Script para popular tabela 'politicians' com dados das APIs públicas.

Busca deputados federais e senadores das APIs oficiais e salva no Supabase.

Uso:
    python populate_politicians.py                    # Execução normal
    python populate_politicians.py --dry-run          # Simular sem salvar
    python populate_politicians.py --update           # Atualizar existentes
    python populate_politicians.py --verbose          # Logs detalhados
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from tqdm.asyncio import tqdm
from app.integrations import CamaraAPI, SenadoAPI, get_supabase, SupabaseClientError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class PoliticianPopulator:
    """Classe para popular banco de dados com políticos."""
    
    def __init__(self, dry_run: bool = False, update: bool = False):
        """
        Inicializa o populador.
        
        Args:
            dry_run: Se True, apenas simula sem salvar
            update: Se True, atualiza políticos existentes
        """
        self.dry_run = dry_run
        self.update = update
        self.supabase = get_supabase()
        self.camara = CamaraAPI()
        self.senado = SenadoAPI()
        
        self.stats = {
            "total": 0,
            "created": 0,
            "updated": 0,
            "errors": 0,
            "skipped": 0
        }
    
    async def populate_deputados(self):
        """Popula banco com deputados federais."""
        logger.info("=" * 50)
        logger.info("POPULANDO DEPUTADOS FEDERAIS")
        logger.info("=" * 50)
        
        try:
            # Buscar todos os deputados (paginação)
            pagina = 1
            todos_deputados = []
            
            while True:
                logger.info(f"Buscando página {pagina} de deputados...")
                response = await self.camara.get_deputados(pagina=pagina, itens=100)
                deputados = response.get("dados", [])
                
                if not deputados:
                    break
                
                todos_deputados.extend(deputados)
                logger.info(f"Encontrados {len(deputados)} deputados na página {pagina}")
                
                # Verificar se há mais páginas
                links = response.get("links", [])
                has_next = any(link.get("rel") == "next" for link in links)
                
                if not has_next:
                    break
                
                pagina += 1
            
            logger.info(f"Total de deputados encontrados: {len(todos_deputados)}")
            
            # Processar cada deputado
            for deputado_basico in tqdm(todos_deputados, desc="Processando deputados"):
                try:
                    deputado_id = deputado_basico.get("id")
                    
                    # Buscar dados completos
                    deputado_completo = await self.camara.get_deputado(deputado_id)
                    
                    # Normalizar dados
                    normalized = self.camara.normalize_deputado(deputado_completo)
                    
                    # Salvar no banco
                    await self._save_politician(normalized)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar deputado {deputado_basico.get('id')}: {str(e)}")
                    self.stats["errors"] += 1
        
        except Exception as e:
            logger.error(f"Erro ao buscar deputados: {str(e)}", exc_info=True)
    
    async def populate_senadores(self):
        """Popula banco com senadores."""
        logger.info("=" * 50)
        logger.info("POPULANDO SENADORES")
        logger.info("=" * 50)
        
        try:
            # Buscar todos os senadores em exercício
            response = await self.senado.get_senadores()
            senadores = response.get("dados", [])
            
            logger.info(f"Total de senadores encontrados: {len(senadores)}")
            
            # Processar cada senador
            for senador_basico in tqdm(senadores, desc="Processando senadores"):
                try:
                    senador_id = senador_basico.get("IdentificacaoParlamentar", {}).get("CodigoParlamentar")
                    
                    if not senador_id:
                        logger.warning("Senador sem ID, pulando...")
                        self.stats["skipped"] += 1
                        continue
                    
                    # Buscar dados completos
                    senador_completo = await self.senado.get_senador(senador_id)
                    
                    # Normalizar dados
                    normalized = self.senado.normalize_senador(senador_completo)
                    
                    # Salvar no banco
                    await self._save_politician(normalized)
                
                except Exception as e:
                    logger.error(f"Erro ao processar senador: {str(e)}")
                    self.stats["errors"] += 1
        
        except Exception as e:
            logger.error(f"Erro ao buscar senadores: {str(e)}", exc_info=True)
    
    async def _save_politician(self, data: dict):
        """
        Salva político no banco de dados.
        
        Args:
            data: Dados normalizados do político
        """
        self.stats["total"] += 1
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Salvaria: {data.get('parliamentary_name')} ({data.get('position')})")
            self.stats["created"] += 1
            return
        
        try:
            external_id = data.get("external_id")
            
            # Verificar se já existe
            existing = await self.supabase.client.table("politicians")\
                .select("id")\
                .eq("external_id", external_id)\
                .maybe_single()\
                .execute()
            
            if existing.data:
                if self.update:
                    # Atualizar existente
                    await self.supabase.client.table("politicians")\
                        .update(data)\
                        .eq("external_id", external_id)\
                        .execute()
                    
                    logger.info(f"Atualizado: {data.get('parliamentary_name')}")
                    self.stats["updated"] += 1
                else:
                    logger.debug(f"Já existe: {data.get('parliamentary_name')}")
                    self.stats["skipped"] += 1
            else:
                # Criar novo
                await self.supabase.create_politician(data)
                
                logger.info(f"Criado: {data.get('parliamentary_name')}")
                self.stats["created"] += 1
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao salvar político {data.get('parliamentary_name')}: {str(e)}")
            self.stats["errors"] += 1
    
    def print_stats(self):
        """Imprime estatísticas finais."""
        logger.info("=" * 50)
        logger.info("ESTATÍSTICAS FINAIS")
        logger.info("=" * 50)
        logger.info(f"Total processados: {self.stats['total']}")
        logger.info(f"Criados: {self.stats['created']}")
        logger.info(f"Atualizados: {self.stats['updated']}")
        logger.info(f"Pulados: {self.stats['skipped']}")
        logger.info(f"Erros: {self.stats['errors']}")
        logger.info("=" * 50)
    
    async def run(self):
        """Executa população completa."""
        logger.info("Iniciando população de políticos...")
        
        if self.dry_run:
            logger.warning("MODO DRY RUN - Nenhum dado será salvo no banco")
        
        if self.update:
            logger.info("MODO UPDATE - Políticos existentes serão atualizados")
        
        # Popular deputados
        await self.populate_deputados()
        
        # Popular senadores
        await self.populate_senadores()
        
        # Imprimir estatísticas
        self.print_stats()
        
        logger.info("População concluída!")


async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Popula banco de dados com políticos das APIs públicas"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula execução sem salvar no banco"
    )
    
    parser.add_argument(
        "--update",
        action="store_true",
        help="Atualiza políticos existentes"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Logs mais detalhados"
    )
    
    parser.add_argument(
        "--only-deputados",
        action="store_true",
        help="Popula apenas deputados federais"
    )
    
    parser.add_argument(
        "--only-senadores",
        action="store_true",
        help="Popula apenas senadores"
    )
    
    args = parser.parse_args()
    
    # Ajustar nível de log
    if args.verbose:
        logger.setLevel("DEBUG")
    
    # Criar populador
    populator = PoliticianPopulator(
        dry_run=args.dry_run,
        update=args.update
    )
    
    # Executar população
    try:
        if args.only_deputados:
            await populator.populate_deputados()
        elif args.only_senadores:
            await populator.populate_senadores()
        else:
            await populator.run()
        
        populator.print_stats()
    
    except KeyboardInterrupt:
        logger.warning("\nInterrompido pelo usuário")
        populator.print_stats()
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

