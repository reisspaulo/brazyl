"""
Aplicação principal FastAPI - Brazyl MVP.
Sistema de acompanhamento de políticos brasileiros via WhatsApp.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.utils.logger import setup_logger
from app.api.routes import health, users, politicians, follows, notifications

# Setup logger
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Gerenciamento do ciclo de vida da aplicação.
    Executado na inicialização e finalização.
    """
    # Startup
    logger.info("Iniciando aplicação Brazyl", extra={
        "environment": settings.environment,
        "log_level": settings.log_level
    })
    
    # TODO: Inicializar conexões (Redis, etc)
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação Brazyl")
    # TODO: Fechar conexões


# Inicialização do FastAPI
app = FastAPI(
    title="Brazyl API",
    description="API para acompanhamento de políticos brasileiros via WhatsApp",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Loga todas as requisições HTTP."""
    logger.info(
        f"Requisição recebida: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None
        }
    )
    
    response = await call_next(request)
    
    logger.info(
        f"Resposta enviada: {response.status_code}",
        extra={
            "status_code": response.status_code,
            "method": request.method,
            "path": request.url.path
        }
    )
    
    return response


# Error Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação Pydantic."""
    logger.warning(
        f"Erro de validação: {exc.errors()}",
        extra={"errors": exc.errors(), "body": exc.body}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Erro de validação",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handler genérico para exceções não tratadas."""
    logger.error(
        f"Erro não tratado: {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Erro interno do servidor",
            "message": str(exc) if settings.is_development else "Ocorreu um erro inesperado"
        }
    )


# Incluir routers
app.include_router(health.router, tags=["Health"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(politicians.router, prefix="/politicians", tags=["Politicians"])
app.include_router(follows.router, prefix="/follows", tags=["Follows"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])


@app.get("/")
async def root():
    """Endpoint raiz - informações básicas da API."""
    return {
        "name": "Brazyl API",
        "version": "0.1.0",
        "status": "operational",
        "environment": settings.environment,
        "docs": "/docs"
    }

