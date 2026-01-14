"""
Rotas para API de Symbology.

Define endpoints para criar, consultar e exportar simbologias.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from loguru import logger

from scr.core.model.symbology import Symbology
from scr.api.schemas.responses import (
    SymbologyResponse,
    ConfigResponse,
    GeoServerConfigResponse,
    ErrorResponse,
)
from scr.api.schemas.symbology_schema import SymbologyCreateSchema
from scr.api.services.preview import generate_preview

router = APIRouter(prefix="/api", tags=["symbology"])


@router.post(
    "/symbology",
    response_model=SymbologyResponse,
    responses={400: {"model": ErrorResponse}},
)
async def create_symbology(symbology_data: SymbologyCreateSchema) -> SymbologyResponse:
    """
    Cria uma simbologia e retorna URLs para acessar seus recursos.

    Recebe objeto Symbology completo com todas as configurações de estilo geoespacial.

    Returns:
        SymbologyResponse: Contém url_key (chave compacta) e URLs para recursos
    """
    try:
        # Converte schema para Symbology object
        symbology = symbology_data.to_symbology()

        # Gera chave URL-safe ultra-compacta (17 caracteres)
        url_key = symbology.url_key()

        logger.info(f"Symbology created with url_key: {url_key}")

        # Serializa symbology com model_dump_json então re-parse
        symbology_dict = symbology.model_dump(mode="json")

        return SymbologyResponse(
            url_key=url_key,
            matplotlib_url=f"/api/result/{url_key}/json",
            preview_url=f"/api/result/{url_key}/png",
            symbology=symbology_dict,
        )

    except Exception as e:
        logger.error(f"Error creating symbology: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/result/{url_key}/json",
    response_model=ConfigResponse,
    responses={400: {"model": ErrorResponse}},
)
async def get_symbology_config(url_key: str) -> ConfigResponse:
    """
    Obtém configurações completas de uma simbologia.

    Retorna configurações para matplotlib, GeoServer e a simbologia completa em JSON.

    Args:
        url_key: Chave de 17 caracteres gerada por create_symbology

    Returns:
        ConfigResponse: Contém matplotlib kwargs, GeoServer configs e simbolgia
    """
    try:
        # Descompacta a url_key e reconstrói a simbologia
        symbology = Symbology.from_url_key(url_key)

        logger.debug(f"Retrieved symbology from url_key: {url_key}")

        # Gera configurações
        matplotlib_kwargs = symbology.to_matplotlib_patch_kwargs()

        geoserver_config = GeoServerConfigResponse(
            sld=symbology.to_geoserver_sld(),
            css=symbology.to_geoserver_css(),
            rest_payload=symbology.to_geoserver_rest_payload(),
        )

        # Serializa symbology
        symbology_dict = symbology.model_dump(mode="json")

        return ConfigResponse(
            url_key=url_key,
            matplotlib=matplotlib_kwargs,
            geoserver=geoserver_config,
            symbology=symbology_dict,
        )

    except ValueError as e:
        logger.warning(f"Invalid url_key: {url_key} - {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid url_key format: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error retrieving symbology: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/result/{url_key}/png",
    responses={
        200: {"description": "PNG image", "content": {"image/png": {}}},
        400: {"model": ErrorResponse},
    },
)
async def get_symbology_preview(url_key: str, size: int = Query(200, ge=50, le=1000)):
    """
    Obtém preview PNG de uma simbologia.

    Renderiza a simbologia como imagem PNG mostrando como ficará em um mapa.

    Args:
        url_key: Chave de 17 caracteres gerada por create_symbology
        size: Tamanho da imagem em pixels (50-1000, padrão 200)

    Returns:
        Response: PNG image binary
    """
    try:
        # Descompacta a url_key e reconstrói a simbologia
        symbology = Symbology.from_url_key(url_key)

        logger.debug(f"Generating preview for url_key: {url_key}, size: {size}")

        # Gera imagem PNG
        png_bytes = generate_preview(symbology, size=size)

        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},  # Cache 24h
        )

    except ValueError as e:
        logger.warning(f"Invalid url_key: {url_key} - {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid url_key format: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
