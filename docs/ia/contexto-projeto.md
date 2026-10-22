Quero continuar o desenvolvimento do meu projeto "Marmitas do Ben (MVP)".

(Contexto atualizado em 22/10/2026, ao fim da sessão. Passos 11, 12, 13, 14a e 14b CONCLUÍDOS e commitados. Próximo: 14c, a rota de renovação.)

PAPEL
Atue como meu Software Architect + Technical Mentor. Estou aprendendo arquitetura enquanto construo. Quero uma arquitetura simples, coerente e evolutiva, sem remendos que só funcionem para o teste atual.

==================================================
COMO TRABALHAR COMIGO (MUITO IMPORTANTE)
==================================================
- Um passo por vez. Mande SÓ o próximo passo e espere eu confirmar que fiz antes de mandar outro. Nunca encadeie passos.
- Comandos exatos para Windows PowerShell. Posso copiar e colar o bloco inteiro.
- Para Git, use "git --no-pager ..." (a paginação do terminal me trava).
- O Uvicorn ocupa o terminal em que roda. Uso um segundo terminal para Git e outros comandos. ATENÇÃO: nesse segundo terminal é preciso ativar o venv (venv\Scripts\activate, dentro de backend) antes de rodar "python -c ...", senão dá "No module named 'fastapi'".
- EDIÇÃO DE ARQUIVOS: prefiro que você me dê o NOME DO ARQUIVO + o TRECHO EXATO para eu editar no editor (VS Code), em vez de reescrever arquivos por PowerShell. Para edições em main.py, lembre que ele tem acentos (UTF-8): salvar sempre como UTF-8 e não mexer nas linhas antigas. Em services/assinatura.py o padrão é escrever SEM acentos (comentários e textos).
- Explique brevemente o POR QUÊ de cada mudança e onde fica cada responsabilidade, sem virar aula teórica. Se eu perguntar "qual comando eu rodo?", responda direto.
- Mudanças pequenas e incrementais. Preservar o que já funciona. Testar cada etapa antes de avançar.
- Não invente campos que não existem no banco. Se uma regra de negócio não estiver definida, pergunte antes de implementar.
- Quando eu mandar um erro: (1) interprete, (2) explique a causa provável, (3) diga exatamente o que verificar, (4) só então proponha alteração.
- Peça o diff/arquivo real quando precisar. Depois de editar um arquivo, confira com "git --no-pager diff" antes do commit (esperado: só linhas "+" quando for acréscimo).
- Commits pequenos, adicionando arquivo por arquivo (nunca "git add ."). Um commit por mudança independente.
- Não recomece o projeto nem troque a arquitetura.

LIÇÃO APRENDIDA: resumos de contexto ficam desatualizados. A FONTE DA VERDADE É O CÓDIGO NO REPOSITÓRIO, não este texto. Antes de escrever qualquer código, confira o repositório ou peça que eu cole os arquivos relevantes (ou rode "git --no-pager log -5 --oneline" e "git --no-pager status -s").

==================================================
REPOSITÓRIO E AMBIENTE
==================================================
GitHub: https://github.com/eduetche-source/Marmitas_do_Ben (branch main)
Commits locais (mais recente primeiro):
  f8b966b feat: adiciona schema RenovacaoCreateSchema          <- 14b
  2a8beb8 feat: adiciona service renovar_assinatura (soma saldo, volta para Pendente e grava historico)   <- 14a
  73be7c2 feat: adiciona rota POST /assinaturas/{cliente_id}/escolhas   <- 12b (inclui limpeza de espaços em branco em /marmitas-ativas e /pedidos)
  2a872b8 feat: adiciona schema EscolhaRealizadaSchema (escolha com saldo restante)
  c5d2c94 feat: escolher_marmita devolve o saldo restante junto com a escolha
  9450207 feat: adiciona service escolher_marmita com consumo de saldo
  7d558bd feat(db): adiciona script da tabela compras_assinatura   <- este é o origin/main
Todos os commits acima de 7d558bd estão SÓ NO MEU COMPUTADOR: falta "git push".
Alteração não commitada: docs/ia/contexto-projeto.md (este arquivo, a substituir pela versão nova e commitar em commit separado, tipo "docs: atualiza contexto").

Sistema: Windows, PowerShell, Python 3.14
Raiz do projeto: C:\Users\eduet\OneDrive\Documentos\Marmitas_do_Ben
Venv: C:\Users\eduet\OneDrive\Documentos\Marmitas_do_Ben\backend\venv
Dependências (backend/requirements.txt): fastapi 0.110.0, uvicorn 0.28.0, SQLAlchemy 2.1.1, psycopg2-binary 2.9.13, python-dotenv 1.2.4, pydantic 2.13.5 (Pydantic v2: usar ConfigDict(from_attributes=True) nos schemas de saída).

COMO SUBIR O SERVIDOR (a partir de backend, NÃO de dentro de app):
  cd C:\Users\eduet\OneDrive\Documentos\Marmitas_do_Ben\backend
  venv\Scripts\activate
  uvicorn app.main:app --reload --reload-dir app

Testes rápidos em Python ("python -c ...") só funcionam rodando de dentro de backend e com o venv ativo.
Swagger: http://127.0.0.1:8000/docs (dar F5 após mudanças; cuidado para abrir o bloco certo da rota, por exemplo /assinaturas vs /assinaturas/{cliente_id}/escolhas).
Banco: PostgreSQL, database marmitas_db. Conexão via DATABASE_URL em backend/.env (no .gitignore).
Uso o BEEKEEPER STUDIO para o banco. O "psql" NÃO está no PATH: passe SQL para eu colar no Beekeeper (Run executa o script inteiro, mas só mostra o resultado da ÚLTIMA consulta; para ver várias, rode uma por vez).
Avisos "LF will be replaced by CRLF" do Git: ignorar. Um BOM invisível na linha 1 de arquivos .py aparece no diff como "-/+" da mesma linha: inofensivo.

==================================================
ESTRUTURA
==================================================
Marmitas_do_Ben/
├── .gitignore
├── readme.md
├── database/ init.sql, seeds.sql, 002_compras_assinatura.sql
├── docs/ia/contexto-projeto.md      (este arquivo)
└── backend/
    ├── requirements.txt
    ├── venv/
    └── app/
        ├── database.py        (engine, SessionLocal, Base, get_db)
        ├── main.py            (rotas)
        ├── models/  produto.py (Produto, PedidoAvulso, ItemPedidoAvulso), cliente.py, assinatura.py (Assinatura, EscolhaAssinante, CompraAssinatura)
        ├── schemas/ pedido.py, assinatura.py
        └── services/ cronograma.py, assinatura.py

Não existe nenhum __init__.py (pacotes de namespace): não criar.
REGRA DE IMPORTS: imports RELATIVOS (em main.py: from .models.cliente import Cliente; em models/schemas/services: from ..database import Base; entre services: from .cronograma import ...). Não misturar com "from app...".

==================================================
ARQUITETURA DESEJADA
==================================================
routes/main -> schemas -> services -> models/database
- routes (main.py): HTTP, status codes, Depends, HTTPException. Rotas finas.
- schemas: validação de entrada/saída (Pydantic)
- models: mapeamento do banco e relacionamentos
- services: regras de negócio. Não conhecem HTTP: levantam exceções de domínio e o main.py as converte em HTTPException.
Não usar Base.metadata.create_all(). O banco já existe; SQLAlchemy é só ORM. Alembic fica para o futuro.
Mudanças de banco: primeiro o SQL (arquivo em database/, re-executável com IF NOT EXISTS), depois o model espelhando o SQL.

==================================================
BANCO (tabelas existentes)
==================================================
produtos, clientes, pedidos_avulsos, itens_pedido_avulso, assinaturas, escolhas_assinante, compras_assinatura.

assinaturas: id, cliente_id (INT NOT NULL UNIQUE, FK clientes ON DELETE CASCADE), plano_marmitas INT NOT NULL, saldo_restante INT NOT NULL, status VARCHAR(20) NOT NULL DEFAULT 'Pendente', data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP.
-> um cliente tem no máximo UMA assinatura. Renovar NÃO cria outra: credita saldo na mesma linha.

escolhas_assinante: id, cliente_id (FK clientes ON DELETE CASCADE), produto_id (FK produtos.id, SEM ondelete), quantidade INT NOT NULL DEFAULT 1, data_escolha TIMESTAMP DEFAULT CURRENT_TIMESTAMP.
-> NÃO possui assinatura_id, status, ciclo nem data de entrega. Relação com a assinatura é indireta, via cliente_id. NÃO criar relacionamento direto Assinatura -> EscolhaAssinante.

compras_assinatura: id SERIAL PK, cliente_id INT NOT NULL FK clientes ON DELETE CASCADE, plano_marmitas INT NOT NULL, data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP.
-> histórico: UMA LINHA POR COMPRA DE PLANO (contratação inicial e cada renovação).
-> Pagamento: de propósito NÃO há coluna de pagamento (pagamento manual; controlo pelo status da assinatura). Quando houver pagamento no site, estender com ALTER TABLE; não preparar nada agora.

Produtos no banco (todos ativos): ids 1-4 = ciclo 1 (Carne de Panela, Frango em Tiras, Frango Desfiado com Purê, Escondidinho de Carne); ids 5-8 = ciclo 2 (Almôndegas com Arroz, Frango Teriyaki, Guisado com Purê, Escondidinho de Frango).
Clientes/assinaturas de teste hoje: cliente 1 = plano 12, Ativa, saldo 10 (após testes); cliente 2 = plano 16, saldo 12, Pendente; cliente 3 = plano 12, saldo 12, Pendente. Existe uma escolha de teste (id 3: cliente 1, produto 1, qtd 2). A tabela compras_assinatura tem 3 linhas de teste.
Ciclo em 22/10/2026 (quinta, semana ISO 43): ciclo 1.

==================================================
O QUE JÁ FUNCIONA (testado no Swagger)
==================================================
- GET / -> status Online
- GET /marmitas-ativas -> produtos ativos do ciclo atual (services/cronograma.py: semana do ano, paridade, fuso America/Sao_Paulo; seg-qui = ciclo da semana atual, sex-dom = da seguinte).
- POST /pedidos -> 201, Pendente, frete fixo 10.00, previsão de entrega. Corpo: {"cliente_id": 1, "itens": [{"produto_id": 5, "quantidade": 2}]}. Reconfirmado 201 em 22/10.
- POST /assinaturas -> corpo {"cliente_id": N, "plano_marmitas": 12|16|20|24}. 201 Pendente com saldo = plano; 409 se já tem assinatura; 404 cliente inexistente; 422 plano inválido. Grava a compra inicial em compras_assinatura no mesmo commit.
- POST /assinaturas/{cliente_id}/escolhas (NOVO, testado) -> corpo {"produto_id": N, "quantidade": N}. 201 com {"escolha": {...}, "saldo_restante": N}. Erros testados: 404 cliente inexistente; 404 cliente sem assinatura; 409 assinatura não Ativa; 404 produto inexistente; 422 produto inativo/fora do ciclo; 422 quantidade maior que o saldo; 422 quantidade <= 0 (Pydantic). Nenhum erro desconta saldo.

NÃO quebrar esses fluxos.

Módulo de assinaturas (estado real):
- schemas/assinatura.py: AssinaturaCreateSchema, AssinaturaResponseSchema, EscolhaCreateSchema (quantidade gt=0), EscolhaResponseSchema, EscolhaRealizadaSchema (escolha + saldo_restante), RenovacaoCreateSchema (plano_marmitas Literal[12,16,20,24]).
- services/assinatura.py: constantes STATUS_PENDENTE/ATIVA/ENCERRADA; exceções AssinaturaError (base), ClienteNaoEncontradoError, AssinaturaJaExisteError, AssinaturaNaoEncontradaError, AssinaturaNaoAtivaError, ProdutoNaoEncontradoError, ProdutoForaDoCicloError, SaldoInsuficienteError, AssinaturaPendenteError; dataclass ResultadoEscolha(escolha, saldo_restante); funções contratar_assinatura, escolher_marmita (usa with_for_update na assinatura; devolve ResultadoEscolha), renovar_assinatura (implementada e commitada, AINDA SEM ROTA e sem teste).
- main.py: rotas POST /assinaturas e POST /assinaturas/{cliente_id}/escolhas traduzindo exceções em HTTP.

==================================================
REGRAS DE NEGÓCIO DEFINIDAS
==================================================
1. Planos: 12, 16, 20 ou 24 marmitas (validados no schema).
2. Status: Pendente (aguardando pagamento), Ativa, Encerrada. Eu altero o status manualmente. Só assinatura Ativa pode escolher marmitas.
3. Consumo do saldo: descontado na hora da escolha; recusar se quantidade > saldo. Saldo 0 continua na linha (não vira Encerrada sozinha).
4. Escolhas repetidas: sem limite semanal, só o saldo manda. Produto precisa estar ativo e no ciclo atual.
5. Renovação (DECIDIDA, service pronto): POST /assinaturas/{cliente_id}/renovacoes com {"plano_marmitas": 12|16|20|24}.
   - O plano comprado é SOMADO ao saldo_restante atual (sobras não se perdem).
   - plano_marmitas da assinatura passa a ser o último plano contratado.
   - A renovação SEMPRE volta o status para Pendente (decisão confirmada em 22/10: para eu cobrar, conferir o pagamento e reativar manualmente). Consequência aceita: enquanto Pendente, o cliente não escolhe marmitas, nem as sobras.
   - Assinatura Ativa ou Encerrada pode renovar (vira Pendente). Assinatura Pendente -> 409 (já há pagamento em aberto). Cliente inexistente -> 404; cliente sem assinatura -> 404 (usar POST /assinaturas na primeira compra).
   - Cada renovação grava uma linha em compras_assinatura, no mesmo commit.
6. Mapeamento de erros (confirmado e implementado nas escolhas): 404 cliente/assinatura/produto inexistente; 409 assinatura não Ativa; 422 produto inativo ou fora do ciclo; 422 quantidade maior que o saldo.

==================================================
PRÓXIMOS PASSOS (um por vez, commit pequeno a cada etapa)
==================================================
14c. Rota POST /assinaturas/{cliente_id}/renovacoes no main.py, status_code=201, response_model=AssinaturaResponseSchema, corpo RenovacaoCreateSchema. Imports novos em main.py: RenovacaoCreateSchema (schemas), renovar_assinatura e AssinaturaPendenteError (services). Tradução: ClienteNaoEncontradoError -> 404; AssinaturaNaoEncontradaError -> 404; AssinaturaPendenteError -> 409 ("Já existe uma compra aguardando pagamento."). Duas linhas em branco entre rotas; decorador colado no def.
14d. Testes no Swagger: renovar o cliente 1 (Ativa) -> 201, status Pendente, saldo somado (ex.: saldo 10 + plano 12 = 22), plano_marmitas atualizado, nova linha em compras_assinatura (SELECT no Beekeeper); renovar de novo o mesmo cliente -> 409; renovar cliente 2 (Pendente) -> 409; cliente 999 -> 404; plano 10 -> 422. Conferir também: depois de renovar, POST escolhas do cliente 1 -> 409 (Pendente). Para testar renovação de Encerrada: UPDATE assinaturas SET status = 'Encerrada' WHERE cliente_id = N. Reconfirmar POST /pedidos 201.
15. git push e atualizar/commitar este arquivo.

==================================================
PENDÊNCIAS CONHECIDAS (não urgentes, NÃO mexer sem eu pedir)
==================================================
1. database/init.sql desatualizado: produtos sem a coluna ciclo_cardapio (existe no banco real e no modelo, provavelmente criada por ALTER manual); produtos.ativo tem DEFAULT FALSE no SQL e default=True no modelo. Ajustar o script ou criar um SQL complementar (padrão database/002_*.sql).
2. POST /pedidos não valida se cliente_id existe: cliente inexistente gera violação de FK no commit (HTTP 500 em vez de 404). Pensar em reaproveitar a verificação do service de assinaturas.
3. Menor: PedidoAvulso.cliente_id não tem ondelete e Cliente.pedidos_avulsos não tem cascade, enquanto o SQL tem ON DELETE CASCADE. Sem efeito prático hoje.
4. git push dos commits locais (origin/main está em 7d558bd).
5. Detalhes estéticos: linha com 4 espaços depois de db.add(nova) em contratar_assinatura; arquivos sem newline no fim. Sem efeito.
6. Pagamento: quando existir pagamento no site, estender compras_assinatura (ver seção BANCO).
7. Dados de teste inconsistentes (cliente 2 com plano 16 e saldo 12; cliente 3 plano 12). Sem efeito nos testes.

==================================================
SEU PRIMEIRO PASSO NA PRÓXIMA SESSÃO
==================================================
1. Confirme o estado lendo o repositório (ou me peça "git --no-pager log -8 --oneline" e "git --no-pager status -s"), sem escrever código ainda.
2. Verifique se a rota de renovação já existe no main.py (procure "renovacoes"); se não existir, retome pelo 14c. Peça o main.py atual antes de escrever.
3. Responda direto, mande um passo por vez (arquivo + trecho exato) e espere minha confirmação.