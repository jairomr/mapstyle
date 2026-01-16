/**
 * Enumerações e constantes da API
 */

export const GEOMETRY_TYPES = {
  POLYGON: { label: 'Polígono', value: 'POLYGON' },
  LINE: { label: 'Linha', value: 'LINE' },
  POINT: { label: 'Ponto', value: 'POINT' },
} as const;

export const FILL_STYLES = {
  SOLID: { label: 'Sólido', value: 'SOLID' },
  NOBRUSH: { label: 'Sem preenchimento', value: 'NOBRUSH' },
  SLASH: { label: 'Barras /', value: 'SLASH' },
  BACKSLASH: { label: 'Barras \\', value: 'BACKSLASH' },
  PIPE: { label: 'Linhas verticais', value: 'PIPE' },
  DASH: { label: 'Traços', value: 'DASH' },
  PLUS: { label: 'Mais (+)', value: 'PLUS' },
  X: { label: 'Xis (X)', value: 'X' },
  O_LOWER: { label: 'Círculos pequenos', value: 'O_LOWER' },
  O_UPPER: { label: 'Círculos grandes', value: 'O_UPPER' },
  DOT: { label: 'Pontos', value: 'DOT' },
  STAR: { label: 'Estrelas', value: 'STAR' },
} as const;

export const LINE_STYLES = {
  SOLID: { label: 'Sólido', value: 'SOLID' },
  DASHED: { label: 'Tracejado', value: 'DASHED' },
  DOTTED: { label: 'Pontilhado', value: 'DOTTED' },
  DASH_DOT: { label: 'Traço-ponto', value: 'DASH_DOT' },
  LONG_DASH: { label: 'Traço longo', value: 'LONG_DASH' },
  SHORT_DASH: { label: 'Traço curto', value: 'SHORT_DASH' },
  DASH_DOT_DOT: { label: 'Traço-ponto-ponto', value: 'DASH_DOT_DOT' },
  DASH_DOT_DOT_DOT: { label: 'Traço-ponto-ponto-ponto', value: 'DASH_DOT_DOT_DOT' },
  SPARSE_DOT: { label: 'Pontos espaçados', value: 'SPARSE_DOT' },
  DENSE_DOT: { label: 'Pontos densos', value: 'DENSE_DOT' },
  NONE: { label: 'Nenhum', value: 'NONE' },
} as const;

export const MARKER_TYPES = {
  CIRCLE: { label: '● Círculo', value: 'CIRCLE' },
  SQUARE: { label: '■ Quadrado', value: 'SQUARE' },
  TRIANGLE: { label: '▲ Triângulo', value: 'TRIANGLE' },
  STAR: { label: '★ Estrela', value: 'STAR' },
  CROSS: { label: '+ Cruz', value: 'CROSS' },
  DIAMOND: { label: '◆ Diamante', value: 'DIAMOND' },
  PENTAGON: { label: '⬟ Pentágono', value: 'PENTAGON' },
  HEXAGON: { label: '⬢ Hexágono', value: 'HEXAGON' },
  ARROW: { label: '→ Seta', value: 'ARROW' },
  VERTICAL_ARROW: { label: '↑ Seta vertical', value: 'VERTICAL_ARROW' },
  X_MARK: { label: '✕ X', value: 'X_MARK' },
  PLUS_MARK: { label: '+ Mais', value: 'PLUS_MARK' },
} as const;

export const DEFAULT_FORM_STATE = {
  symbology_geometry_type: 'POLYGON' as const,
  symbology_fill_color: '#FF0000',
  symbology_fill_style: 'SOLID' as const,
  symbology_fill_density: 0,
  symbology_stroke_color: '#000000',
  symbology_stroke_style: 'SOLID' as const,
  symbology_stroke_line: 2.0,
};

export const PREVIEW_SIZES = [100, 200, 400, 800] as const;
