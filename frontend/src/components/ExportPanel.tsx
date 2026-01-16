import { useState, useEffect } from 'react';
import { Copy, Download, Check } from 'lucide-react';
import { api } from '../api/symbology';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-light.css';

interface ExportPanelProps {
  urlKey: string | null;
  config: any | null;
  isLoading?: boolean;
}

type TabType = 'json' | 'sld' | 'css' | 'rest';

export function ExportPanel({ urlKey, config, isLoading = false }: ExportPanelProps) {
  const [activeTab, setActiveTab] = useState<TabType>('json');
  const [tabContent, setTabContent] = useState<Record<TabType, string>>({
    json: '',
    sld: '',
    css: '',
    rest: '',
  });
  const [loadingTabs, setLoadingTabs] = useState<Set<TabType>>(new Set());
  const [copied, setCopied] = useState<TabType | null>(null);

  // Carregar conteúdo dos tabs sob demanda
  useEffect(() => {
    if (!urlKey || !config) return;

    const loadTabContent = async (tab: TabType) => {
      try {
        setLoadingTabs((prev) => new Set([...prev, tab]));

        let content = '';

        if (tab === 'json') {
          content = JSON.stringify(config, null, 2);
        } else if (tab === 'sld') {
          content = await api.getSld(urlKey);
        } else if (tab === 'css') {
          content = await api.getCss(urlKey);
        } else if (tab === 'rest') {
          content = await api.getRest(urlKey);
        }

        setTabContent((prev) => ({ ...prev, [tab]: content }));
        setLoadingTabs((prev) => {
          const next = new Set(prev);
          next.delete(tab);
          return next;
        });
      } catch (err) {
        console.error(`Erro ao carregar ${tab}:`, err);
        setLoadingTabs((prev) => {
          const next = new Set(prev);
          next.delete(tab);
          return next;
        });
      }
    };

    if (!tabContent[activeTab]) {
      loadTabContent(activeTab);
    }
  }, [urlKey, config, activeTab, tabContent]);

  const handleCopyContent = async () => {
    try {
      await navigator.clipboard.writeText(tabContent[activeTab]);
      setCopied(activeTab);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error('Erro ao copiar:', err);
    }
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    element.setAttribute(
      'href',
      `data:text/plain;charset=utf-8,${encodeURIComponent(tabContent[activeTab])}`
    );

    const fileExtensions: Record<TabType, string> = {
      json: 'json',
      sld: 'sld',
      css: 'css',
      rest: 'json',
    };

    element.setAttribute(
      'download',
      `symbology-${urlKey}.${fileExtensions[activeTab]}`
    );
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const getHighlightLanguage = (tab: TabType): string => {
    if (tab === 'json' || tab === 'rest') return 'json';
    if (tab === 'sld') return 'xml';
    if (tab === 'css') return 'css';
    return 'plaintext';
  };

  const highlightCode = (code: string, language: string) => {
    try {
      return hljs.highlight(code, { language, ignoreIllegals: true }).value;
    } catch {
      return code;
    }
  };

  if (!urlKey || !config) {
    return null;
  }

  const tabs: Array<{ id: TabType; label: string }> = [
    { id: 'json', label: 'JSON' },
    { id: 'sld', label: 'SLD (XML)' },
    { id: 'css', label: 'CSS' },
    { id: 'rest', label: 'REST Payload' },
  ];

  const isLoading_ = loadingTabs.has(activeTab);
  const highlightedCode = highlightCode(
    tabContent[activeTab],
    getHighlightLanguage(activeTab)
  );

  return (
    <div className="flex flex-col gap-4 p-6 bg-white rounded-lg border border-gray-200">
      <h2 className="text-xl font-bold text-gray-900">Exportar Configurações</h2>

      {/* Tab buttons */}
      <div className="flex gap-2 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium text-sm transition border-b-2 ${
              activeTab === tab.id
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content area */}
      <div className="flex-1 relative">
        {isLoading_ ? (
          <div className="h-64 flex items-center justify-center">
            <div className="w-8 h-8 rounded-full border-4 border-blue-200 border-t-blue-500 animate-spin" />
          </div>
        ) : (
          <>
            <pre className="bg-gray-50 rounded border border-gray-200 p-4 overflow-auto max-h-96 text-sm">
              <code
                dangerouslySetInnerHTML={{
                  __html: highlightedCode,
                }}
              />
            </pre>

            {/* Action buttons */}
            <div className="flex gap-2 mt-4">
              <button
                onClick={handleCopyContent}
                className={`flex items-center gap-2 px-4 py-2 rounded font-medium text-sm transition ${
                  copied === activeTab
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
                }`}
              >
                {copied === activeTab ? (
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

              <button
                onClick={handleDownload}
                className="flex items-center gap-2 px-4 py-2 rounded font-medium text-sm bg-blue-500 text-white hover:bg-blue-600 transition"
              >
                <Download size={16} />
                Download
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
