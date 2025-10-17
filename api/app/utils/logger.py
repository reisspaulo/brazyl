"""
Configuração de logging estruturado para a aplicação.
Logs em formato JSON para facilitar análise e monitoramento.
"""

import logging
import sys
from typing import Any
import json
from datetime import datetime

from app.config import settings


class JSONFormatter(logging.Formatter):
    """Formatter para logs em formato JSON estruturado."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log record em JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adicionar informações extras se existirem
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Adicionar exception info se existir
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(name: str) -> logging.Logger:
    """
    Configura e retorna um logger com formato JSON.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.log_level))
    
    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # Usar JSON formatter em produção, formato simples em dev
    if settings.is_production:
        handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger

