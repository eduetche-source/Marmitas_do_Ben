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
- **assinaturas**: id, cliente_id (INT NOT NULL UNIQUE, FK clientes ON DELETE CASCADE), plano_marmitas INT NOT NULL, saldo_restante INT NOT NULL, status VARCHAR(20) NOT NULL DEFAULT 'Pendente', data_inicio TIMESTAMP. Um cliente tem no máximo UMA assinatura; renovar credita saldo na mesma linha.
- **escolhas_assinante**: id, cliente_id (FK clientes ON DELETE CASCADE), produto_id (FK produtos, sem ondelete), quantidade INT NOT NULL DEFAULT 1, data_escolha. NÃO tem assinatura_id/status/ciclo/data de entrega. Relação com assinatura é indireta via cliente_id: NÃO criar relacionamento direto Assinatura -> EscolhaAssinante.
- **compras_assinatura**: id, cliente_id (FK ON DELETE CASCADE), plano_marmitas, data_compra, status_pagamento ('Pendente' | 'Paga' | 'Cancelada', adicionada em `003_status_pagamento_compras.sql`). Uma linha por compra de plano (inicial e cada renovação). No máximo UMA compra Pendente por cliente (índice único parcial). Pagamento continua manual: eu confirmo pela API.
- Produtos (todos ativos): ids 1-4 = ciclo 1, ids 5-8 = ciclo 2.

## Regras de negócio
1. Planos: 12, 16, 20 ou 24 marmitas (validados no schema).
2. Status: Pendente (aguardando pagamento), Ativa, Encerrada. Eu altero manualmente. Só Ativa escolhe marmitas.
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
8. Mapeamento de erros: 404 cliente/assinatura/produto inexistente; 409 assinatura não Ativa (ou Pendente na renovação); 422 produto inativo/fora do ciclo; 422 quantidade > saldo.

## O que já funciona (testado no Swagger) — NÃO quebrar
- `GET /` -> Online
- `GET /marmitas-ativas` -> produtos ativos do ciclo atual
- `POST /pedidos` -> 201, Pendente, frete fixo 10.00, previsão de entrega. Corpo: `{"cliente_id": 1, "itens": [{"produto_id": N, "quantidade": 2}]}` com N do ciclo ATUAL (ver GET /marmitas-ativas). Erros: 404 cliente; 404 produto; 422 produto inativo/fora do ciclo. Item inválido recusa o pedido inteiro (nada é gravado). Lógica em `services/pedido.py`.
- `POST /assinaturas` -> `{"cliente_id": N, "plano_marmitas": 12}`. 201 Pendente com saldo = plano; 409 já tem; 404 cliente; 422 plano. Grava compra inicial.
- `POST /assinaturas/{cliente_id}/escolhas` -> `{"produto_id": N, "quantidade": N}`. 201 com `{"escolha": {...}, "saldo_restante": N}`. Erros conforme regra 8; nenhum erro desconta saldo.

## Onde paramos (atualizado em 18/11/2026, fim da sessão)
RESUMO: bloco 17 quase pronto, falta só o 17g (testes finais + atualizar seções do CLAUDE.md). Commits da sessão de 18/11 ainda NÃO foram enviados ao GitHub (falta `git push`).

Concluído: services `contratar_assinatura`, `escolher_marmita`, `renovar_assinatura`; schema `RenovacaoCreateSchema`.
- **14c (feito, commit e898fe9):** rota `POST /assinaturas/{cliente_id}/renovacoes` no main.py (`criar_renovacao`).
- **14d (feito, 18/11/2026):** testado no Swagger. Ativa -> 201 (saldo somado, plano atualizado, linha nova em compras_assinatura); Encerrada -> 201; Pendente -> 409; cliente 999 -> 404; plano 10 -> 422; escolhas depois de renovar -> 409; POST /pedidos -> 201.

- **15 (feito):** push da sessão de 18/11.

Bloco atual: arrumar POST /pedidos (passos 16a-16d).
- **16a (feito, 3b26375):** `services/pedido.py` com `criar_pedido_avulso`, `ResultadoPedido`, exceções com prefixo `Pedido`.
- **16b (feito, a202ebd):** rota POST /pedidos usa o service (comportamento idêntico, testado).
- **16c (feito, e1fdea5 + 93c638e):** cliente inexistente -> 404 (testado).
- **16d (feito):** produto inativo ou fora do ciclo -> 422 (testado, inclusive pedido com item bom + item ruim não grava nada).
- Bloco 16 CONCLUÍDO.

Bloco atual: pagamento das compras de assinatura (regra 7). Passos:
- **17a (feito, c86d85d):** SQL `database/003_status_pagamento_compras.sql`, já executado no banco (5 compras antigas = Paga).
- **17b (feito, d6c4c1a):** model CompraAssinatura com status_pagamento.
- **17c (feito):** contratar_assinatura -> saldo 0, compra Pendente. Constantes COMPRA_PENDENTE/PAGA/CANCELADA em services/assinatura.py.
- **17d (feito):** renovar_assinatura só cria compra Pendente (CompraPendenteError -> 409, inclusive se o índice único barrar). Rota de renovação agora devolve a COMPRA (CompraResponseSchema). AssinaturaPendenteError foi substituída por CompraPendenteError.
- **17e (feito, testado):** `POST /assinaturas/{cliente_id}/confirmar-pagamento`, sem corpo, 200. Compra -> Paga; saldo += plano; plano_marmitas = plano; assinatura -> Ativa. Erros: 404 cliente/assinatura; 409 SemCompraPendenteError. Testado: renovar cliente 1 (compra Pendente, saldo intacto) -> confirmar (saldo 22 -> 34, Ativa) -> confirmar de novo 409 -> cliente 999 404.
- **17f (feito, 6fb35b0, testado):** `POST /assinaturas/{cliente_id}/cancelar-compra`, sem corpo, 200. Compra -> Cancelada; saldo não muda; assinatura Pendente (1ª compra) -> Encerrada; senão status não muda. Erros 404/409. Confirmar e cancelar compartilham `_buscar_compra_pendente` no service.
- **17g (PRÓXIMO):** testes que faltam: (a) renovar assinatura Encerrada (cliente 4) -> confirmar -> Ativa com saldo = plano; (b) escolher marmita com renovação Pendente em aberto (cliente 1 Ativa) -> 201, sobras continuam valendo; (c) reconfirmar a confirmação de pagamento após o refactor do `_buscar_compra_pendente`; (d) POST /pedidos 201. Depois, decidir comigo o que fazer com os clientes 2 e 3 (assinatura Pendente sem compra Pendente, sobra do modelo antigo: não conseguem ativar pela API). Então atualizar as seções "Regras" (2 e 8), "Banco" e "O que já funciona" para o modelo novo e fechar o bloco 17.
- Depois: rota para encerrar assinatura Ativa (Ativa -> Encerrada), se eu quiser.

Roteiro combinado (18/11/2026), nesta ordem:
1. Terminar o bloco 17.
2. Bloco de rotas GET: assinatura/saldo do cliente, compras pendentes, pedidos e escolhas da semana.
3. Frontend começando pela parte do CLIENTE (cardápio da semana + fazer pedido), que não precisa de login. Decidir tecnologia comigo (HTML/JS simples ou React).
4. Painel de admin junto com o login.
- Pendência de segurança (OBRIGATÓRIA antes de publicar na internet): rotas de admin (confirmar/cancelar) não têm login.
- Limpeza opcional: import `calcular_data_entrega_pedido` sem uso no main.py.

Dados de teste em 18/11/2026 16:50 (conferir no banco): cliente 1 = plano 12, saldo 34, Ativa; cliente 2 = plano 16, saldo 12, Pendente; cliente 3 = plano 20, saldo 32, Pendente; cliente 4 ("Cliente Teste 4", criado direto no banco) = plano 12, saldo 0, Encerrada. compras_assinatura: 8 linhas (ids 1-6 Paga, 7 e 8 Cancelada), nenhuma Pendente. Ainda não existe rota para cadastrar cliente.

## Pendências conhecidas (NÃO mexer sem eu pedir)
1. `database/init.sql` desatualizado: falta coluna `ciclo_cardapio` em produtos; `produtos.ativo` DEFAULT FALSE no SQL vs default=True no modelo. Resolver com SQL complementar (padrão 00N_*.sql).
2. (Resolvida em 18/11/2026: POST /pedidos valida cliente -> 404.)
3. `PedidoAvulso.cliente_id` sem ondelete e `Cliente.pedidos_avulsos` sem cascade (SQL tem ON DELETE CASCADE). Sem efeito hoje.
4. Estética: arquivos sem newline no fim. (Os espaços sobrando após `db.add(nova)` saíram no 17c.)
5. Pagamento no site: estender compras_assinatura quando existir.
6. Dados de teste inconsistentes (cliente 2 plano 16 saldo 12). Sem efeito.
7. Exceções comuns repetidas entre services (cliente/produto não encontrado). Hoje as de pedido levam prefixo `Pedido` para não colidir com as de assinatura. Futuro: juntar num `services/erros.py`.
8. Ideia (não pedida ainda): "modo cardápio completo" para liberar os dois ciclos numa semana especial, via configuração, sem mexer em `ciclo_cardapio`.
