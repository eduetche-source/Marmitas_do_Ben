# 🍱 Projeto Marmitas do Ben - MVP

Este é o diário de bordo e documentação do MVP do sistema de marmitas congeladas (venda avulsa e assinaturas).

---

## 📌 Onde o Projeto Parou? (Para passar para o próximo Agente)

Se for iniciar um novo chat com uma IA, **copie e cole o texto abaixo integralmente** na primeira mensagem para continuar de onde paramos:

---

Quero continuar o desenvolvimento do meu projeto "Marmitas do Ben (MVP)".

IMPORTANTE:
Quero que você atue como meu Software Architect + Technical Mentor.
Estou desenvolvendo o projeto passo a passo e quero uma arquitetura coerente, simples e evolutiva, sem "remendos" ou soluções que funcionem apenas para o teste atual.

Prefiro:
- explicações claras e práticas;
- comandos exatos para Windows quando necessário;
- mudanças incrementais;
- preservar o que já está funcionando;
- não criar complexidade desnecessária;
- antes de alterar arquivos, entender como as partes se relacionam;
- testar cada etapa antes de avançar.

==================================================
STACK ATUAL
==================================================

Backend:
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Uvicorn

Sistema:
- Windows
- Python 3.14
- ambiente virtual em:
  C:\Users\eduet\OneDrive\Documentos\Marmitas_do_Ben\backend\venv

Projeto:
C:\Users\eduet\OneDrive\Documentos\Marmitas_do_Ben\backend\app

Para iniciar atualmente:
cd C:\Users\eduet\OneDrive\Documentos\Marmitas_do_Ben\backend\app
uvicorn main:app --reload

Servidor:
http://127.0.0.1:8000

Swagger:
http://127.0.0.1:8000/docs

Banco:
PostgreSQL
database: marmitas_db

==================================================
ESTRUTURA ATUAL
==================================================

backend/
└── app/
    ├── database.py
    ├── main.py
    ├── models/
    │   ├── produto.py
    │   ├── cliente.py
    │   └── assinatura.py
    ├── schemas/
    │   └── pedido.py
    └── services/
        └── cronograma.py

O backend já está iniciando normalmente com Uvicorn.

Último estado confirmado:

INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.

==================================================
BANCO DE DADOS
==================================================

Tabelas principais existentes:

1. produtos
2. clientes
3. pedidos_avulsos
4. itens_pedido_avulso
5. assinaturas
6. escolhas_assinante

Tabela clientes:

CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    whatsapp VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    rua VARCHAR(150) NOT NULL,
    numero VARCHAR(20) NOT NULL,
    bairro VARCHAR(50) NOT NULL,
    cidade VARCHAR(50) NOT NULL DEFAULT 'Porto Alegre',
    distancia_km DECIMAL(5, 2)
);

Tabela assinaturas:

CREATE TABLE IF NOT EXISTS assinaturas (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL UNIQUE, 
    plano_marmitas INT NOT NULL,    
    saldo_restante INT NOT NULL,    
    status VARCHAR(20) NOT NULL DEFAULT 'Pendente', 
    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cliente_assinatura
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE CASCADE
);

Tabela escolhas_assinante:

CREATE TABLE IF NOT EXISTS escolhas_assinante (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    data_escolha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cliente_escolha
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_produto_escolha
        FOREIGN KEY (produto_id)
        REFERENCES produtos(id)
);

IMPORTANTE:
A tabela escolhas_assinante NÃO possui assinatura_id.
A relação da escolha com a assinatura é indireta através de cliente_id.

Também é importante respeitar o fato de que assinaturas.cliente_id é UNIQUE:
um cliente pode ter no máximo uma assinatura nesse modelo atual.

==================================================
REGRAS DE NEGÓCIO JÁ IMPLEMENTADAS
==================================================

1. CICLO DE CARDÁPIO

GET /marmitas-ativas

Existe um serviço em:
services/cronograma.py

Ele calcula o ciclo usando:
- semana do ano;
- paridade da semana;
- timezone America/Sao_Paulo.

Regra:

Segunda a quinta:
→ mostra o ciclo da semana atual.

Sexta a domingo:
→ mostra o ciclo da semana seguinte.

O endpoint retorna somente produtos:
- ativos;
- pertencentes ao ciclo calculado.

==================================================
TESTE JÁ REALIZADO: GET /marmitas-ativas
==================================================

O endpoint foi testado pelo Swagger e funcionou.

Resultado:

{
  "ciclo_vendas_atual": 2,
  "total_produtos": 4,
  "produtos": [
    {
      "id": 5,
      "preco": 23.9,
      "ciclo_cardapio": 2,
      "descricao": "Almôndegas caseiras, acompanhadas de arroz integral com sementes e legumes refogados.",
      "nome": "Almôndegas com Arroz",
      "ativo": true
    },
    {
      "id": 6,
      "preco": 23.9,
      "ciclo_cardapio": 2,
      "descricao": "Frango ao molho teriyaki, acompanhado de arroz integral com sementes e legumes refogados.",
      "nome": "Frango Teriyaki",
      "ativo": true
    },
    {
      "id": 7,
      "preco": 23.9,
      "ciclo_cardapio": 2,
      "descricao": "Guisado perfeitamente temperado, acompanhado de purê de batata inglesa e legumes refogados.",
      "nome": "Guisado com Purê",
      "ativo": true
    },
    {
      "id": 8,
      "preco": 23.9,
      "ciclo_cardapio": 2,
      "descricao": "Delicioso escondidinho de aipim cremoso recheado com frango desfiado.",
      "nome": "Escondidinho de Frango",
      "ativo": true
    }
  ]
}

Esse teste passou.

==================================================
PEDIDOS AVULSOS
==================================================

POST /pedidos

Já está funcionando.

Teste realizado:

{
  "cliente_id": 1,
  "itens": [
    {
      "produto_id": 5,
      "quantidade": 2
    }
  ]
}

Resultado:

HTTP 201

{
  "mensagem": "Pedido realizado com sucesso!",
  "pedido_id": 3,
  "status_pagamento": "Pendente",
  "data_entrega_prevista": "2026-10-05",
  "total_itens": 1
}

Portanto:
- cliente foi encontrado;
- produto foi encontrado;
- pedido foi criado;
- item foi criado;
- status de pagamento ficou Pendente;
- previsão de entrega foi calculada;
- HTTP 201 está correto.

NÃO devemos quebrar esse fluxo enquanto implementamos assinaturas.

==================================================
MODELOS ATUAIS
==================================================

models/cliente.py:

from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    whatsapp = Column(String(20), nullable=False, unique=True, index=True)
    email = Column(String(100), unique=True, nullable=True)
    rua = Column(String(150), nullable=False)
    numero = Column(String(20), nullable=False)
    bairro = Column(String(50), nullable=False)
    cidade = Column(String(50), nullable=False, default="Porto Alegre")
    distancia_km = Column(Numeric(5, 2), nullable=True)

    assinatura = relationship(
        "Assinatura",
        back_populates="cliente",
        uselist=False
    )

    escolhas_assinante = relationship(
        "EscolhaAssinante",
        back_populates="cliente",
        cascade="all, delete-orphan"
    )

    pedidos_avulsos = relationship(
        "PedidoAvulso",
        back_populates="cliente"
    )


models/produto.py atualmente contém:

- Produto
- PedidoAvulso
- ItemPedidoAvulso

Modelo Produto possui relacionamentos com:
- ItemPedidoAvulso
- EscolhaAssinante

PedidoAvulso possui:
- cliente_id
- data_pedido
- valor_frete
- status_pagamento
- cliente
- itens

ItemPedidoAvulso possui:
- pedido_id
- produto_id
- quantidade
- pedido
- produto

IMPORTANTE:
Não assumir que o SQL físico de pedidos_avulsos possui exatamente a mesma FK que o modelo Python.
O SQL original completo de pedidos_avulsos não foi fornecido.
Se isso se tornar relevante, primeiro devemos verificar o banco físico.

==================================================
MODELO DE ASSINATURAS
==================================================

models/assinatura.py contém:

class Assinatura(Base):
    __tablename__ = "assinaturas"

    id
    cliente_id
    plano_marmitas
    saldo_restante
    status
    data_inicio

Relacionamento:
Assinatura -> Cliente

E:

class EscolhaAssinante(Base):
    __tablename__ = "escolhas_assinante"

    id
    cliente_id
    produto_id
    quantidade
    data_escolha

Relacionamentos:
EscolhaAssinante -> Cliente
EscolhaAssinante -> Produto

IMPORTANTE:
produto_id de EscolhaAssinante deve ser:

ForeignKey("produtos.id")

SEM ondelete="CASCADE", para refletir exatamente o SQL fornecido.

Também NÃO criar um relacionamento direto:
Assinatura -> EscolhaAssinante

porque a tabela escolhas_assinante não possui assinatura_id.

==================================================
MAIN.PY
==================================================

O main.py atualmente importa todos os modelos para que os relacionamentos string-based do SQLAlchemy sejam registrados:

from models.cliente import Cliente
from models.produto import Produto, PedidoAvulso, ItemPedidoAvulso
from models.assinatura import Assinatura, EscolhaAssinante

Também possui:

GET /
GET /marmitas-ativas
POST /pedidos

Não adicionar Base.metadata.create_all() neste momento.

O banco já existe e estamos tratando o SQLAlchemy como camada ORM, não como ferramenta de criação/migração do banco.

Alembic pode ser considerado futuramente, mas não agora.

==================================================
ARQUITETURA DESEJADA
==================================================

Queremos evoluir gradualmente para:

routes/main
    ↓
schemas
    ↓
services
    ↓
models / database

Responsabilidades:

routes:
- HTTP
- status codes
- Depends
- HTTPException

schemas:
- validação de entrada/saída

models:
- mapeamento do banco
- relacionamentos

services:
- regras de negócio
- cálculos
- fluxos de domínio

Não quero fazer uma grande refatoração de uma vez.

==================================================
PRÓXIMO PASSO
==================================================

O próximo módulo a implementar é:

ASSINATURAS RECORRENTES.

Ordem desejada:

1. Confirmar os modelos Assinatura e EscolhaAssinante.
2. Criar schemas Pydantic.
3. Criar endpoint para contratar uma assinatura.
4. Criar endpoint para escolher as marmitas da assinatura.
5. Definir como o saldo_restante será consumido.
6. Testar tudo pelo Swagger.
7. Só depois pensar em refatorar serviços/rotas se necessário.

Antes de escrever código:
- explique brevemente a decisão arquitetural;
- diga quais arquivos serão criados/alterados;
- faça mudanças pequenas;
- teste cada etapa;
- não invente campos que não existem no banco;
- se uma regra de negócio ainda não estiver definida, pergunte antes de implementá-la.

==================================================
ESTILO DE TRABALHO
==================================================

Estou aprendendo arquitetura de software enquanto construo o projeto.

Não quero apenas receber código pronto.
Quero entender:
- por que estamos fazendo cada mudança;
- onde cada responsabilidade deve ficar;
- como as tabelas se relacionam;
- por que determinada decisão é melhor para o MVP.

Mas não precisa transformar tudo em aula teórica.
Se eu perguntar "qual comando eu rodo?", responda diretamente com o comando.

Quando eu mandar um erro:
1. interprete o erro;
2. explique a causa provável;
3. diga exatamente o que verificar;
4. só então proponha alteração.

IMPORTANTE:
Não recomeçar o projeto.
Não substituir a arquitetura inteira.
Continuar exatamente do ponto em que estamos.

ESTADO ATUAL:
Backend funcionando.
GET /marmitas-ativas funcionando.
POST /pedidos funcionando com HTTP 201.
Modelos Cliente e Assinatura adicionados.
Uvicorn funcionando.
Swagger funcionando.

PRÓXIMA TAREFA:
Continuar a implementação do módulo de assinaturas recorrentes.