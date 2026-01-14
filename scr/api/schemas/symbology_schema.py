"""
Schema customizado para Symbology com suporte a JSON.

Permite receber dados via JSON na API e convertê-los para objetos Symbology.
"""

from pydantic import BaseModel, field_validator

from scr.core.model.symbology import (
    Symbology,
    SymbologyGeometryType,
    SymbologyFill,
    LineStyle,
)
from pydantic_extra_types.color import Color


class SymbologyCreateSchema(BaseModel):
    """
    Schema para criação de Symbology via JSON.

    Aceita enums como strings e as converte automaticamente.
    """

    symbology_geometry_type: str  # "POLYGON", "LINE", "POINT"
    symbology_fill_color: str  # Aceita hex, rgb, nomes
    symbology_fill_style: str  # SOLID, NOBRUSH, SLASH, BACKSLASH, etc
    symbology_fill_density: int
    symbology_stroke_color: str  # Aceita hex, rgb, nomes
    symbology_stroke_style: str  # SOLID, DASHED, DOTTED, etc
    symbology_stroke_line: float

    @field_validator("symbology_geometry_type", mode="after")
    @classmethod
    def validate_geometry_type(cls, v):
        """Valida e converte geometry type."""
        if isinstance(v, str):
            try:
                return SymbologyGeometryType[v]
            except KeyError:
                raise ValueError(f"Invalid geometry type: {v}")
        return v

    @field_validator("symbology_fill_style", mode="after")
    @classmethod
    def validate_fill_style(cls, v):
        """Valida e converte fill style."""
        if isinstance(v, str):
            try:
                return SymbologyFill[v]
            except KeyError:
                raise ValueError(f"Invalid fill style: {v}")
        return v

    @field_validator("symbology_stroke_style", mode="after")
    @classmethod
    def validate_stroke_style(cls, v):
        """Valida e converte stroke style."""
        if isinstance(v, str):
            try:
                return LineStyle[v]
            except KeyError:
                raise ValueError(f"Invalid stroke style: {v}")
        return v

    def to_symbology(self) -> Symbology:
        """Converte para objeto Symbology."""
        return Symbology(
            symbology_geometry_type=self.symbology_geometry_type,
            symbology_fill_color=Color(self.symbology_fill_color),
            symbology_fill_style=self.symbology_fill_style,
            symbology_fill_density=self.symbology_fill_density,
            symbology_stroke_color=Color(self.symbology_stroke_color),
            symbology_stroke_style=self.symbology_stroke_style,
            symbology_stroke_line=self.symbology_stroke_line,
        )

    class Config:
        json_schema_extra = {
            "example": {
                "symbology_geometry_type": "POLYGON",
                "symbology_fill_color": "#ff0000",
                "symbology_fill_style": "SOLID",
                "symbology_fill_density": 0,
                "symbology_stroke_color": "#0000ff",
                "symbology_stroke_style": "DASHED",
                "symbology_stroke_line": 2.0,
            }
        }
