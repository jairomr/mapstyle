"""
Serviço de geração de preview PNG para simbologias.

Converte representações Symbology em imagens PNG usando matplotlib.
"""

from io import BytesIO
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.lines import Line2D
from pydantic_extra_types.color import Color

from scr.core.model.symbology import Symbology, SymbologyGeometryType


def _clean_kwargs(kwargs: dict) -> dict:
    """
    Limpa kwargs para matplotlib, convertendo cores RGB para hex.

    Matplotlib não suporta formato 'rgb(r,g,b)', então convertemos para hex.
    """
    cleaned = kwargs.copy()

    for color_key in ["facecolor", "edgecolor", "color"]:
        if color_key in cleaned and isinstance(cleaned[color_key], str):
            color_str = cleaned[color_key]
            # Se é rgb(...), converte para hex
            if color_str.startswith("rgb("):
                try:
                    color = Color(color_str)
                    cleaned[color_key] = color.as_hex()
                except:
                    # Se falhar, deixa como está
                    pass

    return cleaned


def generate_preview(symbology: Symbology, size: int = 200) -> bytes:
    """
    Gera preview PNG da simbologia.

    Renderiza a simbologia como uma imagem:
    - POLYGON: Retângulo com preenchimento e borda
    - LINE: Linha diagonal com estilo
    - POINT: Círculo com preenchimento e borda

    Args:
        symbology: Objeto Symbology a renderizar
        size: Tamanho da imagem em pixels (quadrada)

    Returns:
        bytes: Dados PNG em bytes
    """

    # Cria figura sem margins
    fig, ax = plt.subplots(figsize=(size / 100, size / 100), dpi=100)
    fig.patch.set_facecolor("white")

    # Obtém configurações matplotlib
    kwargs = symbology.to_matplotlib_patch_kwargs()

    try:
        if symbology.symbology_geometry_type == SymbologyGeometryType.POLYGON:
            _render_polygon(ax, kwargs)

        elif symbology.symbology_geometry_type == SymbologyGeometryType.LINE:
            _render_line(ax, kwargs)

        elif symbology.symbology_geometry_type == SymbologyGeometryType.POINT:
            _render_point(ax, kwargs)

        # Limpa eixos
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
        fig.tight_layout(pad=0)

        # Salva em bytes
        buffer = BytesIO()
        fig.savefig(buffer, format="png", dpi=100, bbox_inches="tight", pad_inches=0)
        buffer.seek(0)
        return buffer.getvalue()

    finally:
        plt.close(fig)


def _render_polygon(ax, kwargs: dict) -> None:
    """Renderiza polígono (retângulo) na figura."""
    # Limpa cores em formato rgb() que matplotlib não suporta
    polygon_kwargs = _clean_kwargs(kwargs)

    # Se edgecolor é 'none', remove o parâmetro para matplotlib não desenhar borda
    if polygon_kwargs.get('edgecolor') == 'none':
        polygon_kwargs.pop('edgecolor', None)
        polygon_kwargs['linewidth'] = 0

    rect = Rectangle((0.2, 0.2), 0.6, 0.6, **polygon_kwargs)
    ax.add_patch(rect)


def _render_line(ax, kwargs: dict) -> None:
    """Renderiza linha na figura."""
    # Remove parâmetros que não funcionam com Line2D
    line_kwargs = _clean_kwargs(kwargs)
    for key in ["fill", "facecolor", "hatch", "radius"]:
        line_kwargs.pop(key, None)

    # Usa edgecolor e linestyle de forma correta
    if "edgecolor" in line_kwargs:
        color = line_kwargs.pop("edgecolor")
        # Só desenha linha se color não é 'none'
        if color != 'none':
            line_kwargs["color"] = color
        else:
            # Sem linha, apenas retorna sem desenhar
            return

    line = Line2D([0.1, 0.9], [0.5, 0.5], **line_kwargs)
    ax.add_line(line)


def _render_point(ax, kwargs: dict) -> None:
    """Renderiza ponto (círculo) na figura."""
    # Para pontos, usa radius se disponível, senão extrai do linewidth
    circle_kwargs = _clean_kwargs(kwargs)

    if "radius" in circle_kwargs:
        radius = circle_kwargs.pop("radius")
    else:
        radius = max(0.05, circle_kwargs.get("linewidth", 1.0) / 20)

    # Remove parâmetros que não funcionam com Circle
    for key in ["radius", "linestyle", "hatch"]:
        circle_kwargs.pop(key, None)

    # Se edgecolor é 'none', remove o parâmetro para matplotlib não desenhar borda
    if circle_kwargs.get('edgecolor') == 'none':
        circle_kwargs.pop('edgecolor', None)
        circle_kwargs['linewidth'] = 0

    circle = Circle((0.5, 0.5), radius, **circle_kwargs)
    ax.add_patch(circle)
