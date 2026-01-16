import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface ShareButtonProps {
  urlKey: string | null;
}

export function ShareButton({ urlKey }: ShareButtonProps) {
  const [copied, setCopied] = useState(false);

  const getShareUrl = () => {
    if (!urlKey) return '';
    const baseUrl = window.location.origin;
    return `${baseUrl}/${urlKey}`;
  };

  const handleCopyLink = async () => {
    const shareUrl = getShareUrl();
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Erro ao copiar:', err);
    }
  };

  if (!urlKey) {
    return null;
  }

  return (
    <div className="flex flex-col gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
      <label className="text-sm font-medium text-green-900">Link Compartilhável</label>
      <div className="flex gap-2">
        <input
          type="text"
          value={getShareUrl()}
          readOnly
          className="flex-1 px-3 py-2 text-sm font-mono bg-white border border-green-300 rounded text-gray-700"
        />
        <button
          onClick={handleCopyLink}
          className={`px-4 py-2 rounded font-medium text-white transition flex items-center gap-2 ${
            copied
              ? 'bg-green-600'
              : 'bg-green-500 hover:bg-green-600'
          }`}
        >
          {copied ? (
            <>
              <Check size={16} />
              Copiado
            </>
          ) : (
            <>
              <Copy size={16} />
              Copiar
            </>
          )}
        </button>
      </div>
    </div>
  );
}
