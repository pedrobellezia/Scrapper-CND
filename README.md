# Web Scraping Application with FastAPI and Playwright

Aplicação para scraping de CNDs brasileiras via Playwright + 2Captcha.

## Instalação

### Pré-requisitos
- Python 3.10+
- UV (gerenciador de pacotes)

### Setup

1. Clone o repositório:
```bash
git clone <repo-url>
cd teste
```

2. Instale as dependências:
```bash
uv sync
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

4. Execute a aplicação:
```bash
python -m app.app
```

## Configuração

### Variáveis de Ambiente Obrigatórias
- `SECRET_KEY`: Chave secreta para autenticação (mínimo 32 caracteres)
- `CAPTCHA_API_KEY`: Chave da API 2Captcha

### Variáveis de Ambiente Opcionais
- `HOST`: Host do servidor (padrão: 0.0.0.0)
- `PORT`: Porta do servidor (padrão: 5000)
- `RELOAD`: Recarregar servidor em mudanças de código (padrão: false)
- `HEADLESS`: Executar Playwright em modo headless (padrão: false)
- `PAGE_LOAD_TIMEOUT`: Timeout de carregamento de página em ms (padrão: 30000)
- `WAIT_FOR_SELECTOR_TIMEOUT`: Timeout de espera por seletor em ms (padrão: 10000)
- `MAX_RETRIES`: Número máximo de tentativas (padrão: 3)

## Segurança

⚠️ **IMPORTANTE**: 

1. **Nunca commit credenciais reais no git**
   - Renomear `.env` para `.env.example` antes de fazer commit
   - Adicionar `.env` ao `.gitignore`

2. **Rotacionar credenciais imediatamente** se forem expostas

3. **Usar HTTPS em produção** para proteger credenciais

4. **Controlar acesso aos arquivos PDF** em `public/`
   - Implementar autenticação para todos os endpoints (incluindo GET)
   - Usar IDs aleatórios para nomes de arquivo em vez de UUIDs previsíveis

5. **SECRET_KEY deve ter pelo menos 32 caracteres**
   - Usar `secrets.token_urlsafe(32)` para gerar uma chave forte

## Endpoints

### POST /trabalhista
Scraping de CNDs Trabalhistas
```bash
curl -X POST http://localhost:5000/trabalhista \
  -H "Authorization: Bearer YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"cnpj": "12345678000195"}'
```

### POST /fgts
Scraping de CNDs FGTS

### POST /estadual
Scraping de CNDs Estaduais

### POST /municipal
Scraping de CNDs Municipais

## Troubleshooting

### Erro de circular import
Se receber `AttributeError: cannot access submodule 'config'`:
- Verificar que imports em `middlewares.py` são diretos dos módulos específicos
- Não importar de `app.config` dentro de módulos da config

### Browser não inicializa
- Verificar que Playwright está instalado: `playwright install chromium`
- Verificar permissões de execução

## Contribuindo

1. Seguir o padrão de código existente
2. Rodar testes antes de fazer commit
3. Documenter mudanças significativas

## Licença

MIT

