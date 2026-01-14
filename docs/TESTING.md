# Guia de Testes - MapTemaMapBiomas

## Visão Geral

O projeto utiliza **pytest** com **pytest-cov** para teste e cobertura de código.

- **Total de testes:** 48
- **Cobertura:** 92.02%
- **Tempo de execução:** ~0.3s

## Instalação

Se ainda não instalou as dependências de teste:

```bash
uv sync --all-extras
```

## Executando Testes

### Básico - Executar todos os testes

```bash
pytest
```

### Verboso - Mostrar detalhes de cada teste

```bash
pytest -v
```

### Com cobertura em terminal

```bash
pytest --cov=scr --cov-report=term-missing
```

Mostra quais linhas não foram cobertas.

### Com relatório HTML

```bash
pytest --cov=scr --cov-report=html
```

Gera relatório em `htmlcov/index.html`. Abra no navegador:

```bash
# Linux/Mac
open htmlcov/index.html

# Ou com python
python -m http.server -d htmlcov 8000
# Então acesse: http://localhost:8000
```

### Execução paralela (mais rápido)

```bash
pytest -n auto
```

Executa testes em paralelo usando todos os cores disponíveis.

### Executar classe de teste específica

```bash
pytest tests/test_symbology.py::TestSymbologyCreation -v
```

### Executar teste específico

```bash
pytest tests/test_symbology.py::TestSymbologyCreation::test_symbology_creation_valid -v
```

### Parar no primeiro erro

```bash
pytest -x
```

### Modo watch (rerun ao salvar arquivo)

```bash
pytest --looponfail
```

## Estrutura dos Testes

Testes organizados por funcionalidade em `tests/test_symbology.py`:

### Classes de Teste

| Classe | Testes | Funcionalidade |
|--------|--------|---|
| `TestLineStyle` | 5 | Estilos de linha e enumerações |
| `TestSymbologyGeometryType` | 1 | Tipos de geometria |
| `TestSymbologyFill` | 2 | Padrões de preenchimento |
| `TestSymbologyCreation` | 5 | Criação e validação |
| `TestSymbologyCacheKey` | 3 | Geração de cache keys |
| `TestSymbologyHash` | 3 | Hash e uso em coleções |
| `TestSymbologyBinarySerialization` | 5 | Pack/unpack binário |
| `TestSymbologyBase62Encoding` | 2 | Codificação Base62 |
| `TestSymbologyURLKey` | 5 | Serialização URL-safe |
| `TestSymbologyMatplotlib` | 5 | Kwargs para matplotlib |
| `TestSymbologyGeoServerSLD` | 5 | Geração de SLD XML |
| `TestSymbologyGeoServerCSS` | 5 | Geração de CSS |
| `TestSymbologyGeoServerRESTPayload` | 2 | Payload REST API |

**Total: 48 testes**

## Cobertura

### Relatório por arquivo

```
scr/core/model/symbology.py
├── Linhas: 294 (92.02% cobertas)
├── Branches: 82 (78.05% cobertas)
└── Linhas não cobertas: 12
```

### Aumentar cobertura

Linhas não cobertas estão principalmente em:
- Tratamento de erro em edge cases
- Branches pouco comuns em métodos de conversão
- Validações que dependem de entrada específica

Para aumentar cobertura, adicione testes para:

```python
# Exemplo: Test linha 371
def test_matplotlib_line_with_none_stroke():
    # Teste para LineStyle.NONE
    pass

# Exemplo: Test linha 404
def test_invalid_geometry_type():
    # Teste com tipo de geometria inválido
    pass
```

## Configuração (pyproject.toml)

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-v --cov=scr --cov-report=html --cov-report=term-missing --tb=short"
testpaths = ["tests"]
pythonpath = ["."]

[tool.coverage.run]
branch = true
source = ["scr"]
omit = ["*/tests/*", "*/__main__.py"]
```

## Boas Práticas

### Nomes descritivos

```python
# ✅ Bom
def test_symbology_creation_with_valid_parameters(self):
    """Testa criação com parâmetros válidos."""

# ❌ Ruim
def test_create(self):
    pass
```

### Usar fixtures

```python
# ✅ Bom
@pytest.fixture
def valid_symbology(self):
    return Symbology(...)

def test_something(self, valid_symbology):
    assert valid_symbology is not None
```

### Organizar em classes

```python
# ✅ Bom - Testes agrupados por funcionalidade
class TestSymbologyCreation:
    def test_valid_creation(self):
        pass

    def test_invalid_parameters(self):
        pass
```

### Testar casos positivos e negativos

```python
# ✅ Bom - Cobre ambos os casos
def test_symbology_fill_density_valid(self):
    # Caso positivo: densidade válida
    symbology = Symbology(..., symbology_fill_density=5)
    assert symbology.symbology_fill_density == 5

def test_symbology_fill_density_invalid(self):
    # Caso negativo: densidade inválida
    with pytest.raises(Exception):
        Symbology(..., symbology_fill_density=11)
```

## Debugging de Testes

### Adicionar prints/logging

```python
def test_something(self):
    symbology = Symbology(...)
    print(f"Cache key: {symbology.cache_key()}")  # print normal
    logger.debug(f"State: {symbology}")  # usando loguru
```

### Usar pdb

```python
def test_something(self):
    import pdb; pdb.set_trace()  # Para aqui para debug
    symbology = Symbology(...)
```

### Executar com output

```bash
pytest -s  # Mostra prints
pytest -vv  # Muito verboso
```

## CI/CD

Para integração contínua, use:

```bash
# Executar testes + gerar cobertura
pytest --cov=scr --cov-report=term-missing --cov-report=html

# Falhar se cobertura < 85%
pytest --cov=scr --cov-fail-under=85
```

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'scr'"

Solução:
```bash
uv sync
# Ou manual:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Testes lentos

Use paralelização:
```bash
pytest -n auto
```

### Cache de pytest

Limpe o cache:
```bash
pytest --cache-clear
```

## Recursos

- [Documentação pytest](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
