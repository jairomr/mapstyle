import { useState, useRef, useEffect } from 'react';
import { ChromePicker } from 'react-color';
import { X } from 'lucide-react';

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
  label?: string;
}

export function ColorPicker({ value, onChange, label }: ColorPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const pickerRef = useRef<HTMLDivElement>(null);

  // Fechar ColorPicker quando clicar fora
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleColorChange = (color: any) => {
    onChange(color.hex);
  };

  return (
    <div className="flex flex-col gap-3">
      {label && <label className="text-base font-semibold text-gray-800">{label}</label>}

      <div className="flex gap-3 items-center">
        {/* Swatch visual */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="w-14 h-14 rounded border-2 border-gray-300 hover:border-gray-400 transition"
          style={{ backgroundColor: value }}
          title="Clique para abrir seletor"
        />

        {/* Input texto */}
        <input
          type="text"
          value={value}
          onChange={(e) => {
            const val = e.target.value;
            if (val.startsWith('#') && (val.length === 7 || val.length === 4)) {
              onChange(val);
            }
          }}
          placeholder="#FF0000"
          className="flex-1 px-3 py-2 border border-gray-300 rounded text-base font-mono focus:border-gray-400 focus:outline-none"
        />
      </div>

      {/* Color picker */}
      {isOpen && (
        <div
          ref={pickerRef}
          className="relative p-4 border border-gray-300 rounded bg-white shadow-lg"
        >
          {/* Botão X para fechar */}
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            className="absolute top-2 right-2 p-1 text-gray-500 hover:text-gray-700 transition"
            title="Fechar"
          >
            <X size={20} />
          </button>

          {/* ChromePicker */}
          <div className="mt-2">
            <ChromePicker
              color={value}
              onChange={handleColorChange}
              disableAlpha
              width="100%"
            />
          </div>
        </div>
      )}
    </div>
  );
}
