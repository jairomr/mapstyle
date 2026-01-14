"""
Módulo de simbologia para representação geoespacial.

Este módulo fornece classes para definir e serializar estilos de símbolos
geoespaciais (polígonos, linhas, pontos) com suporte a cache e URL encoding.
"""

import struct
from enum import Enum
from typing import Dict, Type, Any, List, Tuple
from xml.etree import ElementTree as ET

from loguru import logger
from pydantic import BaseModel, Field, field_validator
from pydantic_extra_types.color import Color


class LineStyle(Enum):
    """
    Estilos de linha compatíveis com matplotlib.

    Cada estilo contém (valor_matplotlib, representação_string, código_numérico).
    """
    SOLID = ('-', '────', 0)
    DASHED = ('--', '--', 1)
    DOTTED = (':', '····', 2)
    DASH_DOT = ('-.', '-.-.', 3)
    LONG_DASH = ((0, (8, 4)), '----', 4)
    SHORT_DASH = ((0, (4, 2)), '--', 5)
    DASH_DOT_DOT = ((0, (6, 2, 1, 2)), '--.--', 6)
    DASH_DOT_DOT_DOT = ((0, (6, 2, 1, 2, 1, 2)), '--..--', 7)
    SPARSE_DOT = ((0, (1, 4)), '.   .', 8)
    DENSE_DOT = ((0, (1, 1)), '.....', 9)
    NONE = ('None', 'none', 10)

    def __init__(self, mpl_value, repr_str: str, code: int):
        self.mpl = mpl_value
        self.repr = repr_str
        self.code = code

    def __str__(self) -> str:
        return self.repr

    @classmethod
    def from_code(cls, code: int) -> 'LineStyle':
        """Recupera LineStyle a partir do código numérico."""
        for style in cls:
            if style.code == code:
                return style
        raise ValueError(f"Código LineStyle inválido: {code}")


class SymbologyGeometryType(str, Enum):
    """Tipos de geometria suportados para simbologia."""
    POLYGON = "POLYGON"
    LINE = "LINE"
    POINT = "POINT"


# Mapeamentos para códigos numéricos
_GEOMETRY_TYPE_TO_CODE: Dict[SymbologyGeometryType, int] = {
    SymbologyGeometryType.POLYGON: 0,
    SymbologyGeometryType.LINE: 1,
    SymbologyGeometryType.POINT: 2,
}

_CODE_TO_GEOMETRY_TYPE: Dict[int, SymbologyGeometryType] = {
    v: k for k, v in _GEOMETRY_TYPE_TO_CODE.items()
}


class SymbologyFill(str, Enum):
    """
    Padrões de preenchimento para geometrias.

    Compatível com matplotlib hatch patterns.
    """
    SOLID = "SOLID"
    NOBRUSH = "NOBRUSH"
    SLASH = '/'
    BACKSLASH = '\\'
    PIPE = '|'
    DASH = '-'
    PLUS = '+'
    X = 'x'
    O_LOWER = 'o'
    O_UPPER = 'O'
    DOT = '.'
    STAR = '*'


# Mapeamentos para códigos numéricos
_FILL_STYLE_TO_CODE: Dict[SymbologyFill, int] = {
    SymbologyFill.SOLID: 0,
    SymbologyFill.NOBRUSH: 1,
    SymbologyFill.SLASH: 2,
    SymbologyFill.BACKSLASH: 3,
    SymbologyFill.PIPE: 4,
    SymbologyFill.DASH: 5,
    SymbologyFill.PLUS: 6,
    SymbologyFill.X: 7,
    SymbologyFill.O_LOWER: 8,
    SymbologyFill.O_UPPER: 9,
    SymbologyFill.DOT: 10,
    SymbologyFill.STAR: 11,
}

_CODE_TO_FILL_STYLE: Dict[int, SymbologyFill] = {
    v: k for k, v in _FILL_STYLE_TO_CODE.items()
}


class Symbology(BaseModel):
    """
    Representação imutável de simbologia geoespacial.

    Suporta serialização URL-safe e cache baseado em hash consistente.
    Todos os atributos são validados e normalizados na criação.
    """

    model_config = {"frozen": True}

    symbology_geometry_type: SymbologyGeometryType
    symbology_fill_color: Color  # Cor do preenchimento SOLID ou cor do hatch
    symbology_fill_style: SymbologyFill  # Estilo de preenchimento (SOLID, hatch, etc.)
    symbology_fill_density: int = Field(ge=0, le=10, description="Densidade do preenchimento (0-10)")
    symbology_stroke_color: Color  # Cor da linha/borda
    symbology_stroke_style: LineStyle  # Estilo da linha/borda
    symbology_stroke_line: float = Field(ge=0.0, le=50.0, description="Espessura da linha em pixels")

    @field_validator("symbology_stroke_line")
    @classmethod
    def normalize_stroke_line(cls, v: float) -> float:
        """Normaliza espessura da linha para 3 casas decimais."""
        return round(v, 3)

    def cache_key(self) -> tuple:
        """
        Gera chave de cache consistente e hashável.

        Returns:
            Tupla imutável representando o estado do objeto
        """
        return (
            self.symbology_geometry_type.value,
            self.symbology_fill_color.as_hex().lower(),
            self.symbology_fill_style.value,
            self.symbology_fill_density,
            self.symbology_stroke_color.as_hex().lower(),
            self.symbology_stroke_style.repr,
            self.symbology_stroke_line,
        )

    def __hash__(self) -> int:
        """Hash baseado na cache_key para uso em sets e dicts."""
        return hash(self.cache_key())

    def _pack_binary(self) -> bytes:
        """
        Empacota a simbologia em formato binário compacto (13 bytes).

        Formato:
        - Tipo geometria: 1 byte (código 0-2)
        - Cor preenchimento: 3 bytes (RGB)
        - Estilo preenchimento: 1 byte (código 0-11)
        - Densidade: 1 byte (0-10)
        - Cor linha: 3 bytes (RGB)
        - Estilo linha: 1 byte (código 0-10)
        - Espessura linha: 2 bytes (uint16, milésimos de pixel)
        - Reservado: 1 byte (0 para futuras expansões)

        Total: 1+3+1+1+3+1+2+1 = 13 bytes
        """
        # Códigos numéricos
        geom_code = _GEOMETRY_TYPE_TO_CODE[self.symbology_geometry_type]
        fill_style_code = _FILL_STYLE_TO_CODE[self.symbology_fill_style]
        stroke_style_code = self.symbology_stroke_style.code

        # Cores como RGB
        fill_color_rgb = self.symbology_fill_color.as_rgb_tuple()
        stroke_color_rgb = self.symbology_stroke_color.as_rgb_tuple()

        # Espessura como inteiro (milésimos)
        stroke_line_int = min(int(self.symbology_stroke_line * 1000), 65535)

        # Empacotamento
        data = struct.pack(
            '>B3B B B3B B H B',
            geom_code,                  # 1 byte
            *fill_color_rgb,            # 3 bytes
            fill_style_code,            # 1 byte
            self.symbology_fill_density,# 1 byte
            *stroke_color_rgb,          # 3 bytes
            stroke_style_code,          # 1 byte
            stroke_line_int,            # 2 bytes
            0,                          # 1 byte reservado
        )

        return data

    @classmethod
    def _unpack_binary(cls, data: bytes) -> 'Symbology':
        """
        Desempacota a simbologia de formato binário.

        Args:
            data: Bytes empacotados (13 bytes)

        Returns:
            Nova instância de Symbology

        Raises:
            ValueError: Se dados forem inválidos
            struct.error: Se formato binário estiver incorreto
        """
        # Verifica tamanho
        if len(data) != 13:
            raise ValueError(f"Dados devem ter 13 bytes, recebidos {len(data)}")

        # Desempacotamento
        unpacked = struct.unpack('>B3B B B3B B H B', data)

        geom_code, fr, fg, fb, fill_style_code, fill_density, \
            sr, sg, sb, stroke_style_code, stroke_line_int, _ = unpacked

        # Validações básicas
        if fill_density > 10:
            raise ValueError(f"Densidade inválida: {fill_density}")
        if stroke_line_int > 50000:  # 50.0 pixels * 1000
            raise ValueError(f"Espessura inválida: {stroke_line_int/1000}")

        # Reconstrução
        return cls(
            symbology_geometry_type=_CODE_TO_GEOMETRY_TYPE[geom_code],
            symbology_fill_color=Color.from_rgb(fr, fg, fb),
            symbology_fill_style=_CODE_TO_FILL_STYLE[fill_style_code],
            symbology_fill_density=fill_density,
            symbology_stroke_color=Color.from_rgb(sr, sg, sb),
            symbology_stroke_style=LineStyle.from_code(stroke_style_code),
            symbology_stroke_line=stroke_line_int / 1000.0,
        )

    def _encode_base62(self, data: bytes) -> str:
        """
        Codifica bytes em Base62 (URL-safe, case-sensitive).

        Args:
            data: Bytes para codificar

        Returns:
            String Base62
        """
        ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        BASE = 62

        # Converte bytes para inteiro
        num = int.from_bytes(data, byteorder='big')

        # Codifica em base62
        encoded = []
        while num > 0:
            num, rem = divmod(num, BASE)
            encoded.append(ALPHABET[rem])

        # Inverte e preenche para tamanho fixo
        result = ''.join(reversed(encoded))

        # Para 13 bytes, o máximo em base62 é 17 caracteres
        # Adicionamos padding com zeros à esquerda para 17 caracteres
        return result.rjust(17, '0')

    def _decode_base62(self, encoded: str) -> bytes:
        """
        Decodifica string Base62 para bytes.

        Args:
            encoded: String Base62

        Returns:
            Bytes decodificados

        Raises:
            ValueError: Se string contiver caracteres inválidos
        """
        ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        BASE = 62

        # Converte base62 para inteiro
        num = 0
        for char in encoded:
            if char not in ALPHABET:
                raise ValueError(f"Caractere inválido na string Base62: '{char}'")
            num = num * BASE + ALPHABET.index(char)

        # Converte inteiro para bytes (13 bytes)
        return num.to_bytes(13, byteorder='big')

    def url_key(self) -> str:
        """
        Serializa objeto para string URL-safe extremamente compacta.

        Usa formato binário de 13 bytes + encoding Base62 para 17 caracteres.

        Returns:
            String de 17 caracteres URL-safe
        """
        # Empacota em binário
        binary_data = self._pack_binary()

        # Codifica em Base62
        encoded = self._encode_base62(binary_data)

        logger.debug(f"Gerada url_key de {len(encoded)} caracteres")
        return encoded

    @classmethod
    def from_url_key(cls: Type['Symbology'], url_key: str) -> 'Symbology':
        """
        Reconstrói Symbology a partir de url_key.

        Args:
            url_key: String de 17 caracteres gerada por url_key()

        Returns:
            Nova instância de Symbology

        Raises:
            ValueError: Se url_key for inválida
        """
        try:
            # Verifica tamanho
            if len(url_key) != 17:
                raise ValueError(f"url_key deve ter 17 caracteres, recebidos {len(url_key)}")

            # Decodifica Base62
            binary_data = cls._decode_base62(url_key)

            # Desempacota
            return cls._unpack_binary(binary_data)

        except (ValueError, struct.error, KeyError) as e:
            logger.error(f"Erro ao decodificar url_key: {e}")
            raise ValueError(f"url_key inválida: {url_key}") from e

    def to_matplotlib_patch_kwargs(self) -> Dict[str, Any]:
        """
        Converte a simbologia para kwargs de matplotlib.patches.

        Returns:
            Dicionário com parâmetros para matplotlib patches
        """
        base_kwargs = {}

        # Configuração de preenchimento
        if self.symbology_fill_style == SymbologyFill.NOBRUSH:
            base_kwargs['fill'] = False
        else:
            base_kwargs['fill'] = True

            if self.symbology_fill_style == SymbologyFill.SOLID:
                # Preenchimento sólido
                base_kwargs['facecolor'] = self.symbology_fill_color.as_rgb()
            else:
                # Hatch pattern - facecolor é 'none', hatch usa fill_color
                base_kwargs['facecolor'] = 'none'
                base_kwargs['edgecolor'] = self.symbology_fill_color.as_rgb()  # Hatch color
                base_kwargs['hatch'] = self.symbology_fill_style.value

                # Densidade do hatch
                if self.symbology_fill_density > 1:
                    base_kwargs['hatch'] = base_kwargs['hatch'] * self.symbology_fill_density

        # Configuração da borda/linha
        if self.symbology_stroke_style != LineStyle.NONE:
            base_kwargs.update({
                'edgecolor': self.symbology_stroke_color.as_rgb(),
                'linewidth': self.symbology_stroke_line,
                'linestyle': self.symbology_stroke_style.mpl,
            })

        # Geometria específica
        if self.symbology_geometry_type == SymbologyGeometryType.POLYGON:
            return base_kwargs

        elif self.symbology_geometry_type == SymbologyGeometryType.LINE:
            # Para linhas, removemos o preenchimento
            line_kwargs = base_kwargs.copy()
            line_kwargs['fill'] = False
            if 'facecolor' in line_kwargs:
                del line_kwargs['facecolor']
            if 'hatch' in line_kwargs:
                del line_kwargs['hatch']
            return line_kwargs

        elif self.symbology_geometry_type == SymbologyGeometryType.POINT:
            # Para pontos, ajustamos para círculos
            point_kwargs = base_kwargs.copy()
            if 'linewidth' in point_kwargs:
                point_kwargs['radius'] = max(2.0, self.symbology_stroke_line * 2)
            return point_kwargs

        else:
            raise ValueError(f"Tipo de geometria não suportado: {self.symbology_geometry_type}")

    def to_geoserver_sld(self, layer_name: str = "layer") -> str:
        """
        Converte a simbologia para SLD (Styled Layer Descriptor) do Geoserver.

        Args:
            layer_name: Nome da camada para referência no SLD

        Returns:
            String XML contendo o SLD
        """
        # Namespaces do SLD
        namespaces = {
            'sld': 'http://www.opengis.net/sld',
            'ogc': 'http://www.opengis.net/ogc',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        # Cria elemento raiz
        root = ET.Element('{http://www.opengis.net/sld}StyledLayerDescriptor',
                          {'version': '1.0.0',
                           '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation':
                               'http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd'})

        # NamedLayer
        named_layer = ET.SubElement(root, '{http://www.opengis.net/sld}NamedLayer')
        ET.SubElement(named_layer, '{http://www.opengis.net/sld}Name').text = layer_name

        # UserStyle
        user_style = ET.SubElement(named_layer, '{http://www.opengis.net/sld}UserStyle')
        ET.SubElement(user_style, '{http://www.opengis.net/sld}Name').text = 'style'

        # FeatureTypeStyle
        feature_type_style = ET.SubElement(user_style, '{http://www.opengis.net/sld}FeatureTypeStyle')

        # Regra
        rule = ET.SubElement(feature_type_style, '{http://www.opengis.net/sld}Rule')

        if self.symbology_geometry_type == SymbologyGeometryType.POLYGON:
            self._add_polygon_sld(rule)
        elif self.symbology_geometry_type == SymbologyGeometryType.LINE:
            self._add_line_sld(rule)
        elif self.symbology_geometry_type == SymbologyGeometryType.POINT:
            self._add_point_sld(rule)

        # Converte para string XML formatada
        ET.indent(root, space="  ")
        xml_str = ET.tostring(root, encoding='unicode', method='xml')

        # Adiciona declaração XML
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str

    def _add_polygon_sld(self, rule: ET.Element) -> None:
        """Adiciona símbolo de polígono ao SLD."""
        # PolygonSymbolizer
        polygon_symbolizer = ET.SubElement(rule, '{http://www.opengis.net/sld}PolygonSymbolizer')

        # Preenchimento
        fill = ET.SubElement(polygon_symbolizer, '{http://www.opengis.net/sld}Fill')

        if self.symbology_fill_style == SymbologyFill.NOBRUSH:
            # Sem preenchimento
            ET.SubElement(fill, '{http://www.opengis.net/sld}CssParameter', {'name': 'fill'}).text = '#000000'
            ET.SubElement(fill, '{http://www.opengis.net/sld}CssParameter', {'name': 'fill-opacity'}).text = '0'
        elif self.symbology_fill_style == SymbologyFill.SOLID:
            # Preenchimento sólido
            fill_hex = self.symbology_fill_color.as_hex()
            ET.SubElement(fill, '{http://www.opengis.net/sld}CssParameter', {'name': 'fill'}).text = fill_hex
            ET.SubElement(fill, '{http://www.opengis.net/sld}CssParameter', {'name': 'fill-opacity'}).text = '1'
        else:
            # Hatch pattern - Geoserver não suporta nativamente, usamos GraphicFill
            self._add_hatch_fill_sld(polygon_symbolizer)

        # Borda/Stroke
        if self.symbology_stroke_style != LineStyle.NONE:
            stroke = ET.SubElement(polygon_symbolizer, '{http://www.opengis.net/sld}Stroke')
            stroke_hex = self.symbology_stroke_color.as_hex()
            ET.SubElement(stroke, '{http://www.opengis.net/sld}CssParameter', {'name': 'stroke'}).text = stroke_hex
            ET.SubElement(stroke, '{http://www.opengis.net/sld}CssParameter', {'name': 'stroke-width'}).text = str(self.symbology_stroke_line)

            # Estilo da linha
            if self.symbology_stroke_style != LineStyle.SOLID:
                dash_array = self._line_style_to_dash_array()
                if dash_array:
                    ET.SubElement(stroke, '{http://www.opengis.net/sld}CssParameter', {'name': 'stroke-dasharray'}).text = dash_array

    def _add_hatch_fill_sld(self, polygon_symbolizer: ET.Element) -> None:
        """Adiciona preenchimento com hatch pattern usando GraphicFill."""
        # GraphicFill para hatch patterns
        fill = ET.SubElement(polygon_symbolizer, '{http://www.opengis.net/sld}Fill')
        graphic_fill = ET.SubElement(fill, '{http://www.opengis.net/sld}GraphicFill')
        graphic = ET.SubElement(graphic_fill, '{http://www.opengis.net/sld}Graphic')

        # Define o marcador baseado no padrão de hatch
        mark = ET.SubElement(graphic, '{http://www.opengis.net/sld}Mark')

        # Mapeia padrões para well-known marks do Geoserver
        hatch_to_mark = {
            SymbologyFill.SLASH: 'shape://slash',
            SymbologyFill.BACKSLASH: 'shape://backslash',
            SymbologyFill.PIPE: 'shape://vertline',
            SymbologyFill.DASH: 'shape://horline',
            SymbologyFill.PLUS: 'shape://plus',
            SymbologyFill.X: 'shape://times',
            SymbologyFill.O_LOWER: 'circle',
            SymbologyFill.O_UPPER: 'circle',
            SymbologyFill.DOT: 'circle',
            SymbologyFill.STAR: 'star',
        }

        mark_name = hatch_to_mark.get(self.symbology_fill_style, 'square')
        ET.SubElement(mark, '{http://www.opengis.net/sld}WellKnownName').text = mark_name

        # Cor do hatch
        fill_color = self.symbology_fill_color.as_hex()
        fill_elem = ET.SubElement(mark, '{http://www.opengis.net/sld}Fill')
        ET.SubElement(fill_elem, '{http://www.opengis.net/sld}CssParameter', {'name': 'fill'}).text = fill_color

        # Tamanho baseado na densidade
        size = max(4, self.symbology_fill_density * 4)
        ET.SubElement(graphic, '{http://www.opengis.net/sld}Size').text = str(size)

    def _add_line_sld(self, rule: ET.Element) -> None:
        """Adiciona símbolo de linha ao SLD."""
        # LineSymbolizer
        line_symbolizer = ET.SubElement(rule, '{http://www.opengis.net/sld}LineSymbolizer')
        stroke = ET.SubElement(line_symbolizer, '{http://www.opengis.net/sld}Stroke')

        # Cor da linha
        stroke_hex = self.symbology_stroke_color.as_hex()
        ET.SubElement(stroke, '{http://www.opengis.net/sld}CssParameter', {'name': 'stroke'}).text = stroke_hex

        # Espessura
        ET.SubElement(stroke, '{http://www.opengis.net/sld}CssParameter', {'name': 'stroke-width'}).text = str(self.symbology_stroke_line)

        # Estilo da linha
        if self.symbology_stroke_style != LineStyle.SOLID:
            dash_array = self._line_style_to_dash_array()
            if dash_array:
                ET.SubElement(stroke, '{http://www.opengis.net/sld}CssParameter', {'name': 'stroke-dasharray'}).text = dash_array

    def _add_point_sld(self, rule: ET.Element) -> None:
        """Adiciona símbolo de ponto ao SLD."""
        # PointSymbolizer
        point_symbolizer = ET.SubElement(rule, '{http://www.opengis.net/sld}PointSymbolizer')
        graphic = ET.SubElement(point_symbolizer, '{http://www.opengis.net/sld}Graphic')

        # Define o marcador
        mark = ET.SubElement(graphic, '{http://www.opengis.net/sld}Mark')
        ET.SubElement(mark, '{http://www.opengis.net/sld}WellKnownName').text = 'circle'

        # Preenchimento do marcador
        fill = ET.SubElement(mark, '{http://www.opengis.net/sld}Fill')
        if self.symbology_fill_style == SymbologyFill.NOBRUSH:
            ET.SubElement(fill, '{http://www.opengis.net/sld}CssParameter', {'name': 'fill'}).text = '#000000'
            ET.SubElement(fill, '{http://www.opengis.net/sld}CssParameter', {'name': 'fill-opacity'}).text = '0'
        else:
            fill_hex = self.symbology_fill_color.as_hex()
            ET.SubElement(fill, '{http://www.opengis.net/sld}CssParameter', {'name': 'fill'}).text = fill_hex
            ET.SubElement(fill, '{http://www.opengis.net/sld}CssParameter', {'name': 'fill-opacity'}).text = '1'

        # Borda do marcador
        if self.symbology_stroke_style != LineStyle.NONE:
            stroke = ET.SubElement(mark, '{http://www.opengis.net/sld}Stroke')
            stroke_hex = self.symbology_stroke_color.as_hex()
            ET.SubElement(stroke, '{http://www.opengis.net/sld}CssParameter', {'name': 'stroke'}).text = stroke_hex
            ET.SubElement(stroke, '{http://www.opengis.net/sld}CssParameter', {'name': 'stroke-width'}).text = str(self.symbology_stroke_line)

        # Tamanho do ponto
        size = max(6, self.symbology_stroke_line * 4)
        ET.SubElement(graphic, '{http://www.opengis.net/sld}Size').text = str(size)

    def _line_style_to_dash_array(self) -> str:
        """Converte LineStyle para array de dash do Geoserver."""
        # Valores típicos para dash arrays no Geoserver
        dash_map = {
            LineStyle.DASHED: "5 5",
            LineStyle.DOTTED: "1 5",
            LineStyle.DASH_DOT: "5 5 1 5",
            LineStyle.LONG_DASH: "10 5",
            LineStyle.SHORT_DASH: "3 3",
            LineStyle.DASH_DOT_DOT: "5 5 1 5 1 5",
            LineStyle.DASH_DOT_DOT_DOT: "5 5 1 5 1 5 1 5",
            LineStyle.SPARSE_DOT: "1 10",
            LineStyle.DENSE_DOT: "1 2",
        }
        return dash_map.get(self.symbology_stroke_style, "")

    def to_geoserver_css(self) -> str:
        """
        Converte a simbologia para CSS do Geoserver.

        Returns:
            String CSS para estilização no Geoserver
        """
        css_lines = []

        if self.symbology_geometry_type == SymbologyGeometryType.POLYGON:
            css_lines.append("* {")

            # Preenchimento
            if self.symbology_fill_style == SymbologyFill.NOBRUSH:
                css_lines.append("  fill: #000000;")
                css_lines.append("  fill-opacity: 0;")
            elif self.symbology_fill_style == SymbologyFill.SOLID:
                fill_hex = self.symbology_fill_color.as_hex()
                css_lines.append(f"  fill: {fill_hex};")
                css_lines.append("  fill-opacity: 1;")
            else:
                # Hatch patterns em CSS - usando pattern
                fill_hex = self.symbology_fill_color.as_hex()
                hatch_pattern = self._get_css_hatch_pattern()
                css_lines.append(f"  fill: {hatch_pattern};")
                css_lines.append(f"  fill-color: {fill_hex};")

            # Borda
            if self.symbology_stroke_style != LineStyle.NONE:
                stroke_hex = self.symbology_stroke_color.as_hex()
                css_lines.append(f"  stroke: {stroke_hex};")
                css_lines.append(f"  stroke-width: {self.symbology_stroke_line};")

                if self.symbology_stroke_style != LineStyle.SOLID:
                    dash_array = self._line_style_to_dash_array()
                    css_lines.append(f"  stroke-dasharray: {dash_array};")
            else:
                css_lines.append("  stroke: none;")

            css_lines.append("}")

        elif self.symbology_geometry_type == SymbologyGeometryType.LINE:
            css_lines.append("* {")
            css_lines.append("  stroke: " + self.symbology_stroke_color.as_hex() + ";")
            css_lines.append(f"  stroke-width: {self.symbology_stroke_line};")

            if self.symbology_stroke_style != LineStyle.SOLID:
                dash_array = self._line_style_to_dash_array()
                css_lines.append(f"  stroke-dasharray: {dash_array};")

            css_lines.append("}")

        elif self.symbology_geometry_type == SymbologyGeometryType.POINT:
            css_lines.append("* {")

            # Define o marcador
            css_lines.append("  mark: symbol(circle);")

            # Preenchimento
            if self.symbology_fill_style == SymbologyFill.NOBRUSH:
                css_lines.append("  mark-fill: #000000;")
                css_lines.append("  mark-fill-opacity: 0;")
            else:
                css_lines.append("  mark-fill: " + self.symbology_fill_color.as_hex() + ";")
                css_lines.append("  mark-fill-opacity: 1;")

            # Borda
            if self.symbology_stroke_style != LineStyle.NONE:
                css_lines.append("  mark-stroke: " + self.symbology_stroke_color.as_hex() + ";")
                css_lines.append(f"  mark-stroke-width: {self.symbology_stroke_line};")
            else:
                css_lines.append("  mark-stroke: none;")

            # Tamanho
            size = max(6, self.symbology_stroke_line * 4)
            css_lines.append(f"  mark-size: {size};")

            css_lines.append("}")

        return '\n'.join(css_lines)

    def _get_css_hatch_pattern(self) -> str:
        """Retorna padrão de hatch para CSS."""
        # Geoserver CSS suporta alguns padrões básicos
        pattern_map = {
            SymbologyFill.SLASH: "symbol('shape://slash')",
            SymbologyFill.BACKSLASH: "symbol('shape://backslash')",
            SymbologyFill.PIPE: "symbol('shape://vertline')",
            SymbologyFill.DASH: "symbol('shape://horline')",
            SymbologyFill.PLUS: "symbol('shape://plus')",
            SymbologyFill.X: "symbol('shape://times')",
            SymbologyFill.O_LOWER: "symbol('circle')",
            SymbologyFill.O_UPPER: "symbol('circle')",
            SymbologyFill.DOT: "symbol('circle')",
            SymbologyFill.STAR: "symbol('star')",
        }
        return pattern_map.get(self.symbology_fill_style, "symbol('square')")

    def to_geoserver_rest_payload(self) -> Dict[str, Any]:
        """
        Converte a simbologia para payload da API REST do Geoserver.

        Returns:
            Dicionário no formato esperado pela API REST do Geoserver
        """
        payload = {
            "style": {
                "name": "generated_style",
                "filename": "generated_style.sld"
            }
        }

        # Adiciona o SLD como conteúdo
        sld_content = self.to_geoserver_sld()
        payload["style"]["body"] = sld_content

        return payload


def _run_tests() -> None:
    """Suite de testes básicos para validação."""
    logger.info("Iniciando testes de Symbology com Geoserver")

    # Teste 1: Polígono sólido com borda
    s1 = Symbology(
        symbology_geometry_type=SymbologyGeometryType.POLYGON,
        symbology_fill_color=Color("#ff0000"),
        symbology_fill_style=SymbologyFill.SOLID,
        symbology_fill_density=0,
        symbology_stroke_color=Color("#0000ff"),
        symbology_stroke_style=LineStyle.DASHED,
        symbology_stroke_line=2.0,
    )

    sld1 = s1.to_geoserver_sld("test_polygon")
    logger.info(f"SLD polígono (primeiras linhas):")
    for line in sld1.split('\n')[:10]:
        logger.info(f"  {line}")

    assert "<sld:PolygonSymbolizer>" in sld1
    assert "#ff0000" in sld1
    assert "stroke-dasharray" in sld1
    logger.success("✅ SLD polígono funciona")

    # Teste 2: Polígono com hatch
    s2 = Symbology(
        symbology_geometry_type=SymbologyGeometryType.POLYGON,
        symbology_fill_color=Color("#00ff00"),
        symbology_fill_style=SymbologyFill.SLASH,
        symbology_fill_density=3,
        symbology_stroke_color=Color("#000000"),
        symbology_stroke_style=LineStyle.NONE,
        symbology_stroke_line=0.0,
    )

    sld2 = s2.to_geoserver_sld("test_hatch")
    logger.info(f"SLD hatch (primeiras linhas):")
    for line in sld2.split('\n')[:10]:
        logger.info(f"  {line}")

    assert "GraphicFill" in sld2
    assert "shape://slash" in sld2
    logger.success("✅ SLD hatch funciona")

    # Teste 3: Linha