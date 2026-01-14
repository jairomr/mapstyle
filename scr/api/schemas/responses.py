"""
Schemas de resposta para API FastAPI.

Define estruturas Pydantic para serialização de respostas.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any


class SymbologyResponse(BaseModel):
    """
    Resposta para criação de simbologia.

    Retornada por POST /symbology
    """

    url_key: str = Field(
        description="Chave URL-safe de 17 caracteres para acessar a simbologia"
    )
    matplotlib_url: str = Field(description="URL para configurações matplotlib")
    preview_url: str = Field(description="URL para preview PNG")
    symbology: Dict[str, Any] = Field(
        description="Simbologia serializada em JSON (pydantic dump)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "url_key": "00A1B2C3D4E5F6G7H",
                "matplotlib_url": "/api/result/00A1B2C3D4E5F6G7H/json",
                "preview_url": "/api/result/00A1B2C3D4E5F6G7H/png",
                "symbology": {
                    "symbology_geometry_type": "POLYGON",
                    "symbology_fill_color": "rgb(255, 0, 0)",
                    "symbology_fill_style": "SOLID",
                    "symbology_fill_density": 0,
                    "symbology_stroke_color": "rgb(0, 0, 255)",
                    "symbology_stroke_style": "DASHED",
                    "symbology_stroke_line": 2.0,
                },
            }
        }


class GeoServerConfigResponse(BaseModel):
    """Configurações para GeoServer."""

    sld: str = Field(description="SLD XML para GeoServer")
    css: str = Field(description="CSS para GeoServer")
    rest_payload: Dict[str, Any] = Field(description="Payload para API REST GeoServer")


class MatplotlibConfigResponse(BaseModel):
    """Configurações para matplotlib."""

    fill: bool = Field(description="Se há preenchimento")
    facecolor: str | None = Field(
        default=None, description="Cor de preenchimento (hex ou RGB)"
    )
    edgecolor: str | None = Field(default=None, description="Cor da borda")
    linewidth: float = Field(description="Espessura da linha")
    linestyle: str | None = Field(default=None, description="Estilo da linha")
    hatch: str | None = Field(
        default=None, description="Padrão de hatch (se aplicável)"
    )
    radius: float | None = Field(
        default=None, description="Raio para pontos (círculos)"
    )


class ConfigResponse(BaseModel):
    """
    Resposta com configurações completas da simbologia.

    Retornada por GET /api/result/{url_key}/json
    """

    url_key: str = Field(description="Chave URL-safe da simbologia")
    matplotlib: Dict[str, Any] = Field(
        description="Kwargs bruto para matplotlib.patches"
    )
    geoserver: GeoServerConfigResponse = Field(description="Configurações GeoServer")
    symbology: Dict[str, Any] = Field(description="Simbologia completa em JSON")

    class Config:
        json_schema_extra = {
            "example": {
                "url_key": "00A1B2C3D4E5F6G7H",
                "matplotlib": {
                    "fill": True,
                    "facecolor": "rgb(255, 0, 0)",
                    "edgecolor": "rgb(0, 0, 255)",
                    "linewidth": 2.0,
                    "linestyle": "--",
                },
                "geoserver": {
                    "sld": "<?xml version='1.0'...",
                    "css": "* { fill: #ff0000; ...",
                    "rest_payload": {},
                },
                "symbology": {},
            }
        }


class ErrorResponse(BaseModel):
    """Resposta de erro."""

    detail: str = Field(description="Descrição do erro")
    status_code: int = Field(description="Código HTTP do erro")

    class Config:
        json_schema_extra = {
            "example": {"detail": "Invalid url_key format", "status_code": 400}
        }
