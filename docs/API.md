# API FastAPI - MapTema MapBiomas

## Visão Geral

API REST para criar, consultar e exportar simbologias geoespaciais. Oferece endpoints para:

- Criar e serializar simbologias em chaves URL-safe compactas (17 caracteres)
- Obter configurações em múltiplos formatos (matplotlib, GeoServer)
- Gerar previews PNG das simbologias

**Base URL**: `http://localhost:8000`

**Documentação interativa**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Começar

### Iniciar servidor

```bash
# Com recarregamento automático
uvicorn scr.api.main:app --reload --port 8000

# Produção
uvicorn scr.api.main:app --host 0.0.0.0 --port 8000
```

### Health Check

```bash
curl http://localhost:8000/health
```

Resposta:
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Endpoints

### 1. POST /api/symbology - Criar Simbologia

Cria uma nova simbologia e retorna chave compacta para acessá-la.

**Request**:

```bash
curl -X POST "http://localhost:8000/api/symbology" \
  -H "Content-Type: application/json" \
  -d '{
    "symbology_geometry_type": "POLYGON",
    "symbology_fill_color": "#ff0000",
    "symbology_fill_style": "SOLID",
    "symbology_fill_density": 0,
    "symbology_stroke_color": "#0000ff",
    "symbology_stroke_style": "DASHED",
    "symbology_stroke_line": 2.0
  }'
```

**Body Parameters**:

| Campo | Tipo | Descrição | Valores |
|-------|------|-----------|---------|
| `symbology_geometry_type` | string | Tipo de geometria | `POLYGON`, `LINE`, `POINT` |
| `symbology_fill_color` | string | Cor do preenchimento (hex ou RGB) | ex: `#ff0000`, `rgb(255,0,0)` |
| `symbology_fill_style` | string | Estilo de preenchimento | `SOLID`, `NOBRUSH`, `SLASH`, `BACKSLASH`, `PIPE`, `DASH`, `PLUS`, `X`, `O_LOWER`, `O_UPPER`, `DOT`, `STAR` |
| `symbology_fill_density` | integer | Densidade do hatch (0-10) | `0` a `10` |
| `symbology_stroke_color` | string | Cor da borda/linha | hex ou RGB |
| `symbology_stroke_style` | string | Estilo da linha | `SOLID`, `DASHED`, `DOTTED`, `DASH_DOT`, `LONG_DASH`, `SHORT_DASH`, `DASH_DOT_DOT`, `DASH_DOT_DOT_DOT`, `SPARSE_DOT`, `DENSE_DOT`, `NONE` |
| `symbology_stroke_line` | number | Espessura da linha (pixels) | `0.0` a `50.0` |

**Response** (200 OK):

```json
{
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
    "symbology_stroke_line": 2.0
  }
}
```

**URL Key**: Chave de 17 caracteres que codifica toda a simbologia em formato URL-safe. Pode ser usada para recuperar a simbologia depois sem necessidade de persistência.

---

### 2. GET /api/result/{url_key}/json - Obter Configurações

Retorna configurações completas da simbologia em múltiplos formatos.

**Request**:

```bash
curl "http://localhost:8000/api/result/00A1B2C3D4E5F6G7H/json"
```

**Path Parameters**:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `url_key` | string | Chave de 17 caracteres retornada por POST /api/symbology |

**Response** (200 OK):

```json
{
  "url_key": "00A1B2C3D4E5F6G7H",
  "matplotlib": {
    "fill": true,
    "facecolor": "rgb(255, 0, 0)",
    "edgecolor": "rgb(0, 0, 255)",
    "linewidth": 2.0,
    "linestyle": "--"
  },
  "geoserver": {
    "sld": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<sld:StyledLayerDescriptor...",
    "css": "* {\n  fill: #ff0000;\n  stroke: #0000ff;\n  stroke-width: 2.0;\n}",
    "rest_payload": {
      "style": {
        "name": "generated_style",
        "filename": "generated_style.sld",
        "body": "<?xml version=\"1.0\"...",
      }
    }
  },
  "symbology": {
    "symbology_geometry_type": "POLYGON",
    "symbology_fill_color": "rgb(255, 0, 0)",
    ...
  }
}
```

**Conteúdo da Resposta**:

- **matplotlib**: Kwargs para usar com `matplotlib.patches`
- **geoserver**: Configurações para GeoServer
  - `sld`: XML Styled Layer Descriptor
  - `css`: CSS para styling no GeoServer
  - `rest_payload`: Payload para API REST do GeoServer
- **symbology**: Simbologia completa serializada

---

### 3. GET /api/result/{url_key}/png - Obter Preview

Retorna imagem PNG da simbologia para visualização.

**Request**:

```bash
# Tamanho padrão (200x200px)
curl "http://localhost:8000/api/result/00A1B2C3D4E5F6G7H/png" -o preview.png

# Tamanho customizado
curl "http://localhost:8000/api/result/00A1B2C3D4E5F6G7H/png?size=400" -o preview.png
```

**Path Parameters**:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `url_key` | string | Chave de 17 caracteres |

**Query Parameters**:

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `size` | integer | 200 | Tamanho da imagem em pixels (50-1000) |

**Response** (200 OK):

- Content-Type: `image/png`
- Body: PNG image binary
- Cache-Control: `public, max-age=86400` (cache 24 horas)

---

## Exemplos de Uso

### Exemplo 1: Polígono com preenchimento sólido

```bash
# 1. Criar
curl -X POST "http://localhost:8000/api/symbology" \
  -H "Content-Type: application/json" \
  -d '{
    "symbology_geometry_type": "POLYGON",
    "symbology_fill_color": "#2ecc71",
    "symbology_fill_style": "SOLID",
    "symbology_fill_density": 0,
    "symbology_stroke_color": "#27ae60",
    "symbology_stroke_style": "SOLID",
    "symbology_stroke_line": 1.5
  }' | jq .url_key

# Output: "1a2B3c4D5e6F7g8H9"

# 2. Obter configurações
curl "http://localhost:8000/api/result/1a2B3c4D5e6F7g8H9/json"

# 3. Obter preview
curl "http://localhost:8000/api/result/1a2B3c4D5e6F7g8H9/png" -o preview.png
```

### Exemplo 2: Polígono com padrão hatch

```bash
curl -X POST "http://localhost:8000/api/symbology" \
  -H "Content-Type: application/json" \
  -d '{
    "symbology_geometry_type": "POLYGON",
    "symbology_fill_color": "#e74c3c",
    "symbology_fill_style": "SLASH",
    "symbology_fill_density": 3,
    "symbology_stroke_color": "#c0392b",
    "symbology_stroke_style": "DASHED",
    "symbology_stroke_line": 2.0
  }'
```

### Exemplo 3: Linha com estilo pontilhado

```bash
curl -X POST "http://localhost:8000/api/symbology" \
  -H "Content-Type: application/json" \
  -d '{
    "symbology_geometry_type": "LINE",
    "symbology_fill_color": "#3498db",
    "symbology_fill_style": "SOLID",
    "symbology_fill_density": 0,
    "symbology_stroke_color": "#2980b9",
    "symbology_stroke_style": "DOTTED",
    "symbology_stroke_line": 1.5
  }'
```

### Exemplo 4: Ponto/Círculo

```bash
curl -X POST "http://localhost:8000/api/symbology" \
  -H "Content-Type: application/json" \
  -d '{
    "symbology_geometry_type": "POINT",
    "symbology_fill_color": "#f39c12",
    "symbology_fill_style": "SOLID",
    "symbology_fill_density": 0,
    "symbology_stroke_color": "#d68910",
    "symbology_stroke_style": "SOLID",
    "symbology_stroke_line": 2.0
  }'
```

---

## Códigos de Erro

| Status | Descrição |
|--------|-----------|
| `200` | Sucesso |
| `400` | Bad Request - Parâmetros inválidos |
| `422` | Unprocessable Entity - Validação Pydantic falhou |
| `500` | Internal Server Error |

### Exemplo de erro 400:

```bash
curl "http://localhost:8000/api/result/invalid_key/json"
```

Resposta:
```json
{
  "detail": "Invalid url_key format: url_key deve ter 17 caracteres, recebidos 11"
}
```

---

## Características

### URL Key Determinístico

A mesma simbologia sempre gera a mesma `url_key`:

```bash
# Requisição 1
curl -X POST "http://localhost:8000/api/symbology" \
  -d '{"symbology_geometry_type":"POLYGON",...}' \
  | jq .url_key
# Output: "1a2B3c4D5e6F7g8H9"

# Requisição 2 (mesmos dados)
curl -X POST "http://localhost:8000/api/symbology" \
  -d '{"symbology_geometry_type":"POLYGON",...}' \
  | jq .url_key
# Output: "1a2B3c4D5e6F7g8H9"  (IGUAL!)
```

### Sem Persistência Requerida

A URL Key codifica todo o estado. Não requer banco de dados ou cache:

- 13 bytes de dados binários
- Codificado em Base62 (17 caracteres)
- Pode ser recuperado em qualquer momento

### Cache-friendly

As respostas são cacheavéis:

```bash
# Preview PNG tem Cache-Control de 24h
curl -I "http://localhost:8000/api/result/1a2B3c4D5e6F7g8H9/png"
# Cache-Control: public, max-age=86400
```

---

## Integração com Matplotlib

Use as configurações retornadas por `/api/result/{url_key}/json`:

```python
import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Obter configurações
response = requests.get("http://localhost:8000/api/result/1a2B3c4D5e6F7g8H9/json")
matplotlib_config = response.json()["matplotlib"]

# Criar figura
fig, ax = plt.subplots()
rect = Rectangle((0, 0), 1, 1, **matplotlib_config)
ax.add_patch(rect)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.show()
```

---

## Integração com GeoServer

Use o payload REST para criar estilo no GeoServer:

```python
import requests

# Obter configurações
response = requests.get("http://localhost:8000/api/result/1a2B3c4D5e6F7g8H9/json")
rest_payload = response.json()["geoserver"]["rest_payload"]

# Criar estilo no GeoServer
gs_response = requests.post(
    "http://geoserver:8080/geoserver/rest/styles",
    json=rest_payload,
    auth=("admin", "geoserver")
)
```

---

## Testes

Rodar testes de API:

```bash
pytest tests/test_api.py -v

# Com cobertura
pytest tests/test_api.py -v --cov=scr.api
```

---

## Performance

- Criação de simbologia: < 10ms
- Obtenção de config JSON: < 15ms
- Geração de preview PNG (200x200): ~50-100ms
- Geração de preview PNG (400x400): ~100-150ms

Cache HTTP é recomendado para previews PNG já que são determinísticos.

---

## Limitações

- Sem persistência de histórico (use `url_key` para armazenar estados)
- Preview sempre gerado on-demand (considere cache de proxy/CDN)
- Tamanho máximo de preview: 1000x1000 pixels

---

## Melhorias Futuras

- Cache em memória (LRU) para previews PNG
- Batch endpoint para processar múltiplas simbologias
- WebSocket para atualizações em tempo real
- SVG e PDF previews
- Rate limiting
- Autenticação/Autorização
