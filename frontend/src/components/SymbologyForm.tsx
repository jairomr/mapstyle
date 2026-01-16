import { FormState, SymbologyFill, LineStyle, MarkerType } from '../types/symbology';
import { ColorPicker } from './FormControls/ColorPicker';
import { GeometryTypeSelect } from './FormControls/GeometryTypeSelect';
import { FillStyleSelect } from './FormControls/FillStyleSelect';
import { MarkerTypeSelect } from './FormControls/MarkerTypeSelect';
import { StrokeStyleSelect } from './FormControls/StrokeStyleSelect';
import { NumberSlider } from './FormControls/NumberSlider';

interface SymbologyFormProps {
  formState: FormState;
  onFieldChange: <K extends keyof FormState>(field: K, value: FormState[K]) => void;
  onSubmit: () => Promise<void>;
  isLoading?: boolean;
}

export function SymbologyForm({
  formState,
  onFieldChange,
  onSubmit,
  isLoading = false,
}: SymbologyFormProps) {
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onSubmit();
    } catch (error) {
      // Erro será mostrado no estado do componente pai
      console.error('Erro ao enviar formulário:', error);
    }
  };

  const handleGeometryTypeChange = (value: string) => {
    onFieldChange('symbology_geometry_type', value as any);

    // Quando muda para POINT, usa um marcador padrão
    if (value === 'POINT') {
      onFieldChange('symbology_fill_style', 'CIRCLE' as any);
    }
    // Quando muda para POLYGON/LINE, usa preenchimento padrão
    else {
      onFieldChange('symbology_fill_style', 'SOLID' as any);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6 p-6 bg-white rounded border border-gray-200">
      <h2 className="text-2xl font-bold text-gray-900">Criar Simbologia</h2>

      {/* Geometry Type */}
      <section>
        <GeometryTypeSelect
          value={formState.symbology_geometry_type}
          onChange={handleGeometryTypeChange}
        />
      </section>

      {/* Fill Settings */}
      <section className="border-t pt-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">
          {formState.symbology_geometry_type === 'POINT' ? 'Configurações do Marcador' : 'Configurações de Preenchimento'}
        </h3>

        <div className="flex flex-col gap-4">
          <ColorPicker
            label={formState.symbology_geometry_type === 'POINT' ? 'Cor do Marcador' : 'Cor de Preenchimento'}
            value={formState.symbology_fill_color}
            onChange={(color) => onFieldChange('symbology_fill_color', color)}
          />

          {formState.symbology_geometry_type === 'POINT' ? (
            <>
              <MarkerTypeSelect
                value={formState.symbology_fill_style as MarkerType}
                onChange={(style) => onFieldChange('symbology_fill_style', style)}
              />

              <NumberSlider
                label="Tamanho do Marcador"
                value={formState.symbology_fill_density}
                onChange={(value) => onFieldChange('symbology_fill_density', value)}
                min={0}
                max={10}
                step={1}
              />
            </>
          ) : (
            <>
              <div>
                <FillStyleSelect
                  value={formState.symbology_fill_style as SymbologyFill}
                  onChange={(style) => onFieldChange('symbology_fill_style', style)}
                />
              </div>

              <NumberSlider
                label="Densidade do Preenchimento"
                value={formState.symbology_fill_density}
                onChange={(value) => onFieldChange('symbology_fill_density', value)}
                min={0}
                max={10}
                step={1}
              />
            </>
          )}
        </div>
      </section>

      {/* Stroke Settings */}
      <section className="border-t pt-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">
          {formState.symbology_geometry_type === 'POINT'
            ? 'Configurações da Borda do Marcador'
            : formState.symbology_geometry_type === 'LINE'
            ? 'Configurações da Linha'
            : 'Configurações de Borda'}
        </h3>

        <div className="flex flex-col gap-4">
          <ColorPicker
            label={formState.symbology_geometry_type === 'POINT' ? 'Cor da Borda do Marcador' : 'Cor da Borda/Linha'}
            value={formState.symbology_stroke_color}
            onChange={(color) => onFieldChange('symbology_stroke_color', color)}
          />

          <div>
            <StrokeStyleSelect
              value={formState.symbology_stroke_style as LineStyle}
              onChange={(style) => onFieldChange('symbology_stroke_style', style)}
            />
          </div>

          <NumberSlider
            label={
              formState.symbology_geometry_type === 'POINT'
                ? 'Espessura da Borda do Marcador'
                : formState.symbology_geometry_type === 'LINE'
                ? 'Espessura da Linha'
                : 'Espessura da Borda'
            }
            value={formState.symbology_stroke_line}
            onChange={(value) => onFieldChange('symbology_stroke_line', value)}
            min={0}
            max={50}
            step={0.5}
            unit="px"
          />
        </div>
      </section>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
      >
        {isLoading ? 'Gerando...' : 'Gerar Simbologia'}
      </button>
    </form>
  );
}
