import { Square, Minus, Dot } from 'lucide-react';
import { SymbologyGeometryType } from '../../types/symbology';

interface GeometryTypeSelectProps {
  value: SymbologyGeometryType;
  onChange: (value: SymbologyGeometryType) => void;
}

const OPTIONS = [
  { value: 'POLYGON' as const, label: 'Polígono', icon: Square },
  { value: 'LINE' as const, label: 'Linha', icon: Minus },
  { value: 'POINT' as const, label: 'Ponto', icon: Dot },
];

export function GeometryTypeSelect({ value, onChange }: GeometryTypeSelectProps) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-gray-700">Tipo de Geometria</label>
      <div className="grid grid-cols-3 gap-2">
        {OPTIONS.map((option) => {
          const Icon = option.icon;
          return (
            <button
              key={option.value}
              onClick={() => onChange(option.value)}
              className={`flex flex-col items-center gap-2 p-3 rounded border-2 transition ${
                value === option.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <Icon size={24} className="text-gray-600" />
              <span className="text-xs font-medium text-gray-700">{option.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
