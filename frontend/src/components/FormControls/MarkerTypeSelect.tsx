import { MarkerType } from '../../types/symbology';

// Nomes válidos para MarkerType
const VALID_MARKERS = ['CIRCLE', 'SQUARE', 'TRIANGLE', 'STAR', 'CROSS', 'DIAMOND', 'PENTAGON', 'HEXAGON', 'ARROW', 'VERTICAL_ARROW', 'X_MARK', 'PLUS_MARK'] as const;

const MARKER_LABELS: Record<MarkerType, string> = {
  CIRCLE: '● Círculo',
  SQUARE: '■ Quadrado',
  TRIANGLE: '▲ Triângulo',
  STAR: '★ Estrela',
  CROSS: '+ Cruz',
  DIAMOND: '◆ Diamante',
  PENTAGON: '⬟ Pentágono',
  HEXAGON: '⬢ Hexágono',
  ARROW: '→ Seta',
  VERTICAL_ARROW: '↑ Seta vertical',
  X_MARK: '✕ X',
  PLUS_MARK: '+ Mais',
};

interface MarkerTypeSelectProps {
  value: MarkerType;
  onChange: (value: MarkerType) => void;
}

export function MarkerTypeSelect({
  value,
  onChange,
}: MarkerTypeSelectProps) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-gray-700">Tipo de Marcador</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as MarkerType)}
        className="px-3 py-2 border border-gray-300 rounded text-sm"
      >
        {VALID_MARKERS.map((marker) => (
          <option key={marker} value={marker}>
            {MARKER_LABELS[marker]}
          </option>
        ))}
      </select>
    </div>
  );
}
