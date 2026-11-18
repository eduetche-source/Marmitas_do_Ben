from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from ..models.cliente import Cliente
from ..models.produto import Produto, PedidoAvulso, ItemPedidoAvulso
from .cronograma import calcular_data_entrega_pedido

STATUS_PAGAMENTO_PENDENTE = "Pendente"
VALOR_FRETE = 10.00


class PedidoError(Exception):
    """Base das excecoes de dominio do modulo de pedidos avulsos."""


class PedidoClienteNaoEncontradoError(PedidoError):
    def __init__(self, cliente_id: int):
        super().__init__(cliente_id)
        self.cliente_id = cliente_id


class PedidoProdutoNaoEncontradoError(PedidoError):
    def __init__(self, produto_id: int):
        super().__init__(produto_id)
        self.produto_id = produto_id


@dataclass
class ResultadoPedido:
    pedido: PedidoAvulso
    data_entrega_prevista: datetime


def criar_pedido_avulso(db: Session, cliente_id: int, itens: list) -> ResultadoPedido:
    # Valida o cliente antes de gravar: sem isso, o erro so apareceria
    # no commit (violacao de FK) e viraria HTTP 500.
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise PedidoClienteNaoEncontradoError(cliente_id)

    # O cronograma calcula a previsao de entrega exibida ao cliente.
    data_entrega_prevista = calcular_data_entrega_pedido()

    pedido = PedidoAvulso(
        cliente_id=cliente_id,
        valor_frete=VALOR_FRETE,
        status_pagamento=STATUS_PAGAMENTO_PENDENTE,
    )

    for item in itens:
        produto = db.get(Produto, item.produto_id)
        if produto is None:
            raise PedidoProdutoNaoEncontradoError(item.produto_id)

        pedido.itens.append(
            ItemPedidoAvulso(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
            )
        )

    # Um unico commit: pedido e itens sao gravados juntos.
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return ResultadoPedido(pedido=pedido, data_entrega_prevista=data_entrega_prevista)
