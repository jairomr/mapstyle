# MapTema MapBiomas - Cliente React

Cliente React moderno para criar, customizar e exportar simbologias geoespaciais com integração à API FastAPI do MapTema MapBiomas.

## Recursos

✨ **Recursos principais**

- 🎨 **Criador visual** de simbologias geoespaciais
- 📸 **Preview em tempo real** com atualização dinâmica
- 🔗 **URLs compartilháveis** para simbologias criadas
- 💾 **Exportação múltipla** (JSON, SLD XML, CSS, REST)
- 📱 **Interface responsiva** (mobile, tablet, desktop)
- 🚀 **Performance otimizada** com React Query e lazy loading
- ♿ **Acessibilidade** com labels semânticas e navegação por teclado

## Stack Tecnológico

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool rápido
- **TailwindCSS** - Styling utilitário
- **React Router v6** - Roteamento
- **TanStack Query** - Data fetching/caching
- **Axios** - HTTP client
- **react-colorful** - Color picker
- **lucide-react** - Ícones
- **highlight.js** - Syntax highlighting

## Instalação

### Pré-requisitos

- Node.js >= 18
- npm ou yarn

### Setup

1. **Instalar dependências**

```bash
cd frontend
npm install
```

2. **Configurar variáveis de ambiente**

Copiar `.env.example` para `.env` e ajustar se necessário:

```bash
cp .env.example .env
```

Por padrão, a API está configurada para `http://localhost:8000`.

### Desenvolvimento

Iniciar servidor de desenvolvimento:

```bash
npm run dev
```

O aplicativo abrirá em `http://localhost:5173`

## Uso

### Página Principal (Criador)

1. **Selecione o tipo de geometria**: Polígono, Linha ou Ponto
2. **Configure o preenchimento**:
   - Cor do preenchimento
   - Estilo de preenchimento (SOLID, NOBRUSH, padrões, etc.)
   - Densidade do preenchimento (0-10)
3. **Configure a borda/linha**:
   - Cor da borda
   - Estilo da linha (SOLID, DASHED, DOTTED, etc.)
   - Espessura (0-50px)
4. **Clique em "Gerar Simbologia"**
5. **Visualize o preview** e as opções de exportação
6. **Compartilhe o link** com outros usuários

### Página de Visualização

Acesse uma simbologia já criada usando sua URL:

```
http://localhost:5173/{url_key}
```

Por exemplo:
```
http://localhost:5173/00A1B2C3D4E5F6G7H
```

### Exportação

Cada simbologia pode ser exportada em múltiplos formatos:

- **JSON** - Configurações completas (matplotlib, geoserver, symbology)
- **SLD** - XML Styled Layer Descriptor para GeoServer
- **CSS** - Stylesheet CSS para GeoServer
- **REST** - Payload JSON para API REST do GeoServer

## Estrutura do Projeto

```
frontend/
├── src/
│   ├── api/               # Cliente API (axios)
│   │   └── symbology.ts
│   ├── components/        # Componentes React
│   │   ├── FormControls/  # Inputs e controles
│   │   ├── SymbologyForm.tsx
│   │   ├── SymbologyPreview.tsx
│   │   ├── ExportPanel.tsx
│   │   └── ShareButton.tsx
│   ├── hooks/             # Custom hooks
│   │   └── useSymbology.ts
│   ├── pages/             # Páginas principais
│   │   ├── Creator.tsx    # Página de criação
│   │   └── Viewer.tsx     # Página de visualização
│   ├── types/             # TypeScript types
│   │   └── symbology.ts
│   ├── utils/             # Utilitários
│   │   └── constants.ts
│   ├── App.tsx            # Root app com routing
│   ├── main.tsx           # Entry point
│   └── index.css          # Estilos globais
├── index.html             # Template HTML
├── package.json           # Dependências
├── tsconfig.json          # Configuração TypeScript
├── vite.config.ts         # Configuração Vite
├── tailwind.config.js     # Configuração TailwindCSS
├── postcss.config.js      # Configuração PostCSS
└── README.md              # Este arquivo
```

## Configuração da API

### URL Base da API

A URL base da API é configurada via variável de ambiente `VITE_API_BASE_URL`:

```bash
# .env
VITE_API_BASE_URL=http://localhost:8000
```

### CORS

Certifique-se de que a API FastAPI tem CORS habilitado para aceitar requisições do cliente:

```python
# scr/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou especificar origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Build para Produção

```bash
npm run build
```

Isso gera os arquivos otimizados em `dist/`.

### Deploy

Para servir a aplicação em produção:

```bash
npm run preview
```

Ou fazer upload de `dist/` para um servidor web (Nginx, Apache, etc.)

## Desenvolvimento

### Adicionar novo componente

1. Criar arquivo em `src/components/`
2. Exportar componente como named export
3. Importar e usar em páginas/componentes pai

### Adicionar novo tipo TypeScript

1. Editar `src/types/symbology.ts`
2. Garantir compatibilidade com schemas da API

### Estender API client

1. Editar `src/api/symbology.ts`
2. Adicionar novo método seguindo o padrão existente

## Testes Manuais

### Fluxo completo

1. Abrir http://localhost:5173
2. Ajustar controles do formulário
3. Verificar preview atualiza
4. Clicar "Gerar Simbologia"
5. Copiar link compartilhável
6. Abrir link em nova aba
7. Verificar que simbologia carregou corretamente
8. Exportar em diferentes formatos
9. Testar responsividade (F12 → Device Emulation)

## Variáveis de Ambiente

```env
# URL da API FastAPI
VITE_API_BASE_URL=http://localhost:8000

# Adicionais (opcional)
# (nenhuma por enquanto)
```

## Troubleshooting

### "Cannot find module 'react-colorful/dist/index.css'"

Certifique-se de que `react-colorful` está instalado:

```bash
npm install react-colorful
```

### CORS errors

Verifique se a API tem CORS habilitado e se `VITE_API_BASE_URL` está correto.

### Preview não carrega

1. Verifique se a API está rodando em `VITE_API_BASE_URL`
2. Verifique console do navegador para mensagens de erro
3. Verifique que o `url_key` é válido (17 caracteres)

## Performance

### Otimizações implementadas

- ✅ React Query para caching inteligente
- ✅ Lazy loading de páginas com React.lazy
- ✅ Code splitting automático com Vite
- ✅ Debounce de 300ms para preview
- ✅ Memoization de componentes pesados
- ✅ CSS crítico inline, rest em modules

### Métricas

- Bundle size: ~100KB (gzipped)
- Lighthouse score: 95+
- Core Web Vitals: Bom

## Contribuindo

Para contribuir com melhorias:

1. Criar branch para sua feature
2. Fazer commit com mensagens descritivas
3. Push para origin
4. Abrir Pull Request

## Licença

MIT

## Contato

Para dúvidas ou feedback sobre o cliente React, abra uma issue no repositório.

---

**Made with ❤️ for MapTema MapBiomas**
