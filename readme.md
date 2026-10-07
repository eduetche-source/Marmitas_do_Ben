# Marmitas do Ben (MVP)

API para venda de marmitas: cardápio rotativo por ciclo semanal, pedidos avulsos e (em desenvolvimento) assinaturas recorrentes.

## Stack

- Python 3.14
- FastAPI + Uvicorn
- SQLAlchemy (apenas como camada ORM; o banco já existe)
- PostgreSQL (database `marmitas_db`)

## Como rodar

1. Crie um arquivo `backend/.env` com a conexão do banco:

        DATABASE_URL=postgresql://usuario:senha@localhost:5432/marmitas_db

2. A partir da pasta `backend` (não de dentro de `app`):

        cd backend
        venv\Scripts\activate
        pip install -r requirements.txt
        uvicorn app.main:app --reload --reload-dir app

3. Documentação interativa (Swagger): http://127.0.0.1:8000/docs

O schema do banco está em `database/init.sql` e os dados de exemplo em `database/seeds.sql`.

## Estrutura

    backend/app/
    ├── main.py        rotas HTTP
    ├── database.py    engine, sessão e Base
    ├── models/        mapeamento das tabelas (SQLAlchemy)
    ├── schemas/       validação de entrada e saída (Pydantic)
    └── services/      regras de negócio

Fluxo da arquitetura: rotas -> schemas -> services -> models/database.

## Convenções

- Imports relativos em todo o projeto. Em `main.py`: `from .models.cliente import Cliente`. Em `models/`, `schemas/` e `services/`: `from ..database import Base`. Não usar `from app...`.
- Não usar `Base.metadata.create_all()`. O banco é criado pelos scripts em `database/`.

## Documentação interna

Material de trabalho com IA (contexto do projeto, prompts) fica em `docs/ia/`.
