"""
Aplicação principal FastAPI para MapTema MapBiomas.

Expõe API REST para criar, consultar e exportar simbologias geoespaciais.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from loguru import logger

from scr.api.routes import symbology

# Configuração de logging
logger.add(
    "logs/api.log",
    rotation="500 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)


def create_app() -> FastAPI:
    """
    Factory para criar e configurar a aplicação FastAPI.

    Returns:
        FastAPI: Aplicação configurada e pronta para uso
    """

    app = FastAPI(
        title="MapTema MapBiomas API",
        description="API REST para simbologia geoespacial - criar, consultar e exportar estilos de mapa",
        version="0.1.0",
        contact={
            "name": "MapTema MapBiomas",
            "url": "https://github.com/maptemamapbiomas",
        },
        license_info={
            "name": "MIT",
        },
    )

    # CORS - Permitir requisições de qualquer origem
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health")
    async def health_check():
        """Verifica se a API está funcionando."""
        logger.debug("Health check")
        return {"status": "ok", "version": "0.1.0"}

    # Raiz
    @app.get("/")
    async def root():
        """Informações sobre a API."""
        logger.debug("Root endpoint accessed")
        return {
            "name": "MapTema MapBiomas API",
            "version": "0.1.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        }

    # Incluir rotas
    app.include_router(symbology.router)

    # Customizar OpenAPI schema
    def custom_openapi():
        """Customiza o schema OpenAPI."""
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="MapTema MapBiomas API",
            version="0.1.0",
            description="API para simbologia geoespacial",
            routes=app.routes,
        )

        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Exception handler global
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Handler global para exceções."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": str(type(exc))},
        )

    logger.info("FastAPI application created successfully")
    return app


# Criar app global
app = create_app()


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server...")
    uvicorn.run(
        "scr.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
