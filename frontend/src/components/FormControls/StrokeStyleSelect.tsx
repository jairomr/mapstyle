import { LineStyle } from '../../types/symbology';

// Nomes válidos para LineStyle
const VALID_STYLES = ['SOLID', 'DASHED', 'DOTTED', 'DASH_DOT', 'LONG_DASH', 'SHORT_DASH', 'DASH_DOT_DOT', 'DASH_DOT_DOT_DOT', 'SPARSE_DOT', 'DENSE_DOT', 'NONE'] as const;

const STYLE_LABELS: Record<string, string> = {
  SOLID: 'Sólido',
  DASHED: 'Tracejado',
  DOTTED: 'Pontilhado',
  DASH_DOT: 'Traço-ponto',
  LONG_DASH: 'Traço longo',
  SHORT_DASH: 'Traço curto',
  DASH_DOT_DOT: 'Traço-ponto-ponto',
  DASH_DOT_DOT_DOT: 'Traço-ponto-ponto-ponto',
  SPARSE_DOT: 'Pontos espaçados',
  DENSE_DOT: 'Pontos densos',
  NONE: 'Nenhum',
};

interface StrokeStyleSelectProps {
  value: LineStyle;
  onChange: (value: LineStyle) => void;
}

export function StrokeStyleSelect({
  value,
  onChange,
}: StrokeStyleSelectProps) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-gray-700">Estilo de Linha</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as LineStyle)}
        className="px-3 py-2 border border-gray-300 rounded text-sm"
      >
        {VALID_STYLES.map((style) => (
          <option key={style} value={style}>
            {STYLE_LABELS[style]}
          </option>
        ))}
      </select>
    </div>
  );
}
