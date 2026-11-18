from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db

# Importa todos os models para que o SQLAlchemy registre
# os relacionamentos corretamente.
from .models.cliente import Cliente
from .models.produto import (
    Produto,
    PedidoAvulso,
    ItemPedidoAvulso,
)
from .models.assinatura import (
    Assinatura,
    EscolhaAssinante,
)

from .schemas.pedido import PedidoCreateSchema

from .schemas.assinatura import (
    AssinaturaCreateSchema,
    AssinaturaResponseSchema,
    EscolhaCreateSchema,
    EscolhaRealizadaSchema,
    RenovacaoCreateSchema,
)

from .services.cronograma import (
    obter_ciclo_cardapio_atual,
    calcular_data_entrega_pedido,
)

from .services.assinatura import (
    contratar_assinatura,
    ClienteNaoEncontradoError,
    AssinaturaJaExisteError,
    AssinaturaNaoEncontradaError,
    AssinaturaNaoAtivaError,
    ProdutoNaoEncontradoError,
    ProdutoForaDoCicloError,
    SaldoInsuficienteError,
    escolher_marmita,
    renovar_assinatura,
    AssinaturaPendenteError,
)

from .services.pedido import (
    criar_pedido_avulso,
    PedidoClienteNaoEncontradoError,
    PedidoProdutoNaoEncontradoError,
)

app = FastAPI(title="Marmitas do Ben API")

@app.get("/")
def home():
    return {"status": "Online", "projeto": "Marmitas do Ben"}

@app.get("/marmitas-ativas")
def listar_marmitas_ativas(db: Session = Depends(get_db)):
    ciclo_ativo = obter_ciclo_cardapio_atual()

    marmitas = db.query(Produto).filter(
        Produto.ativo == True,
        Produto.ciclo_cardapio == ciclo_ativo
    ).all()

    return {
        "ciclo_vendas_atual": ciclo_ativo,
        "total_produtos": len(marmitas),
        "produtos": marmitas
    }

@app.post("/pedidos", status_code=201)
def criar_pedido(payload: PedidoCreateSchema, db: Session = Depends(get_db)):
    try:
        resultado = criar_pedido_avulso(db, payload.cliente_id, payload.itens)
    except PedidoClienteNaoEncontradoError as erro:
        raise HTTPException(status_code=404, detail=f"Cliente com ID {erro.cliente_id} não encontrado.")
    except PedidoProdutoNaoEncontradoError as erro:
        raise HTTPException(status_code=404, detail=f"Marmita com ID {erro.produto_id} não encontrada.")

    return {
        "mensagem": "Pedido realizado com sucesso!",
        "pedido_id": resultado.pedido.id,
        "status_pagamento": resultado.pedido.status_pagamento,
        "data_entrega_prevista": resultado.data_entrega_prevista.strftime("%Y-%m-%d"),
        "total_itens": len(resultado.pedido.itens)
    }


@app.post("/assinaturas", status_code=201, response_model=AssinaturaResponseSchema)
def criar_assinatura(payload: AssinaturaCreateSchema, db: Session = Depends(get_db)):
    try:
        return contratar_assinatura(db, payload.cliente_id, payload.plano_marmitas)
    except ClienteNaoEncontradoError:
        raise HTTPException(status_code=404, detail=f"Cliente com ID {payload.cliente_id} não encontrado.")
    except AssinaturaJaExisteError:
        raise HTTPException(status_code=409, detail="Este cliente já possui uma assinatura.")


@app.post(
    "/assinaturas/{cliente_id}/escolhas",
    status_code=201,
    response_model=EscolhaRealizadaSchema,
)
def criar_escolha(cliente_id: int, payload: EscolhaCreateSchema, db: Session = Depends(get_db)):
    try:
        return escolher_marmita(db, cliente_id, payload.produto_id, payload.quantidade)
    except ClienteNaoEncontradoError:
        raise HTTPException(status_code=404, detail=f"Cliente com ID {cliente_id} não encontrado.")
    except AssinaturaNaoEncontradaError:
        raise HTTPException(status_code=404, detail="Este cliente não possui assinatura.")
    except AssinaturaNaoAtivaError:
        raise HTTPException(status_code=409, detail="A assinatura não está ativa.")
    except ProdutoNaoEncontradoError:
        raise HTTPException(status_code=404, detail=f"Marmita com ID {payload.produto_id} não encontrada.")
    except ProdutoForaDoCicloError:
        raise HTTPException(status_code=422, detail="Esta marmita não está disponível no cardápio atual.")
    except SaldoInsuficienteError:
        raise HTTPException(status_code=422, detail="Quantidade maior que o saldo restante da assinatura.")


@app.post(
    "/assinaturas/{cliente_id}/renovacoes",
    status_code=201,
    response_model=AssinaturaResponseSchema,
)
def criar_renovacao(cliente_id: int, payload: RenovacaoCreateSchema, db: Session = Depends(get_db)):
    try:
        return renovar_assinatura(db, cliente_id, payload.plano_marmitas)
    except ClienteNaoEncontradoError:
        raise HTTPException(status_code=404, detail=f"Cliente com ID {cliente_id} não encontrado.")
    except AssinaturaNaoEncontradaError:
        raise HTTPException(status_code=404, detail="Este cliente não possui assinatura.")
    except AssinaturaPendenteError:
        raise HTTPException(status_code=409, detail="Já existe uma compra aguardando pagamento.")