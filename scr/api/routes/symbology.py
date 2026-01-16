"""
Rotas para API de Symbology.

Define endpoints para criar, consultar e exportar simbologias.
"""
from typing import Dict, Any

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
        logger.debug(f"Received symbology data: {symbology_data}")

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
        logger.error(f"Error creating symbology: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/result/{url_key}",
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
    "/result/{url_key}/json",
    response_model=Dict[str, Any],
    responses={400: {"model": ErrorResponse}},
)
async def get_symbology_config_matplotlib(url_key: str) -> Dict[str, Any]:
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

        return matplotlib_kwargs

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
    "/result/{url_key}/sld",
    responses={
        200: {"description": "SLD XML", "content": {"application/xml": {}}},
        400: {"model": ErrorResponse},
    },
)
async def get_symbology_sld(url_key: str, layer_name: str = "layer") -> Response:
    """
    Obtém SLD (Styled Layer Descriptor) de uma simbologia.

    Retorna XML SLD válido para usar diretamente no GeoServer.

    Args:
        url_key: Chave de 17 caracteres gerada por create_symbology
        layer_name: Nome da camada (padrão: "layer")

    Returns:
        Response: XML SLD
    """
    try:
        symbology = Symbology.from_url_key(url_key)

        logger.debug(f"Generating SLD for url_key: {url_key}, layer: {layer_name}")

        sld_xml = symbology.to_geoserver_sld(layer_name)

        return Response(
            content=sld_xml,
            media_type="application/xml",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    except ValueError as e:
        logger.warning(f"Invalid url_key: {url_key} - {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid url_key format: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error generating SLD: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/result/{url_key}/css",
    responses={
        200: {"description": "GeoServer CSS", "content": {"text/css": {}}},
        400: {"model": ErrorResponse},
    },
)
async def get_symbology_css(url_key: str) -> Response:
    """
    Obtém CSS do GeoServer de uma simbologia.

    Retorna CSS válido para usar diretamente no GeoServer.

    Args:
        url_key: Chave de 17 caracteres gerada por create_symbology

    Returns:
        Response: CSS string
    """
    try:
        symbology = Symbology.from_url_key(url_key)

        logger.debug(f"Generating CSS for url_key: {url_key}")

        css = symbology.to_geoserver_css()

        return Response(
            content=css,
            media_type="text/css",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    except ValueError as e:
        logger.warning(f"Invalid url_key: {url_key} - {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid url_key format: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error generating CSS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/result/{url_key}/rest",
    responses={
        200: {"description": "GeoServer REST payload", "content": {"application/json": {}}},
        400: {"model": ErrorResponse},
    },
)
async def get_symbology_rest(url_key: str):
    """
    Obtém payload da API REST do GeoServer.

    Retorna payload JSON pronto para usar com a API REST do GeoServer.

    Args:
        url_key: Chave de 17 caracteres gerada por create_symbology

    Returns:
        JSON payload para POST /geoserver/rest/styles
    """
    try:
        symbology = Symbology.from_url_key(url_key)

        logger.debug(f"Generating REST payload for url_key: {url_key}")

        rest_payload = symbology.to_geoserver_rest_payload()

        return rest_payload

    except ValueError as e:
        logger.warning(f"Invalid url_key: {url_key} - {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid url_key format: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error generating REST payload: {e}")
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
