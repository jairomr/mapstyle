# Docker Setup

Este projeto está totalmente containerizado com Docker usando as melhores práticas:
- Multi-stage build para otimização
- Usuário não-root (appuser)
- Virtual environment isolado
- Docker networking com hostnames
- Reverse proxy nginx para produção
- Healthchecks integrados

## Arquitetura

### Desenvolvimento
```
Browser -> Vite Dev Server (localhost:5175)
                ↓ (proxy /api)
         Backend via Docker hostname (backend:8000)
```

Vite proxy automaticamente redireciona `/api/*` para `http://backend:8000` usando o hostname interno do Docker.

### Produção
```
Browser -> Nginx (localhost:80)
            ├─> Frontend (static files)
            └─> /api/* -> Backend (backend:8000)
```

Nginx reverse proxy centraliza tudo em uma porta única. Backend é acessado via hostname Docker interno.

## Pré-requisitos

- Docker >= 20.10
- Docker Compose >= 2.0

## Desenvolvimento

Para rodar em modo desenvolvimento com hot reload:

```bash
docker-compose -f docker-compose.dev.yml up
```

Isso irá:
- Backend rodando em `http://localhost:8090`
- Frontend rodando em `http://localhost:5175`
- API docs em `http://localhost:8090/docs`
- Vite proxy: `/api/*` → `http://backend:8000` (interno)

### Como funciona em desenvolvimento

1. Frontend acessa `http://localhost:5175`
2. Ao fazer requisição para `/api/something`, Vite proxy intercepta
3. Vite proxeia internamente para `http://backend:8000/something` (via hostname Docker)
4. Resposta volta para o frontend

**Nenhum hardcode de localhost**, tudo usa DNS interno do Docker.

### Comandos úteis

```bash
# Build das imagens
docker-compose -f docker-compose.dev.yml build

# Rebuild sem cache
docker-compose -f docker-compose.dev.yml build --no-cache

# Ver logs em tempo real
docker-compose -f docker-compose.dev.yml logs -f

# Ver logs de um serviço específico
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# Parar os containers
docker-compose -f docker-compose.dev.yml down

# Parar e remover volumes
docker-compose -f docker-compose.dev.yml down -v

# Executar comando no container backend
docker-compose -f docker-compose.dev.yml exec backend sh

# Executar testes
docker-compose -f docker-compose.dev.yml exec backend pytest
```

## Produção

Para rodar em produção:

```bash
docker-compose up -d
```

Isso irá:
- **Backend**: Rodando em porta interna 8000 (não exposto)
- **Frontend**: Build estático em `/app/dist`
- **Nginx**: Reverse proxy na porta 80
  - `http://seu-ip/` → Frontend (estático)
  - `http://seu-ip/api/*` → Backend (backend:8000)

### Como funciona em produção

1. Nginx bind na porta 80 (único ponto de entrada)
2. Requisições para `/` servem frontend estático (cache otimizado)
3. Requisições para `/api/*` são proxiadas para `http://backend:8000` (via hostname Docker)
4. Backend não é exposto diretamente (segurança)
5. Healthchecks garantem que backend esteja pronto antes do nginx

### Acessar de outra máquina

```
http://<ip-do-servidor>/     # Frontend
http://<ip-do-servidor>/api  # API
```

**Tudo funciona automaticamente** porque nginx usa hostname Docker para comunicação interna.

## Configuração

### Frontend - vite.config.js

```javascript
proxy: {
    '/api': {
        target: 'http://backend:8000',  // Hostname Docker
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
    },
}
```

Isso configura o Vite dev server para proxiar `/api/*` para o backend em desenvolvimento.

### Nginx - nginx.conf

```nginx
location /api/ {
    proxy_pass http://backend:8000/;  // Hostname Docker
    # Headers de proxy...
}
```

Nginx proxeia `/api/*` para backend usando hostname interno.

## Variáveis de Ambiente

Veja `.env.example`. Não há variáveis hardcoded de URL - tudo usa:
- **Dev**: Vite proxy (automático)
- **Prod**: Nginx proxy (automático)

## Troubleshooting

### Conexão Backend/Frontend falha

Verifique se backend está healthy:
```bash
docker-compose -f docker-compose.dev.yml logs backend
```

### Port 80 já em uso

```bash
sudo lsof -i :80
```

Para dev, usar:
```bash
docker-compose -f docker-compose.dev.yml up
```
Porta 5175 é usada normalmente.

### Frontend não consegue chamar API

1. **Dev**: Verificar se Vite proxy está funcionando
   ```bash
   docker-compose -f docker-compose.dev.yml logs frontend
   ```

2. **Prod**: Verificar se nginx está rodando
   ```bash
   docker-compose logs nginx
   docker-compose exec nginx wget -O - http://localhost/api/health
   ```

### Limpar tudo e começar do zero

```bash
docker-compose -f docker-compose.dev.yml down -v
docker system prune -a
docker-compose -f docker-compose.dev.yml up --build
```

## Security

- Usuários não-root executam containers
- Healthchecks garantem disponibilidade
- Headers de segurança no nginx (HSTS, CSP, etc)
- Backend não exposto diretamente em produção
- Volumes read-only para arquivos estáticos
