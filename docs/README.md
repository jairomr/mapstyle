# MapTemaMapBiomas - Documentação

## Visão Geral

**MapTemaMapBiomas** é um projeto Python para representação e serialização de simbologia geoespacial. O módulo fornece classes para definir e converter estilos de símbolos geoespaciais (polígonos, linhas, pontos) em múltiplos formatos, com suporte a cache, codificação URL-safe e integração com Matplotlib e Geoserver.

## Estrutura do Projeto

```
mapTemaMapBiomas/
├── scr/
│   └── core/
│       └── model/
│           └── symbology.py       # Módulo principal de simbologia
├── tests/
│   ├── __init__.py
│   └── test_symbology.py          # Suite completa de testes
├── docs/
│   └── README.md                  # Esta documentação
├── main.py                        # Script de exemplo
├── pyproject.toml                 # Configuração do projeto e pytest
└── uv.lock                        # Lock file de dependências
```

## Instalação e Setup

### Dependências

- **Python**: >= 3.13
- **Principais**:
  - `loguru>=0.7.3` - Logging estruturado
  - `pydantic>=2.12.5` - Validação de dados
  - `pydantic-extra-types>=2.11.0` - Tipos extras (Color, etc)

- **Desenvolvimento** (opcional):
  - `pytest>=7.4.0` - Framework de testes
  - `pytest-cov>=4.1.0` - Cobertura de testes
  - `pytest-xdist>=3.3.1` - Execução paralela de testes

### Instalação com uv

```bash
# Clonar repositório
git clone <url_do_repositorio>
cd mapTemaMapBiomas

# Instalar dependências (incluindo dev)
uv sync --all-extras

# Ou apenas dependências principais
uv sync
```

## Uso

### Importação Básica

```python
from scr.core.model.symbology import (
    Symbology,
    SymbologyGeometryType,
    SymbologyFill,
    LineStyle,
)
from pydantic_extra_types.color import Color

# Criar uma simbologia para polígono
symbology = Symbology(
    symbology_geometry_type=SymbologyGeometryType.POLYGON,
    symbology_fill_color=Color("#ff0000"),
    symbology_fill_style=SymbologyFill.SOLID,
    symbology_fill_density=5,
    symbology_stroke_color=Color("#0000ff"),
    symbology_stroke_style=LineStyle.DASHED,
    symbology_stroke_line=2.5,
)
```

### Tipos de Geometria

```python
# Três tipos de geometria suportados
SymbologyGeometryType.POLYGON  # Polígonos
SymbologyGeometryType.LINE     # Linhas
SymbologyGeometryType.POINT    # Pontos
```

### Estilos de Preenchimento

- `SOLID` - Preenchimento sólido
- `NOBRUSH` - Sem preenchimento
- `SLASH` - Padrão de barras inclinadas (/)
- `BACKSLASH` - Padrão de barras invertidas (\)
- `PIPE` - Padrão vertical (|)
- `DASH` - Padrão horizontal (-)
- `PLUS` - Padrão de cruz (+)
- `X` - Padrão X
- `O_LOWER` - Padrão de círculos (o)
- `O_UPPER` - Padrão de círculos (O)
- `DOT` - Padrão de pontos (.)
- `STAR` - Padrão de estrelas (*)

### Estilos de Linha

- `SOLID` - Linha contínua (padrão)
- `DASHED` - Linha tracejada
- `DOTTED` - Linha pontilhada
- `DASH_DOT` - Padrão traço-ponto
- `LONG_DASH` - Traços longos
- `SHORT_DASH` - Traços curtos
- `DASH_DOT_DOT` - Padrão traço-ponto-ponto
- `DASH_DOT_DOT_DOT` - Padrão traço-três pontos
- `SPARSE_DOT` - Pontos espaçados
- `DENSE_DOT` - Pontos densos
- `NONE` - Sem linha/borda

## Funcionalidades Principais

### 1. Serialização Binária Compacta (13 bytes)

Empacota toda a simbologia em formato binário otimizado:

```python
symbology = Symbology(...)
binary_data = symbology._pack_binary()  # Retorna 13 bytes
recovered = Symbology._unpack_binary(binary_data)
```

**Formato binário:**
- Tipo geometria: 1 byte (código 0-2)
- Cor preenchimento: 3 bytes (RGB)
- Estilo preenchimento: 1 byte (código 0-11)
- Densidade: 1 byte (0-10)
- Cor linha: 3 bytes (RGB)
- Estilo linha: 1 byte (código 0-10)
- Espessura linha: 2 bytes (uint16, milésimos de pixel)
- Reservado: 1 byte (para futuras expansões)

### 2. Codificação URL-Safe (17 caracteres)

Serializa a simbologia em uma string compacta e URL-safe usando Base62:

```python
symbology = Symbology(...)
url_key = symbology.url_key()  # String de 17 caracteres
recovered = Symbology.from_url_key(url_key)
```

**Exemplo de url_key:**
```
000FFA2A00B00000
```

### 3. Cache e Hash

Objetos Symbology são imutáveis e hashables, permitindo uso em sets e dicts:

```python
symbology1 = Symbology(...)
symbology2 = Symbology(...)

# Cache key (tupla)
key = symbology1.cache_key()

# Hash
h = hash(symbology1)

# Uso em sets
symbols = {symbology1, symbology2}

# Uso em dicts
cache = {symbology1: "cached_data"}
```

### 4. Matplotlib

Gera kwargs compatíveis com `matplotlib.patches`:

```python
symbology = Symbology(...)
kwargs = symbology.to_matplotlib_patch_kwargs()

# Uso com matplotlib
from matplotlib.patches import Polygon
poly = Polygon(coords, **kwargs)
```

**Retorna kwargs como:**
- `fill`, `facecolor`, `hatch` - Preenchimento
- `edgecolor`, `linewidth`, `linestyle` - Borda/linha
- `radius` - Para pontos

### 5. GeoServer SLD (Styled Layer Descriptor)

Gera XML SLD válido para estilização no GeoServer:

```python
symbology = Symbology(...)
sld_xml = symbology.to_geoserver_sld("nome_da_camada")
```

**Exemplo de SLD gerado:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor version="1.0.0" ...>
  <sld:NamedLayer>
    <sld:Name>layer_name</sld:Name>
    <sld:UserStyle>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#ff0000</sld:CssParameter>
            </sld:Fill>
            ...
          </sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
```

### 6. GeoServer CSS

Gera CSS para estilização no GeoServer:

```python
symbology = Symbology(...)
css = symbology.to_geoserver_css()
```

**Exemplo de CSS gerado:**
```css
* {
  fill: #ff0000;
  fill-opacity: 1;
  stroke: #0000ff;
  stroke-width: 2.5;
  stroke-dasharray: 5 5;
}
```

### 7. GeoServer REST API Payload

Gera payload compatível com a API REST do GeoServer:

```python
symbology = Symbology(...)
payload = symbology.to_geoserver_rest_payload()

# Payload contém:
# {
#   "style": {
#     "name": "generated_style",
#     "filename": "generated_style.sld",
#     "body": "<sld>...</sld>"
#   }
# }
```

## Validações

O módulo valida automaticamente:

- **Densidade de preenchimento**: 0-10 (inclusive)
- **Espessura de linha**: 0.0-50.0 pixels (inclusive)
- **Espessura normalizada**: Arredondada para 3 casas decimais
- **Cores**: Aceita hex, RGB, nomes de cores (via pydantic Color)
- **Imutabilidade**: Objetos são congelados (frozen=True)

## Testes

O projeto inclui uma suite completa de testes com pytest.

### Executar Testes

```bash
# Executar todos os testes
pytest

# Com saída verbosa
pytest -v

# Com cobertura
pytest --cov=scr --cov-report=html

# Testes específicos
pytest tests/test_symbology.py::TestSymbologyCreation -v

# Execução paralela (mais rápido)
pytest -n auto
```

### Cobertura de Testes

Configurado em `pyproject.toml` para gerar:
- Relatório de terminal com linhas não cobertas
- Relatório HTML em `htmlcov/index.html`
- Rastreamento de branches

```bash
# Ver cobertura em terminal
pytest --cov=scr --cov-report=term-missing

# Gerar relatório HTML
pytest --cov=scr --cov-report=html
# Abrir em navegador: htmlcov/index.html
```

### Estrutura de Testes

Testes organizados por funcionalidade:

- `TestLineStyle` - Enumeração de estilos de linha
- `TestSymbologyGeometryType` - Tipos de geometria
- `TestSymbologyFill` - Padrões de preenchimento
- `TestSymbologyCreation` - Criação e validação
- `TestSymbologyCacheKey` - Geração de cache keys
- `TestSymbologyHash` - Hash e uso em coleções
- `TestSymbologyBinarySerialization` - Empacotamento binário
- `TestSymbologyBase62Encoding` - Codificação Base62
- `TestSymbologyURLKey` - Serialização URL-safe
- `TestSymbologyMatplotlib` - Geração de kwargs matplotlib
- `TestSymbologyGeoServerSLD` - Geração de SLD XML
- `TestSymbologyGeoServerCSS` - Geração de CSS
- `TestSymbologyGeoServerRESTPayload` - Payload REST

### Cobertura Alcançada

A suite de testes cobre:
- ✅ Todas as enumerações
- ✅ Validação de entrada
- ✅ Serialização binária (pack/unpack)
- ✅ Codificação Base62
- ✅ Round-trip URL-key
- ✅ Geração de matplotlib kwargs
- ✅ Geração de SLD válido
- ✅ Geração de CSS válido
- ✅ REST API payload
- ✅ Hash e cache_key
- ✅ Casos de erro e exceções

## Exemplo Completo

```python
from scr.core.model.symbology import (
    Symbology,
    SymbologyGeometryType,
    SymbologyFill,
    LineStyle,
)
from pydantic_extra_types.color import Color

# Criar simbologia para um mapa temático
theme_color = Symbology(
    symbology_geometry_type=SymbologyGeometryType.POLYGON,
    symbology_fill_color=Color("#2ecc71"),
    symbology_fill_style=SymbologyFill.SOLID,
    symbology_fill_density=0,
    symbology_stroke_color=Color("#27ae60"),
    symbology_stroke_style=LineStyle.SOLID,
    symbology_stroke_line=1.5,
)

# Gerar chave URL-safe para armazenar em banco de dados
url_key = theme_color.url_key()
print(f"Chave compacta: {url_key}")

# Recuperar simbologia depois
recovered = Symbology.from_url_key(url_key)

# Gerar estilos para diferentes plataformas
matplotlib_kwargs = recovered.to_matplotlib_patch_kwargs()
sld_xml = recovered.to_geoserver_sld("biomas")
geoserver_css = recovered.to_geoserver_css()
rest_payload = recovered.to_geoserver_rest_payload()

# Usar em cache (é hashable)
cache = {recovered: "metadata_associada"}
```

## Configuração (pyproject.toml)

O projeto usa `uv` como package manager. Configurações importantes:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.3.1",
]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-v --cov=scr --cov-report=html --cov-report=term-missing --tb=short"
testpaths = ["tests"]
```

## Roadmap

Possíveis extensões futuras:

- [ ] Suporte a mais estilos de linha
- [ ] Integração com Leaflet/OpenLayers
- [ ] Cache em memória com LRU
- [ ] Persistência em banco de dados
- [ ] API REST para geração de simbologias
- [ ] Interface web para criar/editar simbologias

## Licença

Especificar licença aqui

## Contribuindo

Para contribuir ao projeto:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Execute os testes (`pytest`)
5. Verifique cobertura (`pytest --cov`)
6. Push para a branch (`git push origin feature/AmazingFeature`)
7. Abra um Pull Request

## Autores

Desenvolvido como parte do projeto MapTemaMapBiomas
