# Marmitas do Ben (MVP) — instruções para o Claude

## Papel
Atue como Software Architect + Technical Mentor. Estou aprendendo arquitetura enquanto construo. Arquitetura simples, coerente e evolutiva, sem remendos que só funcionem para o teste atual.

## Início de cada sessão
1. A FONTE DA VERDADE É O CÓDIGO, não este arquivo. Antes de propor código, leia os arquivos relevantes e rode `git --no-pager log -8 --oneline` e `git --no-pager status -sb`.
2. Compare com a seção "Onde paramos" abaixo e me diga em 2-3 linhas o estado real e qual é o próximo passo. Não escreva código ainda.
3. Ao fim de cada passo concluído, atualize a seção "Onde paramos" (e regras/fluxo na hora em que mudarem), SEM commitar.
4. No fim da sessão: um único commit `docs: atualiza CLAUDE.md (...)` e, se eu quiser, o push.

## Como trabalhar comigo
- Um passo por vez. Mande SÓ o próximo passo e espere eu confirmar antes do seguinte. Nunca encadeie passos.
- Comandos exatos para Windows PowerShell (bloco copiável). Git sempre com `git --no-pager ...`.
- Fluxo (decidido em 18/11/2026): o Claude edita os arquivos, roda os comandos e faz os commits; eu supervisiono e dou OK em cada passo.
  - Cada passo: explicar o que vai fazer e por quê -> editar -> mostrar o diff -> eu testo/confiro e dou OK -> commit.
  - Comandos que exigem um terminal ocupado (Uvicorn) ou ferramentas fora do PATH (Beekeeper/SQL) continuam comigo: me passe o comando/SQL exato.
  - Push só quando eu pedir.
  - `main.py` tem acentos (UTF-8): salvar como UTF-8, não mexer nas linhas antigas.
  - `services/assinatura.py`: escrever SEM acentos (comentários e textos).
- Explique brevemente o POR QUÊ e onde fica cada responsabilidade, sem aula teórica. Se eu perguntar "qual comando eu rodo?", responda direto.
- Mudanças pequenas e incrementais. Preservar o que funciona. Testar cada etapa antes de avançar.
- Não invente campos que não existem no banco. Regra de negócio não definida: pergunte antes.
- Quando eu mandar um erro: (1) interprete, (2) causa provável, (3) o que verificar, (4) só então proponha alteração.
- Depois de editar, conferir com `git --no-pager diff` antes do commit (acréscimo = só linhas "+").
- Commits pequenos, arquivo por arquivo (nunca `git add .`), um commit por mudança independente. Mensagens no padrão `feat: ...` / `docs: ...` em português. Commit só depois do meu OK; push só quando eu pedir.
- Não recomece o projeto nem troque a arquitetura.

## Ambiente
- Windows, PowerShell, Python 3.14. Raiz: `C:\Users\eduet\OneDrive\Documentos\Marmitas_do_Ben`
- Venv: `backend\venv`. GitHub: eduetche-source/Marmitas_do_Ben (branch main).
- Dependências (`backend/requirements.txt`): fastapi 0.110.0, uvicorn 0.28.0, SQLAlchemy 2.1.1, psycopg2-binary 2.9.13, python-dotenv 1.2.4, pydantic 2.13.5 (Pydantic v2: `ConfigDict(from_attributes=True)` nos schemas de saída).
- Subir o servidor (a partir de `backend`, NÃO de `app`):
  ```powershell
  cd C:\Users\eduet\OneDrive\Documentos\Marmitas_do_Ben\backend
  venv\Scripts\activate
  uvicorn app.main:app --reload --reload-dir app
  ```
- O Uvicorn ocupa o terminal; uso um segundo terminal para Git etc. Nele é preciso ativar o venv antes de `python -c ...` (senão "No module named 'fastapi'"). `python -c` só funciona de dentro de `backend`.
- Swagger: http://127.0.0.1:8000/docs (F5 após mudanças; abrir o bloco certo da rota).
- Banco: PostgreSQL `marmitas_db`, conexão via `DATABASE_URL` em `backend/.env` (no .gitignore).
- Uso o Beekeeper Studio; `psql` NÃO está no PATH. Passe SQL para eu colar (o Run só mostra o resultado da ÚLTIMA consulta; para ver várias, uma por vez).
- O `--reload` do Uvicorn às vezes TRAVA no Windows quando vários arquivos mudam em sequência (log mostra "Reloading..." sem "Started server process" depois) e o processo antigo segue servindo código velho. Antes de pedir teste, conferir no log que o reload terminou; se travou, reiniciar o servidor. Causa provável: conexão aberta do Swagger no navegador. Prática adotada: deixar o servidor DESLIGADO durante as edições e subir um novo só na hora dos testes.
- Ignorar avisos "LF will be replaced by CRLF". BOM na linha 1 de .py aparecendo como "-/+" no diff é inofensivo.

## Estrutura
```
database/   init.sql, seeds.sql, 002_compras_assinatura.sql, 003_status_pagamento_compras.sql
backend/app/
  database.py   engine, SessionLocal, Base, get_db
  main.py       rotas
  models/       produto.py (Produto, PedidoAvulso, ItemPedidoAvulso), cliente.py, assinatura.py (Assinatura, EscolhaAssinante, CompraAssinatura)
  schemas/      pedido.py, assinatura.py
  services/     cronograma.py, assinatura.py, pedido.py
```
- Não existe `__init__.py` (pacotes de namespace): não criar.
- Imports RELATIVOS sempre (`from .models.cliente import Cliente` no main; `from ..database import Base` em models/schemas/services; `from .cronograma import ...` entre services). Nunca `from app...`.

## Arquitetura
routes (main.py) -> schemas -> services -> models/database
- routes: HTTP, status codes, Depends, HTTPException. Rotas finas.
- schemas: validação de entrada/saída (Pydantic).
- models: mapeamento do banco e relacionamentos.
- services: regras de negócio. Não conhecem HTTP: levantam exceções de domínio e o main.py traduz em HTTPException.
- NÃO usar `Base.metadata.create_all()`. O banco já existe; SQLAlchemy é só ORM. Alembic fica para o futuro.
- Mudança de banco: primeiro o SQL (arquivo novo em `database/`, padrão `00N_*.sql`, re-executável com IF NOT EXISTS), depois o model espelhando o SQL.

## Banco
Tabelas: produtos, clientes, pedidos_avulsos, itens_pedido_avulso, assinaturas, escolhas_assinante, compras_assinatura.
- **assinaturas**: id, cliente_id (INT NOT NULL UNIQUE, FK clientes ON DELETE CASCADE), plano_marmitas INT NOT NULL, saldo_restante INT NOT NULL, status VARCHAR(20) NOT NULL DEFAULT 'Pendente', data_inicio TIMESTAMP. Um cliente tem no máximo UMA assinatura; renovar NÃO cria outra: gera uma compra, e o saldo é creditado na mesma linha quando o pagamento é confirmado.
- **escolhas_assinante**: id, cliente_id (FK clientes ON DELETE CASCADE), produto_id (FK produtos, sem ondelete), quantidade INT NOT NULL DEFAULT 1, data_escolha. NÃO tem assinatura_id/status/ciclo/data de entrega. Relação com assinatura é indireta via cliente_id: NÃO criar relacionamento direto Assinatura -> EscolhaAssinante.
- **compras_assinatura**: id, cliente_id (FK ON DELETE CASCADE), plano_marmitas, data_compra, status_pagamento ('Pendente' | 'Paga' | 'Cancelada', adicionada em `003_status_pagamento_compras.sql`). Uma linha por compra de plano (inicial e cada renovação). No máximo UMA compra Pendente por cliente (índice único parcial). Pagamento continua manual: eu confirmo pela API.
- Produtos (todos ativos): ids 1-4 = ciclo 1, ids 5-8 = ciclo 2.

## Regras de negócio
1. Planos: 12, 16, 20 ou 24 marmitas (validados no schema).
2. Status da assinatura: Pendente (1ª compra ainda não paga), Ativa, Encerrada. Muda pelas rotas de confirmar pagamento / cancelar compra (regra 7), não mais à mão no banco. Só Ativa escolhe marmitas.
3. Saldo descontado na escolha; recusar se quantidade > saldo. Saldo 0 não encerra sozinho.
4. Escolhas sem limite semanal, só o saldo manda. Produto precisa estar ativo e no ciclo atual.
5. Pedido avulso segue o MESMO cardápio: só aceita produto ativo e do ciclo atual (confirmado em 18/11/2026).
6. Ciclo (services/cronograma.py): semana ISO, paridade, fuso America/Sao_Paulo; seg-qui = ciclo da semana atual, sex-dom = da seguinte.
7. SALDO SÓ ENTRA QUANDO O PAGAMENTO É CONFIRMADO (decidido em 18/11/2026; substitui a regra antiga em que a renovação somava o saldo e voltava para Pendente). Motivo: cliente que renova e não paga não pode ganhar marmitas, nem perder as sobras já pagas.
   | Ação | Compra | Saldo | Status da assinatura |
   |---|---|---|---|
   | Contratar (1ª vez) | nova, Pendente | 0 | Pendente |
   | Renovar | nova, Pendente | não muda | não muda (Ativa continua escolhendo) |
   | Confirmar pagamento | Pendente -> Paga | + plano | -> Ativa; plano_marmitas = plano pago |
   | Cancelar compra | Pendente -> Cancelada | não muda | não muda; se a assinatura era Pendente (1ª compra) -> Encerrada |
   - Renovar com compra Pendente em aberto -> 409. Cliente inexistente ou sem assinatura -> 404.
   - Confirmar/cancelar sem compra Pendente -> 409.
   - Compras anteriores a esta regra foram marcadas como Paga (o saldo delas já tinha sido somado).
8. Mapeamento de erros: 404 cliente/assinatura/produto inexistente; 409 conflito de estado (assinatura não Ativa ao escolher; já existe compra Pendente ao renovar; não há compra Pendente ao confirmar/cancelar; cliente já tem assinatura); 422 produto inativo/fora do ciclo; 422 quantidade > saldo; 422 dados inválidos (Pydantic).

## O que já funciona (testado no Swagger) — NÃO quebrar
- `GET /` -> Online
- `GET /marmitas-ativas` -> produtos ativos do ciclo atual
- `POST /pedidos` -> 201, Pendente, frete fixo 10.00, previsão de entrega. Corpo: `{"cliente_id": 1, "itens": [{"produto_id": N, "quantidade": 2}]}` com N do ciclo ATUAL (ver GET /marmitas-ativas). Erros: 404 cliente; 404 produto; 422 produto inativo/fora do ciclo. Item inválido recusa o pedido inteiro (nada é gravado). Lógica em `services/pedido.py`.
- `POST /assinaturas` -> `{"cliente_id": N, "plano_marmitas": 12}`. 201 Pendente com saldo 0 + compra Pendente; 409 já tem; 404 cliente; 422 plano.
- `POST /assinaturas/{cliente_id}/escolhas` -> `{"produto_id": N, "quantidade": N}`. 201 com `{"escolha": {...}, "saldo_restante": N}`. Funciona também com renovação Pendente em aberto (usa as sobras). Erros conforme regra 8; nenhum erro desconta saldo.
- `POST /assinaturas/{cliente_id}/renovacoes` -> `{"plano_marmitas": 12}`. 201 com a COMPRA Pendente (saldo/status não mudam); 409 se já há compra Pendente; 404 cliente/assinatura; 422 plano.
- `POST /assinaturas/{cliente_id}/confirmar-pagamento` (sem corpo) -> 200 com a assinatura: compra Paga, saldo += plano, plano atualizado, Ativa (também reativa Encerrada). 409 sem compra Pendente; 404.
- `POST /assinaturas/{cliente_id}/cancelar-compra` (sem corpo) -> 200 com a assinatura: compra Cancelada, saldo intacto; 1ª compra (Pendente) -> Encerrada. 409 sem compra Pendente; 404.
- `GET /assinaturas/{cliente_id}` -> 200 `{"assinatura": {...}, "compra_pendente": {...} | null}`; 404 cliente/assinatura.
- Rotas de confirmar/cancelar são de ADMIN e ainda não têm login (ver pendência de segurança).

## Onde paramos (atualizado em 19/11/2026)
RESUMO: blocos 14 a 17 CONCLUÍDOS e testados. Próximo: bloco 18 (rotas GET). Detalhes de cada passo antigo estão no `git log`.

Histórico curto:
- Bloco 14 (renovação) e 15 (push): 18/11.
- Bloco 16 (POST /pedidos): lógica movida para `services/pedido.py`; valida cliente (404) e cardápio atual (422).
- Bloco 17 (pagamento das compras, regra 7): coluna `status_pagamento` (SQL 003), contratar com saldo 0, renovar só cria compra Pendente, rotas confirmar-pagamento e cancelar-compra (compartilham `_buscar_compra_pendente`). Testes finais 17g OK em 19/11: Encerrada renova e volta Ativa ao confirmar; escolha funciona com renovação em aberto; POST /pedidos 201. Clientes 2 e 3 (sobra do modelo antigo) marcados como Ativa no banco em 19/11.

Roteiro combinado (18/11/2026), nesta ordem:
1. ~~Terminar o bloco 17.~~ (feito em 19/11)
2. **Bloco 18 (EM ANDAMENTO): rotas GET** (as 4 aprovadas em 19/11):
   - **18a (feito, 394ada8 + 14441d0, testado):** `GET /assinaturas/{cliente_id}` -> `{"assinatura": {...}, "compra_pendente": {...} | null}`. Service `consultar_assinatura` (só leitura). Extraído `_consultar_compra_pendente`, usado também por renovar e `_buscar_compra_pendente` (renovar/confirmar retestados).
   - **18b (PRÓXIMO):** `GET /assinaturas/{cliente_id}/compras` — histórico de compras do cliente.
   - **18c:** `GET /compras-pendentes` — todas as compras aguardando pagamento (admin).
   - **18d:** `GET /producao-da-semana` — soma de escolhas + pedidos avulsos por produto. ANTES: decidir comigo o que conta como "semana" (ex.: feitos de sexta a quinta, entregues na segunda seguinte).
3. Frontend começando pela parte do CLIENTE (cardápio da semana + fazer pedido), que não precisa de login. Decidir tecnologia comigo (HTML/JS simples ou React).
4. Painel de admin junto com o login.
- Pendência de segurança (OBRIGATÓRIA antes de publicar na internet): rotas de admin (confirmar/cancelar) não têm login.
- Talvez: rota para encerrar assinatura Ativa (Ativa -> Encerrada), se eu quiser.
- Talvez: rota para cadastrar cliente (hoje só direto no banco).
- Limpeza opcional: import `calcular_data_entrega_pedido` sem uso no main.py.

Dados de teste em 19/11/2026 (conferir no banco): todas as assinaturas Ativa — cliente 1 = plano 20, saldo 52; cliente 2 = plano 12, saldo 24 (renovou e pagou no teste do 18a); cliente 3 = plano 20, saldo 32; cliente 4 ("Cliente Teste 4", criado direto no banco) = plano 12, saldo 12. compras_assinatura: 11 linhas, nenhuma Pendente.

## Pendências conhecidas (NÃO mexer sem eu pedir)
1. `database/init.sql` desatualizado: falta coluna `ciclo_cardapio` em produtos; `produtos.ativo` DEFAULT FALSE no SQL vs default=True no modelo. Resolver com SQL complementar (padrão 00N_*.sql).
2. (Resolvida em 18/11/2026: POST /pedidos valida cliente -> 404.)
3. `PedidoAvulso.cliente_id` sem ondelete e `Cliente.pedidos_avulsos` sem cascade (SQL tem ON DELETE CASCADE). Sem efeito hoje.
4. Estética: arquivos sem newline no fim. (Os espaços sobrando após `db.add(nova)` saíram no 17c.)
5. Pagamento no site: estender compras_assinatura quando existir.
6. Dados de teste inconsistentes (cliente 2 plano 16 saldo 12). Sem efeito.
7. Exceções comuns repetidas entre services (cliente/produto não encontrado). Hoje as de pedido levam prefixo `Pedido` para não colidir com as de assinatura. Futuro: juntar num `services/erros.py`.
8. Ideia (não pedida ainda): "modo cardápio completo" para liberar os dois ciclos numa semana especial, via configuração, sem mexer em `ciclo_cardapio`.
