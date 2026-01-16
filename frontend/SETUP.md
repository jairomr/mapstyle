# Setup do Cliente React

Este documento fornece instruções detalhadas para instalar e executar o cliente React em diferentes ambientes.

## Pré-requisitos

- **Node.js >= 18** (LTS recomendado: versão 20+)
- **npm >= 9** ou **yarn >= 1.22** ou **pnpm >= 8**

Se você não tem Node.js instalado, instale a partir de: https://nodejs.org/

## Instalação Rápida

### 1. Navegar para o diretório

```bash
cd /docker/projetos/mapTemaMapBiomas/frontend
```

### 2. Instalar dependências

Escolha uma das opções abaixo:

**Usando npm (padrão)**
```bash
npm install
```

**Usando yarn**
```bash
yarn install
```

**Usando pnpm**
```bash
pnpm install
```

### 3. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env se necessário (padrão já está correto para localhost)
# VITE_API_BASE_URL=http://localhost:8000
```

## Execução

### Servidor de Desenvolvimento

```bash
npm run dev
# ou
yarn dev
# ou
pnpm dev
```

Acesso: http://localhost:5173

### Build para Produção

```bash
npm run build
# ou
yarn build
# ou
pnpm build
```

Saída: `dist/`

### Preview da Produção

```bash
npm run preview
# ou
yarn preview
# ou
pnpm preview
```

## Instalação em Diferentes Ambientes

### macOS

1. Instalar Node.js via Homebrew:
```bash
brew install node
```

2. Seguir instruções padrão acima

### Windows

1. Baixar Node.js de https://nodejs.org/
2. Executar instalador
3. Abrir PowerShell ou CMD nova janela
4. Seguir instruções padrão acima

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install nodejs npm

# Verificar versão
node --version
npm --version
```

### Docker

Se quiser executar em um container Docker:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
```

Build:
```bash
docker build -t maptema-client .
```

Run:
```bash
docker run -p 5173:5173 -v $(pwd):/app maptema-client
```

## Troubleshooting

### "npm: command not found"

**Solução:** Node.js não está instalado. Instale de https://nodejs.org/

### "Port 5173 already in use"

**Solução:** Altere a porta em `vite.config.ts`:
```typescript
server: {
  port: 5174,  // Mudar para outra porta
  strictPort: false,
}
```

### CORS errors na API

**Solução:** Certifique-se de que:
1. A API está rodando em http://localhost:8000 (ou configure em `.env`)
2. CORS está habilitado na API FastAPI

### Erro de módulo não encontrado

**Solução:**
```bash
# Limpar cache
rm -rf node_modules package-lock.json
npm install
```

## Verificação de Instalação

Para verificar se está tudo funcionando:

```bash
# Verificar Node.js
node --version
# Deve ser >= v18

# Verificar npm
npm --version
# Deve ser >= 9

# Verificar dependências
npm list
```

## Próximos Passos

1. **Iniciar a API FastAPI**:
```bash
cd /docker/projetos/mapTemaMapBiomas
uv run python -m scr.api.main
```

2. **Em outro terminal, iniciar o cliente React**:
```bash
cd frontend
npm run dev
```

3. **Acessar em http://localhost:5173**

## Scripts Disponíveis

```json
{
  "dev": "vite",              // Servidor de desenvolvimento
  "build": "tsc -b && vite build",  // Build para produção
  "preview": "vite preview",  // Preview do build
  "lint": "eslint . --ext ts,tsx"   // Linting
}
```

## Variáveis de Ambiente

```env
# URL base da API FastAPI
VITE_API_BASE_URL=http://localhost:8000
```

## Suporte

Para problemas de instalação, verifique:

1. Versão do Node.js: `node --version` (>= 18)
2. Versão do npm: `npm --version` (>= 9)
3. Arquivo `.env` configurado corretamente
4. API FastAPI rodando em `VITE_API_BASE_URL`

---

**Documentação completa:** Ver `README.md`
