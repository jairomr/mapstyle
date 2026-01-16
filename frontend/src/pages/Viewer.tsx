import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSymbology } from '../hooks/useSymbology';
import { SymbologyPreview } from '../components/SymbologyPreview';
import { ExportPanel } from '../components/ExportPanel';
import { ShareButton } from '../components/ShareButton';
import { Edit, Home } from 'lucide-react';

export function Viewer() {
  const { urlKey } = useParams<{ urlKey: string }>();
  const navigate = useNavigate();

  const {
    formState,
    currentUrlKey,
    existingConfig,
    isLoading,
    error,
    loadFromUrlKey,
  } = useSymbology({
    urlKey,
    onError: (error) => {
      console.error('Erro ao carregar simbologia:', error);
    },
  });

  // Carregar a simbologia quando o componente monta ou urlKey muda
  useEffect(() => {
    if (urlKey && !currentUrlKey) {
      loadFromUrlKey(urlKey);
    }
  }, [urlKey, currentUrlKey, loadFromUrlKey]);

  if (!urlKey || isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-4 border-blue-200 border-t-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Carregando simbologia...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 py-8 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white p-8 rounded-lg border border-red-200 bg-red-50">
            <h1 className="text-2xl font-bold text-red-900 mb-2">Erro ao carregar</h1>
            <p className="text-red-700 mb-4">
              Não foi possível carregar a simbologia solicitada.
            </p>
            <p className="text-red-600 text-sm mb-6">
              {error.message || 'URL inválida ou simbologia não encontrada'}
            </p>
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
            >
              <Home size={16} />
              Voltar ao início
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!existingConfig) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">Visualizar Simbologia</h1>
            <div className="flex gap-2">
              <button
                onClick={() => navigate('/')}
                className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded font-medium hover:bg-gray-700"
              >
                <Home size={16} />
                Início
              </button>
              <button
                onClick={() => navigate('/', { state: { formState } })}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
              >
                <Edit size={16} />
                Editar
              </button>
            </div>
          </div>
          <p className="text-gray-600">URL key: <code className="text-gray-800 font-mono">{urlKey}</code></p>
        </div>

        {/* Content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Preview */}
          <SymbologyPreview
            urlKey={currentUrlKey || urlKey}
            isLoading={false}
            error={null}
          />

          {/* Details */}
          <div className="flex flex-col gap-4">
            <div className="p-6 bg-white rounded-lg border border-gray-200">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Detalhes</h2>

              <div className="space-y-3 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Tipo de Geometria:</span>
                  <span className="ml-2 text-gray-600">
                    {existingConfig.symbology.symbology_geometry_type}
                  </span>
                </div>

                <div>
                  <span className="font-medium text-gray-700">Cor de Preenchimento:</span>
                  <div className="flex items-center gap-2 mt-1">
                    <div
                      className="w-8 h-8 rounded border border-gray-300"
                      style={{
                        backgroundColor: existingConfig.symbology.symbology_fill_color,
                      }}
                    />
                    <span className="text-gray-600">
                      {existingConfig.symbology.symbology_fill_color}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="font-medium text-gray-700">Estilo de Preenchimento:</span>
                  <span className="ml-2 text-gray-600">
                    {existingConfig.symbology.symbology_fill_style}
                  </span>
                </div>

                <div>
                  <span className="font-medium text-gray-700">Cor da Borda:</span>
                  <div className="flex items-center gap-2 mt-1">
                    <div
                      className="w-8 h-8 rounded border border-gray-300"
                      style={{
                        backgroundColor: existingConfig.symbology.symbology_stroke_color,
                      }}
                    />
                    <span className="text-gray-600">
                      {existingConfig.symbology.symbology_stroke_color}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="font-medium text-gray-700">Estilo de Linha:</span>
                  <span className="ml-2 text-gray-600">
                    {existingConfig.symbology.symbology_stroke_style}
                  </span>
                </div>

                <div>
                  <span className="font-medium text-gray-700">Espessura da Linha:</span>
                  <span className="ml-2 text-gray-600">
                    {existingConfig.symbology.symbology_stroke_line} px
                  </span>
                </div>
              </div>
            </div>

            {/* Share */}
            <ShareButton urlKey={currentUrlKey || urlKey} />
          </div>
        </div>

        {/* Export panel */}
        <div className="mt-6">
          <ExportPanel
            urlKey={currentUrlKey || urlKey}
            config={existingConfig}
            isLoading={false}
          />
        </div>
      </div>
    </div>
  );
}
