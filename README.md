# TeamHub SaaS API

API backend para uma plataforma SaaS colaborativa, desenvolvida com FastAPI, com suporte a autenticação JWT, organizações, memberships, projetos, tarefas, rate limiting com Redis, auditoria de eventos e estrutura preparada para evolução contínua.

---

## Sobre o projeto

O TeamHub SaaS API é o backend de uma aplicação voltada para colaboração entre equipes e gestão de trabalho em ambientes organizacionais. O projeto foi estruturado para atender cenários comuns de produtos SaaS, como autenticação de usuários, organização por times ou empresas, gerenciamento de projetos e acompanhamento de tarefas.

A aplicação segue uma abordagem modular, com separação entre rotas, schemas, models e componentes centrais de infraestrutura. Esse desenho facilita a manutenção do código, melhora a legibilidade do domínio e reduz o acoplamento entre regras de negócio e detalhes de implementação.

Além das funcionalidades de domínio, o projeto também incorpora preocupações técnicas relevantes para sistemas reais, como emissão de JWT, hash seguro de senha, rate limiting com Redis, tarefas em background, auditoria de eventos e suporte a migrations versionadas.

---

## Principais funcionalidades
- Cadastro de usuários.
- Login com autenticação JWT.
- Hash seguro de senha com suporte a bibliotecas apropriadas para proteção de credenciais.
- Gestão de organizações.
- Gestão de memberships entre usuários e organizações.
- Gestão de projetos.
- Gestão de tarefas.
- Rate limiting em endpoints sensíveis.
- Registro de eventos com BackgroundTasks.
- Configuração por variáveis de ambiente.
- Base preparada para múltiplos ambientes e evolução de infraestrutura.

---

## Arquitetura da aplicação

A API foi organizada com foco em clareza estrutural e crescimento progressivo do domínio. O FastAPI oferece tipagem, documentação automática, injeção de dependências e integração natural com validação de dados, o que favorece a construção de APIs modulares e consistentes.

A modelagem usa SQLModel sobre SQLAlchemy, combinando ergonomia de declaração com recursos tradicionais de ORM e consultas relacionais. Para autenticação, o projeto segue o fluxo de OAuth2 Password Form com bearer token, padrão amplamente usado em aplicações FastAPI que trabalham com JWT.

---

## Stack e dependências

Backend e API

- FastAPI
- Starlette
- Uvicorn
- Pydantic
- Pydantic Settings


## Persistência e banco de dados

- SQLModel
- SQLAlchemy 2
- Alembic
- Psycopg / Psycopg Binary
- SQLite e/ou PostgreSQL, conforme ambiente


## Segurança e autenticação

- python-jose
- passlib
- argon2-cffi
- python-multipart
- email-validator


## Cache e recursos operacionais

- Redis
- BackgroundTasks do FastAPI


## Testes e qualidade

- Pytest
- pytest-cov
- coverage
- httpx

---

## Estrutura do projeto
```
teamh/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── audit.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── rate_limit.py
│   │   ├── redis.py
│   │   └── security.py
│   ├── models/
│   │   ├── membership.py
│   │   ├── organization.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── user.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── memberships.py
│   │   ├── organizations.py
│   │   ├── projects.py
│   │   └── tasks.py
│   └── schemas/
│       ├── auth.py
│       ├── membership.py
│       ├── organization.py
│       ├── project.py
│       ├── task.py
│       └── user.py
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── factories.py
│   ├── markers.py
│   ├── test_health.py
│   ├── auth/
│   │   ├── helpers.py
│   │   ├── test_auth_login.py
│   │   ├── test_auth_me.py
│   │   └── test_auth_register.py
│   ├── memberships/
│   │   └── test_memberships.py
│   ├── organizations/
│   │   └── test_organizations.py
│   ├── projects/
│   │   ├── test_projects.py
│   │   └── test_projects_rbac.py
│   └── tasks/
│       ├── conftest.py
│       └── test_task.py
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```
Essa estrutura representa melhor a organização atual do projeto, incluindo aplicação principal, migrations versionadas com Alembic e uma suíte de testes separada por domínio. Essa divisão melhora manutenção, testabilidade e previsibilidade do código em projetos FastAPI estruturados por módulos.

---

## Configuração do ambiente

Exemplo de arquivo .env:
```
APP_ENV=development
PROJECT_NAME=TeamHub SaaS
VERSION=1.0.0
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
```
Em ambientes de produção, recomenda-se utilizar PostgreSQL, chaves seguras, segregação de configuração por ambiente e serviços externos gerenciados para banco e cache.

---

## Como executar localmente

1. Clonar o repositório
```
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```
2. Criar e ativar o ambiente virtual

No Windows:
```
python -m venv venv
venv\Scriptsctivate
```

No Linux/macOS:
```
python -m venv venv
source venv/bin/activate
```
3. Instalar as dependências
```
pip install -r requirements.txt
```
4. Configurar as variáveis de ambiente
Crie um arquivo .env com as configurações da aplicação e dos serviços auxiliares.

5. Executar a aplicação
```
uvicorn app.main:app --reload
```
6. Acessar a documentação interativa
```
• http://127.0.0.1:8000/docs
• http://127.0.0.1:8000/redoc
```
---

## Fluxo de autenticação

O login segue o padrão OAuth2PasswordRequestForm, no qual o cliente envia username e password como formulário, e a API retorna um token JWT do tipo bearer. Esse fluxo é compatível com a abordagem oficial recomendada pelo FastAPI para autenticação baseada em token.

### Registro
```
POST /api/v1/auth/register
Content-Type: application/json
```
### Exemplo de payload:
```
{
  "name": "Test User",
  "email": "user@example.com",
  "password": "12345678"
}
```
### Login
```
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```
### Exemplo de payload:
```
username=user@example.com&password=12345678
```
### Exemplo de resposta:
```
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```
### Autorização em rotas protegidas
```
Authorization: Bearer <jwt>
```
## Migrações

O projeto utiliza Alembic para versionamento de schema e controle de mudanças estruturais no banco de dados. Essa abordagem é importante para manter consistência entre ambientes e garantir evolução segura do schema ao longo do desenvolvimento.

### Comandos comuns:
```
pytest -q
alembic revision --autogenerate -m "descricao_da_migration"
alembic upgrade head
alembic downgrade -1
```
## Testes 

### Execução completa da suíte:
```
pytest -q
```
### Execução com cobertura:
```
pytest --cov=app --cov-report=term-missing
```
### Execução por módulo:
```
pytest tests/auth -q
pytest tests/projects -q
pytest tests/tasks -q
```
O uso de Pytest combinado com httpx e TestClient é amplamente adotado para validação de endpoints FastAPI e fluxos autenticados.

---

## Qualidade e segurança

O projeto foi construído com foco em fundamentos importantes para APIs reais. Entre eles estão a validação tipada de entrada e saída, o uso de hash seguro para credenciais, a proteção de rotas por bearer token e a separação entre o schema exposto via API e os models de persistência.

A presença de rate limiting com Redis reforça a proteção de endpoints sensíveis, especialmente login e registro. O uso de BackgroundTasks permite registrar eventos ou executar tarefas leves após a resposta, sem bloquear desnecessariamente o fluxo principal da requisição
