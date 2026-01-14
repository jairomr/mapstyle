"""
Testes para o módulo symbology.

Valida funcionalidades de simbologia geoespacial:
- Criação e validação de objetos Symbology
- Serialização para diferentes formatos
- Codificação/decodificação URL-safe
- Geração de estilos para matplotlib e Geoserver
"""

import pytest
import struct
from xml.etree import ElementTree as ET

from pydantic_extra_types.color import Color

from scr.core.model.symbology import (
    LineStyle,
    SymbologyGeometryType,
    SymbologyFill,
    Symbology,
)


class TestLineStyle:
    """Testes para a enumeração LineStyle."""

    def test_linestyle_solid_properties(self):
        """Verifica propriedades do estilo SOLID."""
        assert LineStyle.SOLID.code == 0
        assert LineStyle.SOLID.repr == '────'
        assert str(LineStyle.SOLID) == '────'

    def test_linestyle_dashed_properties(self):
        """Verifica propriedades do estilo DASHED."""
        assert LineStyle.DASHED.code == 1
        assert LineStyle.DASHED.repr == '--'

    def test_linestyle_from_code_valid(self):
        """Testa recuperação de LineStyle por código válido."""
        assert LineStyle.from_code(0) == LineStyle.SOLID
        assert LineStyle.from_code(1) == LineStyle.DASHED
        assert LineStyle.from_code(10) == LineStyle.NONE

    def test_linestyle_from_code_invalid(self):
        """Testa exceção com código inválido."""
        with pytest.raises(ValueError, match="Código LineStyle inválido"):
            LineStyle.from_code(999)

    def test_linestyle_all_codes_valid(self):
        """Verifica que todos os estilos podem ser recuperados por código."""
        for style in LineStyle:
            recovered = LineStyle.from_code(style.code)
            assert recovered == style


class TestSymbologyGeometryType:
    """Testes para a enumeração SymbologyGeometryType."""

    def test_geometry_types_exist(self):
        """Verifica que todos os tipos de geometria estão definidos."""
        assert SymbologyGeometryType.POLYGON.value == "POLYGON"
        assert SymbologyGeometryType.LINE.value == "LINE"
        assert SymbologyGeometryType.POINT.value == "POINT"


class TestSymbologyFill:
    """Testes para a enumeração SymbologyFill."""

    def test_fill_solid(self):
        """Verifica padrão SOLID."""
        assert SymbologyFill.SOLID.value == "SOLID"

    def test_fill_patterns(self):
        """Verifica padrões de hatch."""
        assert SymbologyFill.SLASH.value == '/'
        assert SymbologyFill.BACKSLASH.value == '\\'
        assert SymbologyFill.PIPE.value == '|'
        assert SymbologyFill.DASH.value == '-'


class TestSymbologyCreation:
    """Testes para criação de objetos Symbology."""

    @pytest.fixture
    def valid_symbology(self):
        """Fixture com objeto Symbology válido."""
        return Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.5,
        )

    def test_symbology_creation_valid(self, valid_symbology):
        """Verifica criação de Symbology válida."""
        assert valid_symbology.symbology_geometry_type == SymbologyGeometryType.POLYGON
        assert valid_symbology.symbology_fill_density == 5
        assert valid_symbology.symbology_stroke_line == 2.5

    def test_symbology_frozen(self, valid_symbology):
        """Verifica que Symbology é imutável."""
        with pytest.raises(Exception):
            valid_symbology.symbology_fill_density = 10

    def test_symbology_fill_density_validation(self):
        """Testa validação de densidade de preenchimento."""
        # Válido
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        assert symbology.symbology_fill_density == 0

        # Inválido (fora do range)
        with pytest.raises(Exception):
            Symbology(
                symbology_geometry_type=SymbologyGeometryType.POLYGON,
                symbology_fill_color=Color("#ff0000"),
                symbology_fill_style=SymbologyFill.SOLID,
                symbology_fill_density=11,  # Maior que 10
                symbology_stroke_color=Color("#0000ff"),
                symbology_stroke_style=LineStyle.SOLID,
                symbology_stroke_line=1.0,
            )

    def test_symbology_stroke_line_validation(self):
        """Testa validação de espessura de linha."""
        # Válido
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.LINE,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=50.0,
        )
        assert symbology.symbology_stroke_line == 50.0

        # Inválido (acima do máximo)
        with pytest.raises(Exception):
            Symbology(
                symbology_geometry_type=SymbologyGeometryType.LINE,
                symbology_fill_color=Color("#ff0000"),
                symbology_fill_style=SymbologyFill.SOLID,
                symbology_fill_density=0,
                symbology_stroke_color=Color("#0000ff"),
                symbology_stroke_style=LineStyle.SOLID,
                symbology_stroke_line=51.0,
            )

    def test_symbology_stroke_line_normalization(self):
        """Testa normalização de espessura da linha para 3 casas decimais."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=2.456789,
        )
        assert symbology.symbology_stroke_line == 2.457


class TestSymbologyCacheKey:
    """Testes para geração de cache_key."""

    def test_cache_key_returns_tuple(self):
        """Verifica que cache_key retorna tupla."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        key = symbology.cache_key()
        assert isinstance(key, tuple)
        assert len(key) == 7

    def test_cache_key_consistency(self):
        """Verifica que mesmas entradas geram mesma cache_key."""
        s1 = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        s2 = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        assert s1.cache_key() == s2.cache_key()

    def test_cache_key_different_for_different_values(self):
        """Verifica que valores diferentes geram cache_keys diferentes."""
        s1 = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        s2 = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#00ff00"),  # Diferente
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        assert s1.cache_key() != s2.cache_key()


class TestSymbologyHash:
    """Testes para hash de Symbology."""

    def test_symbology_is_hashable(self):
        """Verifica que Symbology é hashável."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        h = hash(symbology)
        assert isinstance(h, int)

    def test_same_symbology_same_hash(self):
        """Verifica que mesmas entradas têm mesmo hash."""
        s1 = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        s2 = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        assert hash(s1) == hash(s2)

    def test_symbology_in_set(self):
        """Verifica que Symbology pode ser usado em sets."""
        s1 = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        s2 = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#00ff00"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        symbol_set = {s1, s2}
        assert len(symbol_set) == 2
        assert s1 in symbol_set


class TestSymbologyBinarySerialization:
    """Testes para serialização binária (13 bytes)."""

    def test_pack_binary_returns_13_bytes(self):
        """Verifica que empacotamento binário retorna 13 bytes."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        binary = symbology._pack_binary()
        assert isinstance(binary, bytes)
        assert len(binary) == 13

    def test_pack_unpack_round_trip(self):
        """Verifica que pack seguido de unpack retorna Symbology equivalente."""
        original = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.345,
        )
        binary = original._pack_binary()
        recovered = Symbology._unpack_binary(binary)

        assert recovered.symbology_geometry_type == original.symbology_geometry_type
        assert recovered.symbology_fill_density == original.symbology_fill_density
        assert recovered.symbology_stroke_style == original.symbology_stroke_style
        # Verifica que stroke_line é recuperado com a precisão esperada
        assert abs(recovered.symbology_stroke_line - original.symbology_stroke_line) < 0.001

    def test_unpack_binary_invalid_size(self):
        """Testa exceção com tamanho inválido."""
        with pytest.raises(ValueError, match="Dados devem ter 13 bytes"):
            Symbology._unpack_binary(b"too_short")

    def test_unpack_binary_invalid_density(self):
        """Testa exceção com densidade inválida."""
        # Cria bytes com densidade > 10
        invalid_data = struct.pack(
            '>B3B B B3B B H B',
            0, 255, 0, 0,  # geom, fill_r, fill_g, fill_b
            0, 11,  # fill_style, fill_density (inválido: 11)
            0, 0, 255, 0, 0, 0  # stroke_r, stroke_g, stroke_b, stroke_style, stroke_line, reserved
        )
        with pytest.raises(ValueError, match="Densidade inválida"):
            Symbology._unpack_binary(invalid_data)

    def test_unpack_binary_invalid_stroke_line(self):
        """Testa exceção com espessura de linha inválida."""
        # Cria bytes com stroke_line > 50000 (50.0 * 1000)
        invalid_data = struct.pack(
            '>B3B B B3B B H B',
            0, 255, 0, 0,  # geom, fill_r, fill_g, fill_b
            0, 5,  # fill_style, fill_density
            0, 0, 255, 0, 51000, 0  # stroke_r, stroke_g, stroke_b, stroke_style, stroke_line (inválido), reserved
        )
        with pytest.raises(ValueError, match="Espessura inválida"):
            Symbology._unpack_binary(invalid_data)


class TestSymbologyBase62Encoding:
    """Testes para codificação Base62."""

    def test_encode_base62_returns_17_chars(self):
        """Verifica que codificação retorna 17 caracteres."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        # Testa com dados binários reais
        binary = symbology._pack_binary()
        encoded = symbology._encode_base62(binary)
        assert len(encoded) == 17

    def test_decode_base62_invalid_char(self):
        """Testa exceção com caractere inválido em Base62."""
        with pytest.raises(ValueError, match="Caractere inválido"):
            Symbology._decode_base62("invalid!char00000")


class TestSymbologyURLKey:
    """Testes para serialização URL-safe."""

    def test_url_key_length(self):
        """Verifica que url_key tem 17 caracteres."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        key = symbology.url_key()
        assert len(key) == 17

    def test_url_key_is_base62(self):
        """Verifica que url_key contém apenas caracteres Base62."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        key = symbology.url_key()
        ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        for char in key:
            assert char in ALPHABET

    def test_from_url_key_round_trip(self):
        """Verifica round-trip url_key -> Symbology -> url_key."""
        original = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=5,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.345,
        )
        url_key = original.url_key()
        recovered = Symbology.from_url_key(url_key)

        # Verifica que os atributos principais são iguais
        assert recovered.symbology_geometry_type == original.symbology_geometry_type
        assert recovered.symbology_fill_density == original.symbology_fill_density
        assert recovered.symbology_stroke_style == original.symbology_stroke_style
        assert abs(recovered.symbology_stroke_line - original.symbology_stroke_line) < 0.001

    def test_from_url_key_invalid_length(self):
        """Testa exceção com url_key de tamanho inválido."""
        with pytest.raises(ValueError):
            Symbology.from_url_key("short")

    def test_from_url_key_invalid_format(self):
        """Testa exceção com url_key inválido."""
        with pytest.raises(ValueError):
            Symbology.from_url_key("invalid!char00000")


class TestSymbologyMatplotlib:
    """Testes para geração de kwargs de matplotlib."""

    def test_matplotlib_polygon_solid_fill(self):
        """Testa kwargs para polígono com preenchimento sólido."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        kwargs = symbology.to_matplotlib_patch_kwargs()

        assert kwargs['fill'] is True
        assert 'facecolor' in kwargs
        # edgecolor pode ser rgb ou hex
        assert 'edgecolor' in kwargs or kwargs.get('edgecolor') == (0, 0, 1)
        assert kwargs['linewidth'] == 2.0

    def test_matplotlib_polygon_no_fill(self):
        """Testa kwargs para polígono sem preenchimento."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.NOBRUSH,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        kwargs = symbology.to_matplotlib_patch_kwargs()

        assert kwargs['fill'] is False

    def test_matplotlib_polygon_hatch_pattern(self):
        """Testa kwargs para polígono com padrão hatch."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SLASH,
            symbology_fill_density=2,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        kwargs = symbology.to_matplotlib_patch_kwargs()

        assert kwargs['fill'] is True
        assert 'hatch' in kwargs
        assert kwargs['hatch'] == '//'
        assert kwargs['facecolor'] == 'none'

    def test_matplotlib_line(self):
        """Testa kwargs para linha."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.LINE,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        kwargs = symbology.to_matplotlib_patch_kwargs()

        assert kwargs['fill'] is False
        assert 'facecolor' not in kwargs
        assert 'edgecolor' in kwargs
        assert kwargs['linewidth'] == 2.0

    def test_matplotlib_point(self):
        """Testa kwargs para ponto."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POINT,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=2.0,
        )
        kwargs = symbology.to_matplotlib_patch_kwargs()

        assert 'radius' in kwargs
        assert kwargs['radius'] == 4.0


class TestSymbologyGeoServerSLD:
    """Testes para geração de SLD (Styled Layer Descriptor)."""

    def test_sld_polygon_solid(self):
        """Testa geração de SLD para polígono sólido."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        sld = symbology.to_geoserver_sld("test_polygon")

        assert sld.startswith('<?xml version="1.0"')
        # O XML pode usar prefixo ns0 ao invés de sld
        assert "PolygonSymbolizer>" in sld
        assert "ff0000" in sld.lower() or "f00" in sld.lower()
        assert "stroke-dasharray" in sld

    def test_sld_polygon_with_hatch(self):
        """Testa geração de SLD para polígono com hatch."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#00ff00"),
            symbology_fill_style=SymbologyFill.SLASH,
            symbology_fill_density=3,
            symbology_stroke_color=Color("#000000"),
            symbology_stroke_style=LineStyle.NONE,
            symbology_stroke_line=0.0,
        )
        sld = symbology.to_geoserver_sld("test_hatch")

        assert "GraphicFill" in sld
        assert "shape://slash" in sld

    def test_sld_line(self):
        """Testa geração de SLD para linha."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.LINE,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DOTTED,
            symbology_stroke_line=1.5,
        )
        sld = symbology.to_geoserver_sld("test_line")

        assert "LineSymbolizer>" in sld
        assert "stroke" in sld

    def test_sld_point(self):
        """Testa geração de SLD para ponto."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POINT,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        sld = symbology.to_geoserver_sld("test_point")

        assert "PointSymbolizer>" in sld
        assert "circle" in sld

    def test_sld_valid_xml(self):
        """Verifica que SLD gerado é XML válido."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        sld = symbology.to_geoserver_sld("test")

        # Tenta fazer parse do XML
        try:
            ET.fromstring(sld)
        except ET.ParseError as e:
            pytest.fail(f"SLD XML inválido: {e}")


class TestSymbologyGeoServerCSS:
    """Testes para geração de CSS do Geoserver."""

    def test_css_polygon_solid(self):
        """Testa geração de CSS para polígono sólido."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.DASHED,
            symbology_stroke_line=2.0,
        )
        css = symbology.to_geoserver_css()

        assert "fill:" in css
        assert "stroke:" in css
        # Color pode ser serializada como #fff ou #ffffff ou f00
        assert "fill:" in css and ("f0" in css.lower() or "red" in css.lower())

    def test_css_polygon_no_fill(self):
        """Testa geração de CSS para polígono sem preenchimento."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.NOBRUSH,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        css = symbology.to_geoserver_css()

        assert "fill-opacity: 0" in css

    def test_css_polygon_hatch(self):
        """Testa geração de CSS para polígono com hatch."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#00ff00"),
            symbology_fill_style=SymbologyFill.SLASH,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#000000"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        css = symbology.to_geoserver_css()

        assert "shape://slash" in css

    def test_css_line(self):
        """Testa geração de CSS para linha."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.LINE,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.5,
        )
        css = symbology.to_geoserver_css()

        assert "stroke:" in css

    def test_css_point(self):
        """Testa geração de CSS para ponto."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POINT,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        css = symbology.to_geoserver_css()

        assert "mark:" in css
        assert "circle" in css


class TestSymbologyGeoServerRESTPayload:
    """Testes para payload REST do Geoserver."""

    def test_rest_payload_structure(self):
        """Verifica estrutura do payload REST."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        payload = symbology.to_geoserver_rest_payload()

        assert "style" in payload
        assert "name" in payload["style"]
        assert "body" in payload["style"]
        assert "filename" in payload["style"]

    def test_rest_payload_contains_sld(self):
        """Verifica que payload contém SLD válido."""
        symbology = Symbology(
            symbology_geometry_type=SymbologyGeometryType.POLYGON,
            symbology_fill_color=Color("#ff0000"),
            symbology_fill_style=SymbologyFill.SOLID,
            symbology_fill_density=0,
            symbology_stroke_color=Color("#0000ff"),
            symbology_stroke_style=LineStyle.SOLID,
            symbology_stroke_line=1.0,
        )
        payload = symbology.to_geoserver_rest_payload()

        assert payload["style"]["body"].startswith('<?xml version="1.0"')
        assert "PolygonSymbolizer>" in payload["style"]["body"]
