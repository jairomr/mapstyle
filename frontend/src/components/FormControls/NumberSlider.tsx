interface NumberSliderProps {
  value: number;
  onChange: (value: number) => void;
  label: string;
  min: number;
  max: number;
  step?: number;
  unit?: string;
}

export function NumberSlider({
  value,
  onChange,
  label,
  min,
  max,
  step = 0.1,
  unit,
}: NumberSliderProps) {
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(parseFloat(e.target.value));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const num = parseFloat(e.target.value);
    if (!isNaN(num)) {
      onChange(Math.min(Math.max(num, min), max));
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <div className="flex items-center gap-1">
          <input
            type="number"
            value={value}
            onChange={handleInputChange}
            min={min}
            max={max}
            step={step}
            className="w-20 px-2 py-1 border border-gray-300 rounded text-sm text-right"
          />
          {unit && <span className="text-sm text-gray-600">{unit}</span>}
        </div>
      </div>

      {/* Slider */}
      <input
        type="range"
        value={value}
        onChange={handleSliderChange}
        min={min}
        max={max}
        step={step}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
      />

      {/* Labels min/max */}
      <div className="flex justify-between text-xs text-gray-500 px-1">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}
