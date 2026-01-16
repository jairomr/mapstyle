import { useState, useEffect } from 'react';
import { api } from '../api/symbology';
import { PREVIEW_SIZES } from '../utils/constants';

interface SymbologyPreviewProps {
  urlKey: string | null;
  isLoading?: boolean;
  error?: Error | null;
}

export function SymbologyPreview({
  urlKey,
  isLoading = false,
  error,
}: SymbologyPreviewProps) {
  const [size, setSize] = useState<number>(200);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoadingImage, setIsLoadingImage] = useState(false);

  useEffect(() => {
    if (urlKey) {
      setIsLoadingImage(true);
      setImageUrl(api.getPreviewUrl(urlKey, size));
    }
  }, [urlKey, size]);

  return (
    <div className="flex flex-col gap-4 p-6 bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Preview</h2>

        {urlKey && (
          <div className="text-sm bg-gray-100 px-3 py-1 rounded font-mono text-gray-600">
            {urlKey}
          </div>
        )}
      </div>

      {/* Size selector */}
      {urlKey && (
        <div className="flex gap-2">
          <label className="text-sm font-medium text-gray-700">Tamanho:</label>
          <div className="flex gap-2">
            {PREVIEW_SIZES.map((s) => (
              <button
                key={s}
                onClick={() => setSize(s)}
                className={`px-3 py-1 text-sm rounded border transition ${
                  size === s
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                {s}px
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Preview container */}
      <div className="flex-1 flex items-center justify-center min-h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
        {isLoading ? (
          <div className="text-center">
            <div className="w-12 h-12 rounded-full border-4 border-blue-200 border-t-blue-500 animate-spin mx-auto mb-2" />
            <p className="text-gray-600 text-sm">Carregando preview...</p>
          </div>
        ) : error ? (
          <div className="text-center">
            <p className="text-red-600 text-sm font-medium">Erro ao carregar preview</p>
            <p className="text-gray-500 text-xs mt-1">{error.message}</p>
          </div>
        ) : imageUrl ? (
          <img
            key={imageUrl}
            src={imageUrl}
            alt="Simbologia preview"
            onLoad={() => setIsLoadingImage(false)}
            className="max-w-full max-h-80 object-contain"
          />
        ) : (
          <div className="text-center text-gray-500">
            <p className="text-sm">Configure a simbologia e clique em "Gerar"</p>
          </div>
        )}
      </div>

      {urlKey && (
        <div className="text-xs text-gray-500 text-center">
          URL: <code className="text-gray-600">{api.getPreviewUrl(urlKey, size)}</code>
        </div>
      )}
    </div>
  );
}
