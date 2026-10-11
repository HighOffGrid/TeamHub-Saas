# TeamHub SaaS API

API backend para uma plataforma colaborativa de gestão de equipes, desenvolvida com FastAPI. O projeto permite autenticação de usuários, organizações, memberships, projetos e tarefas, com controles adicionais de segurança e infraestrutura.

**Stack:** Python · FastAPI · SQLModel · SQLAlchemy · Alembic · Redis · Docker · Pytest

---

## Sobre o projeto

O TeamHub SaaS API é um projeto de backend voltado para cenários de colaboração entre equipes e gestão de trabalho em ambientes organizacionais.

A aplicação foi organizada em módulos de domínio e infraestrutura, separando rotas, schemas, models e componentes centrais de configuração, segurança, banco de dados, Redis, rate limiting e auditoria. Essa organização torna o código mais fácil de manter e testar.

---

## Funcionalidades

- Cadastro de usuários.
- Login com autenticação JWT.
- Proteção de senhas com hash seguro.
- Organizações e memberships entre usuários e organizações.
- Gestão de projetos.
- Gestão de tarefas.
- Rate limiting com Redis em endpoints sensíveis.
- Registro de eventos de auditoria via `BackgroundTasks`.
- Migrations versionadas com Alembic.
- Configuração por variáveis de ambiente.
- Documentação automática da API com Swagger e ReDoc.

---

## Arquitetura

O projeto utiliza uma estrutura modular, com responsabilidades organizadas por camada:

```text
app/
├── main.py
├── core/
│   ├── audit.py
│   ├── config.py
│   ├── database.py
│   ├── rate_limit.py
│   ├── redis.py
│   └── security.py
├── models/
│   ├── membership.py
│   ├── organization.py
│   ├── project.py
│   ├── task.py
│   └── user.py
├── routes/
│   ├── auth.py
│   ├── memberships.py
│   ├── organizations.py
│   ├── projects.py
│   └── tasks.py
└── schemas/
    ├── auth.py
    ├── membership.py
    ├── organization.py
    ├── project.py
    ├── task.py
    └── user.py

migrations/
├── env.py
├── script.py.mako
└── versions/

tests/
├── auth/
├── memberships/
├── organizations/
├── projects/
├── tasks/
├── conftest.py
├── factories.py
├── markers.py
└── test_health.py
```

### Decisões de projeto

- Separação entre schemas da API e models de persistência.
- JWT para autenticação de rotas protegidas.
- Redis para rate limiting.
- Alembic para controle de versões do banco de dados.
- Eventos de auditoria executados em background, evitando bloquear a resposta principal.
- Testes separados por domínio funcional.

---

## Tecnologias

| Categoria | Tecnologias |
|---|---|
| Linguagem | Python |
| Framework | FastAPI, Starlette, Uvicorn |
| Validação e configuração | Pydantic, Pydantic Settings |
| Banco e ORM | SQLModel, SQLAlchemy 2, Alembic |
| Banco de dados | SQLite e PostgreSQL |
| Segurança | python-jose, passlib, argon2-cffi, OAuth2 Password Form |
| Cache e limitação | Redis |
| Testes | Pytest, pytest-cov, httpx |
| Infraestrutura | Docker, Docker Compose |

---

## Como executar localmente

### Pré-requisitos

- Python 3.10 ou superior.
- Redis em execução.
- PostgreSQL para ambiente de produção ou SQLite para desenvolvimento.
- Docker e Docker Compose são opcionais.

### 1. Clonar o repositório

```bash
git clone [https://github.com/HighOffGrid/TeamHub-Saas.git](https://github.com/HighOffGrid/TeamHub-Saas.git)
cd TeamHub-Saas
```

### 2. Criar e ativar ambiente virtual

**Windows**

```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Criar o arquivo de ambiente

Crie um arquivo chamado `.env` na raiz do projeto:

```env
APP_ENV=development
PROJECT_NAME=TeamHub SaaS
VERSION=1.0.0
SECRET_KEY=troque-por-uma-chave-forte
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
```

> O arquivo `.env` deve permanecer apenas na sua máquina e nunca deve ser enviado para o GitHub.

### 5. Aplicar migrations

```bash
alembic upgrade head
```

### 6. Iniciar a aplicação

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Docker

O repositório inclui `docker-compose.yml` para facilitar a execução de serviços dependentes, como banco de dados e Redis.

```bash
docker compose up --build
```

Para encerrar os serviços:

```bash
docker compose down
```

---

## Autenticação

O projeto usa o fluxo OAuth2 Password Form com JWT bearer token para autenticação.

### Registro

```http
POST /api/v1/auth/register
Content-Type: application/json
```

```json
{
  "name": "Test User",
  "email": "user@example.com",
  "password": "12345678"
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

```text
username=user@example.com&password=12345678
```

### Resposta

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### Rotas protegidas

Envie o token no cabeçalho:

```http
Authorization: Bearer <jwt>
```

A documentação completa dos endpoints está disponível no Swagger em `/docs`.

---

## Migrations

O projeto usa Alembic para versionamento do schema do banco de dados.

```bash
alembic revision --autogenerate -m "descricao_da_migration"
alembic upgrade head
alembic downgrade -1
```

---

## Testes

Executar a suíte completa:

```bash
pytest -q
```

Executar testes com relatório de cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```

Executar testes por domínio:

```bash
pytest tests/auth -q
pytest tests/projects -q
pytest tests/tasks -q
```

---

## Segurança

- Senhas protegidas por hash seguro.
- Autenticação com JWT em rotas protegidas.
- Validação de dados de entrada e saída com Pydantic.
- Rate limiting com Redis para reduzir abuso em endpoints sensíveis.
- Variáveis de ambiente para configurações e segredos.
- Eventos de auditoria para ações relevantes de autenticação.
- Arquivos de log gerados localmente não são versionados.

---

## Próximos passos

- Configurar CI com GitHub Actions para executar a suíte de testes a cada push.
- Publicar a API em ambiente de deploy com PostgreSQL e Redis.
- Criar um `.env.example` sem segredos para facilitar a configuração local.
- Revisar os endpoints com base no OWASP API Security Top 10.
