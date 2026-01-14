"""
Testes para API FastAPI de Symbology.

Testa os endpoints de criação, consulta e exportação de simbologias.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic_extra_types.color import Color

from scr.api.main import app
from scr.core.model.symbology import Symbology, SymbologyGeometryType, SymbologyFill, LineStyle

client = TestClient(app)


@pytest.fixture
def valid_symbology_dict():
    """Fixture com dados válidos de simbologia."""
    return {
        "symbology_geometry_type": "POLYGON",
        "symbology_fill_color": "#ff0000",
        "symbology_fill_style": "SOLID",
        "symbology_fill_density": 0,
        "symbology_stroke_color": "#0000ff",
        "symbology_stroke_style": "DASHED",
        "symbology_stroke_line": 2.0,
    }


@pytest.fixture
def valid_symbology():
    """Fixture com objeto Symbology válido."""
    return Symbology(
        symbology_geometry_type=SymbologyGeometryType.POLYGON,
        symbology_fill_color=Color("#ff0000"),
        symbology_fill_style=SymbologyFill.SOLID,
        symbology_fill_density=0,
        symbology_stroke_color=Color("#0000ff"),
        symbology_stroke_style=LineStyle.DASHED,
        symbology_stroke_line=2.0,
    )


class TestHealthEndpoint:
    """Testes para health check."""

    def test_health_check(self):
        """Testa GET /health."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_endpoint(self):
        """Testa GET /."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestCreateSymbology:
    """Testes para criação de simbologia."""

    def test_create_symbology_polygon(self, valid_symbology_dict):
        """Testa POST /api/symbology com polígono."""
        response = client.post("/api/symbology", json=valid_symbology_dict)

        assert response.status_code == 200
        data = response.json()

        # Verifica estrutura da resposta
        assert "url_key" in data
        assert "matplotlib_url" in data
        assert "preview_url" in data
        assert "symbology" in data

        # Verifica url_key (17 caracteres)
        assert len(data["url_key"]) == 17

        # Verifica URLs
        assert f"/api/result/{data['url_key']}/json" == data["matplotlib_url"]
        assert f"/api/result/{data['url_key']}/png" == data["preview_url"]

    def test_create_symbology_line(self, valid_symbology_dict):
        """Testa POST /api/symbology com linha."""
        valid_symbology_dict["symbology_geometry_type"] = "LINE"
        response = client.post("/api/symbology", json=valid_symbology_dict)

        assert response.status_code == 200
        assert "url_key" in response.json()

    def test_create_symbology_point(self, valid_symbology_dict):
        """Testa POST /api/symbology com ponto."""
        valid_symbology_dict["symbology_geometry_type"] = "POINT"
        response = client.post("/api/symbology", json=valid_symbology_dict)

        assert response.status_code == 200
        assert "url_key" in response.json()

    def test_create_symbology_invalid_density(self, valid_symbology_dict):
        """Testa POST /api/symbology com densidade inválida."""
        valid_symbology_dict["symbology_fill_density"] = 11  # > 10
        response = client.post("/api/symbology", json=valid_symbology_dict)

        assert response.status_code == 400

    def test_create_symbology_invalid_stroke_line(self, valid_symbology_dict):
        """Testa POST /api/symbology com espessura de linha inválida."""
        valid_symbology_dict["symbology_stroke_line"] = 51.0  # > 50.0
        response = client.post("/api/symbology", json=valid_symbology_dict)

        assert response.status_code == 400


class TestGetConfig:
    """Testes para obtenção de configurações."""

    def test_get_config_valid_url_key(self, valid_symbology_dict):
        """Testa GET /api/result/{url_key}/json com url_key válida."""
        # Cria simbologia primeiro
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        # Obtém config
        response = client.get(f"/api/result/{url_key}/json")

        assert response.status_code == 200
        data = response.json()

        # Verifica estrutura
        assert "url_key" in data
        assert "matplotlib" in data
        assert "geoserver" in data
        assert "symbology" in data

        # Verifica url_key
        assert data["url_key"] == url_key

        # Verifica matplotlib config
        assert "fill" in data["matplotlib"]
        assert "edgecolor" in data["matplotlib"]
        assert "linewidth" in data["matplotlib"]

        # Verifica geoserver config
        assert "sld" in data["geoserver"]
        assert "css" in data["geoserver"]
        assert "rest_payload" in data["geoserver"]

        # Verifica que SLD começa com XML declaration
        assert data["geoserver"]["sld"].startswith("<?xml")

        # Verifica que CSS tem o símbolo *
        assert "* {" in data["geoserver"]["css"]

    def test_get_config_invalid_url_key(self):
        """Testa GET /api/result/{url_key}/json com url_key inválida."""
        response = client.get("/api/result/invalid_key/json")

        assert response.status_code == 400
        assert "Invalid url_key" in response.json()["detail"]

    def test_get_config_invalid_format(self):
        """Testa GET /api/result/{url_key}/json com formato inválido."""
        # url_key com caractere inválido
        response = client.get("/api/result/invalid!char00000/json")

        assert response.status_code == 400

    def test_get_config_short_url_key(self):
        """Testa GET /api/result/{url_key}/json com url_key muito curta."""
        response = client.get("/api/result/short/json")

        assert response.status_code == 400


class TestGeoServerSLD:
    """Testes para endpoint SLD do GeoServer."""

    def test_get_sld_valid_url_key(self, valid_symbology_dict):
        """Testa GET /api/result/{url_key}/sld."""
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/sld")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml"
        assert response.text.startswith("<?xml")
        assert "PolygonSymbolizer" in response.text or "Symbolizer>" in response.text

    def test_get_sld_with_layer_name(self, valid_symbology_dict):
        """Testa GET /api/result/{url_key}/sld?layer_name=custom."""
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/sld?layer_name=my_layer")

        assert response.status_code == 200
        assert "my_layer" in response.text

    def test_get_sld_invalid_url_key(self):
        """Testa GET /api/result/{url_key}/sld com url_key inválida."""
        response = client.get("/api/result/invalid_key/sld")

        assert response.status_code == 400

    def test_get_sld_polygon(self, valid_symbology_dict):
        """Testa SLD para polígono."""
        valid_symbology_dict["symbology_geometry_type"] = "POLYGON"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/sld")

        assert response.status_code == 200
        assert "PolygonSymbolizer" in response.text or "Polygon" in response.text

    def test_get_sld_line(self, valid_symbology_dict):
        """Testa SLD para linha."""
        valid_symbology_dict["symbology_geometry_type"] = "LINE"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/sld")

        assert response.status_code == 200
        assert "LineSymbolizer" in response.text or "Line" in response.text

    def test_get_sld_point(self, valid_symbology_dict):
        """Testa SLD para ponto."""
        valid_symbology_dict["symbology_geometry_type"] = "POINT"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/sld")

        assert response.status_code == 200
        assert "PointSymbolizer" in response.text or "Point" in response.text


class TestGeoServerCSS:
    """Testes para endpoint CSS do GeoServer."""

    def test_get_css_valid_url_key(self, valid_symbology_dict):
        """Testa GET /api/result/{url_key}/css."""
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/css")

        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]
        assert "* {" in response.text
        assert "fill:" in response.text or "stroke:" in response.text

    def test_get_css_invalid_url_key(self):
        """Testa GET /api/result/{url_key}/css com url_key inválida."""
        response = client.get("/api/result/invalid_key/css")

        assert response.status_code == 400

    def test_get_css_polygon(self, valid_symbology_dict):
        """Testa CSS para polígono."""
        valid_symbology_dict["symbology_geometry_type"] = "POLYGON"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/css")

        assert response.status_code == 200
        assert "fill:" in response.text

    def test_get_css_line(self, valid_symbology_dict):
        """Testa CSS para linha."""
        valid_symbology_dict["symbology_geometry_type"] = "LINE"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/css")

        assert response.status_code == 200
        assert "stroke:" in response.text

    def test_get_css_point(self, valid_symbology_dict):
        """Testa CSS para ponto."""
        valid_symbology_dict["symbology_geometry_type"] = "POINT"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/css")

        assert response.status_code == 200
        assert "mark:" in response.text


class TestGeoServerREST:
    """Testes para endpoint REST do GeoServer."""

    def test_get_rest_valid_url_key(self, valid_symbology_dict):
        """Testa GET /api/result/{url_key}/rest."""
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/rest")

        assert response.status_code == 200
        data = response.json()

        # Verifica estrutura do payload REST
        assert "style" in data
        assert "name" in data["style"]
        assert "filename" in data["style"]
        assert "body" in data["style"]

    def test_get_rest_payload_contains_sld(self, valid_symbology_dict):
        """Testa que payload REST contém SLD válido."""
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/rest")

        assert response.status_code == 200
        data = response.json()
        assert data["style"]["body"].startswith("<?xml")

    def test_get_rest_invalid_url_key(self):
        """Testa GET /api/result/{url_key}/rest com url_key inválida."""
        response = client.get("/api/result/invalid_key/rest")

        assert response.status_code == 400

    def test_get_rest_polygon(self, valid_symbology_dict):
        """Testa REST payload para polígono."""
        valid_symbology_dict["symbology_geometry_type"] = "POLYGON"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/rest")

        assert response.status_code == 200
        assert "PolygonSymbolizer" in response.json()["style"]["body"] or \
               "Polygon" in response.json()["style"]["body"]


class TestGetPreview:
    """Testes para obtenção de preview PNG."""

    def test_get_preview_default_size(self, valid_symbology_dict):
        """Testa GET /api/result/{url_key}/png com tamanho padrão."""
        # Cria simbologia primeiro
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        # Obtém preview
        response = client.get(f"/api/result/{url_key}/png")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

        # Verifica que é uma imagem PNG válida
        assert response.content.startswith(b"\x89PNG")

    def test_get_preview_custom_size(self, valid_symbology_dict):
        """Testa GET /api/result/{url_key}/png com tamanho customizado."""
        # Cria simbologia primeiro
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        # Obtém preview com tamanho 300
        response = client.get(f"/api/result/{url_key}/png?size=300")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.content.startswith(b"\x89PNG")

    def test_get_preview_invalid_size_too_small(self, valid_symbology_dict):
        """Testa GET /api/result/{url_key}/png com tamanho muito pequeno."""
        # Cria simbologia primeiro
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        # Tenta tamanho < 50
        response = client.get(f"/api/result/{url_key}/png?size=30")

        assert response.status_code == 422  # Validation error

    def test_get_preview_invalid_size_too_large(self, valid_symbology_dict):
        """Testa GET /api/result/{url_key}/png com tamanho muito grande."""
        # Cria simbologia primeiro
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        # Tenta tamanho > 1000
        response = client.get(f"/api/result/{url_key}/png?size=2000")

        assert response.status_code == 422  # Validation error

    def test_get_preview_invalid_url_key(self):
        """Testa GET /api/result/{url_key}/png com url_key inválida."""
        response = client.get("/api/result/invalid_key/png")

        assert response.status_code == 400

    def test_get_preview_polygon(self, valid_symbology_dict):
        """Testa preview para polígono."""
        valid_symbology_dict["symbology_geometry_type"] = "POLYGON"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/png")

        assert response.status_code == 200
        assert response.content.startswith(b"\x89PNG")

    def test_get_preview_line(self, valid_symbology_dict):
        """Testa preview para linha."""
        valid_symbology_dict["symbology_geometry_type"] = "LINE"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/png")

        assert response.status_code == 200
        assert response.content.startswith(b"\x89PNG")

    def test_get_preview_point(self, valid_symbology_dict):
        """Testa preview para ponto."""
        valid_symbology_dict["symbology_geometry_type"] = "POINT"
        create_response = client.post("/api/symbology", json=valid_symbology_dict)
        url_key = create_response.json()["url_key"]

        response = client.get(f"/api/result/{url_key}/png")

        assert response.status_code == 200
        assert response.content.startswith(b"\x89PNG")


class TestEndToEnd:
    """Testes end-to-end do fluxo completo."""

    def test_full_flow_polygon(self):
        """Testa fluxo completo: criar -> config -> preview para polígono."""
        # 1. Criar simbologia
        create_response = client.post(
            "/api/symbology",
            json={
                "symbology_geometry_type": "POLYGON",
                "symbology_fill_color": "#2ecc71",
                "symbology_fill_style": "SOLID",
                "symbology_fill_density": 0,
                "symbology_stroke_color": "#27ae60",
                "symbology_stroke_style": "SOLID",
                "symbology_stroke_line": 1.5,
            },
        )
        assert create_response.status_code == 200
        url_key = create_response.json()["url_key"]

        # 2. Obter configurações
        config_response = client.get(f"/api/result/{url_key}/json")
        assert config_response.status_code == 200
        config_data = config_response.json()
        assert config_data["url_key"] == url_key

        # 3. Obter preview
        preview_response = client.get(f"/api/result/{url_key}/png")
        assert preview_response.status_code == 200
        assert preview_response.content.startswith(b"\x89PNG")

    def test_full_flow_with_hatch(self):
        """Testa fluxo completo com padrão hatch."""
        # 1. Criar simbologia com hatch
        create_response = client.post(
            "/api/symbology",
            json={
                "symbology_geometry_type": "POLYGON",
                "symbology_fill_color": "#e74c3c",
                "symbology_fill_style": "SLASH",
                "symbology_fill_density": 3,
                "symbology_stroke_color": "#c0392b",
                "symbology_stroke_style": "DASHED",
                "symbology_stroke_line": 2.0,
            },
        )
        assert create_response.status_code == 200
        url_key = create_response.json()["url_key"]

        # 2. Obter configurações
        config_response = client.get(f"/api/result/{url_key}/json")
        assert config_response.status_code == 200

        # Verifica que hatch foi incluído nas kwargs
        config_data = config_response.json()
        assert "hatch" in config_data["matplotlib"] or config_data["matplotlib"]["fill"]

        # 3. Obter preview
        preview_response = client.get(f"/api/result/{url_key}/png")
        assert preview_response.status_code == 200


class TestUrlKeyPersistence:
    """Testa que url_key é determinístico e persistente."""

    def test_same_symbology_same_url_key(self):
        """Testa que a mesma simbologia gera a mesma url_key."""
        data = {
            "symbology_geometry_type": "POLYGON",
            "symbology_fill_color": "#ff0000",
            "symbology_fill_style": "SOLID",
            "symbology_fill_density": 5,
            "symbology_stroke_color": "#0000ff",
            "symbology_stroke_style": "DASHED",
            "symbology_stroke_line": 2.345,
        }

        response1 = client.post("/api/symbology", json=data)
        response2 = client.post("/api/symbology", json=data)

        assert response1.status_code == 200
        assert response2.status_code == 200

        url_key1 = response1.json()["url_key"]
        url_key2 = response2.json()["url_key"]

        assert url_key1 == url_key2

    def test_different_symbology_different_url_key(self):
        """Testa que simbologias diferentes geram url_keys diferentes."""
        data1 = {
            "symbology_geometry_type": "POLYGON",
            "symbology_fill_color": "#ff0000",
            "symbology_fill_style": "SOLID",
            "symbology_fill_density": 0,
            "symbology_stroke_color": "#0000ff",
            "symbology_stroke_style": "SOLID",
            "symbology_stroke_line": 1.0,
        }

        data2 = {
            "symbology_geometry_type": "POLYGON",
            "symbology_fill_color": "#00ff00",  # Cor diferente
            "symbology_fill_style": "SOLID",
            "symbology_fill_density": 0,
            "symbology_stroke_color": "#0000ff",
            "symbology_stroke_style": "SOLID",
            "symbology_stroke_line": 1.0,
        }

        response1 = client.post("/api/symbology", json=data1)
        response2 = client.post("/api/symbology", json=data2)

        url_key1 = response1.json()["url_key"]
        url_key2 = response2.json()["url_key"]

        assert url_key1 != url_key2


class TestOpenAPIDocumentation:
    """Testa que a documentação OpenAPI está disponível."""

    def test_openapi_schema(self):
        """Testa GET /openapi.json."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_swagger_ui(self):
        """Testa GET /docs."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text

    def test_redoc(self):
        """Testa GET /redoc."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text
