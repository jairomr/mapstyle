import { useSymbology } from '../hooks/useSymbology';
import { SymbologyForm } from '../components/SymbologyForm';
import { SymbologyPreview } from '../components/SymbologyPreview';
import { ExportPanel } from '../components/ExportPanel';
import { ShareButton } from '../components/ShareButton';

export function Creator() {
  const {
    formState,
    currentUrlKey,
    existingConfig,
    isLoading,
    error,
    updateFormField,
    createSymbology,
  } = useSymbology({
    onSuccess: (response) => {
      console.log('Simbologia criada:', response.url_key);
    },
  });

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">MapTema MapBiomas</h1>
          <p className="text-gray-600">
            Crie, customize e exporte simbologias geoespaciais
          </p>
        </div>

        {/* Main content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left column: Form */}
          <div className="flex flex-col gap-4">
            <SymbologyForm
              formState={formState}
              onFieldChange={updateFormField}
              onSubmit={createSymbology}
              isLoading={isLoading}
            />

            {/* Share button */}
            {currentUrlKey && (
              <ShareButton urlKey={currentUrlKey} />
            )}
          </div>

          {/* Right column: Preview */}
          <SymbologyPreview
            urlKey={currentUrlKey}
            isLoading={isLoading}
            error={error as Error}
          />
        </div>

        {/* Export panel - full width below */}
        {currentUrlKey && existingConfig && (
          <div className="mt-6">
            <ExportPanel
              urlKey={currentUrlKey}
              config={existingConfig}
              isLoading={isLoading}
            />
          </div>
        )}
      </div>
    </div>
  );
}
