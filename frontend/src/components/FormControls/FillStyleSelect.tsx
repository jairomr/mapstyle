import { SymbologyFill } from '../../types/symbology';

// Nomes válidos para SymbologyFill
const VALID_STYLES = ['SOLID', 'NOBRUSH', 'SLASH', 'BACKSLASH', 'PIPE', 'DASH', 'PLUS', 'X', 'O_LOWER', 'O_UPPER', 'DOT', 'STAR'] as const;

const STYLE_LABELS: Record<string, string> = {
  SOLID: 'Sólido',
  NOBRUSH: 'Sem preenchimento',
  SLASH: 'Barras /',
  BACKSLASH: 'Barras \\',
  PIPE: 'Linhas verticais',
  DASH: 'Traços',
  PLUS: 'Mais (+)',
  X: 'Xis (X)',
  O_LOWER: 'Círculos pequenos',
  O_UPPER: 'Círculos grandes',
  DOT: 'Pontos',
  STAR: 'Estrelas',
};

interface FillStyleSelectProps {
  value: SymbologyFill;
  onChange: (value: SymbologyFill) => void;
}

export function FillStyleSelect({
  value,
  onChange,
}: FillStyleSelectProps) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-gray-700">Estilo de Preenchimento</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as SymbologyFill)}
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
