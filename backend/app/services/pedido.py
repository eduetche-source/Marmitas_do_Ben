from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from ..models.cliente import Cliente
from ..models.produto import Produto, PedidoAvulso, ItemPedidoAvulso
from .cronograma import calcular_data_entrega_pedido, obter_ciclo_cardapio_atual

STATUS_PAGAMENTO_PENDENTE = "Pendente"
# Decimal (e nao float) para somar com os precos sem erro de arredondamento.
VALOR_FRETE = Decimal("10.00")


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


class PedidoProdutoForaDoCicloError(PedidoError):
    def __init__(self, produto_id: int):
        super().__init__(produto_id)
        self.produto_id = produto_id


@dataclass
class ResultadoPedido:
    pedido: PedidoAvulso
    data_entrega_prevista: datetime
    valor_total: Decimal


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

    # Pedido avulso segue o mesmo cardapio das assinaturas: so produtos
    # ativos e do ciclo atual.
    ciclo_atual = obter_ciclo_cardapio_atual()

    valor_total = VALOR_FRETE

    for item in itens:
        produto = db.get(Produto, item.produto_id)
        if produto is None:
            raise PedidoProdutoNaoEncontradoError(item.produto_id)

        if not produto.ativo or produto.ciclo_cardapio != ciclo_atual:
            raise PedidoProdutoForaDoCicloError(item.produto_id)

        # O preco e copiado para o item: mudar o preco do produto depois
        # nao altera o valor deste pedido.
        pedido.itens.append(
            ItemPedidoAvulso(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco_unitario=produto.preco,
            )
        )
        valor_total += produto.preco * item.quantidade

    # Um unico commit: pedido e itens sao gravados juntos.
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return ResultadoPedido(
        pedido=pedido,
        data_entrega_prevista=data_entrega_prevista,
        valor_total=valor_total,
    )


@dataclass
class ItemPendente:
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: Decimal


@dataclass
class PedidoPendente:
    pedido_id: int
    data_pedido: datetime
    cliente: Cliente
    itens: list[ItemPendente]
    valor_frete: Decimal
    valor_total: Decimal


def listar_pedidos_pendentes(db: Session) -> list[PedidoPendente]:
    # Somente leitura: pedidos aguardando pagamento, do mais antigo para o
    # mais novo (quem espera ha mais tempo aparece primeiro).
    # selectinload busca clientes, itens e produtos em poucas consultas,
    # em vez de uma consulta por pedido.
    pedidos = (
        db.query(PedidoAvulso)
        .options(
            selectinload(PedidoAvulso.cliente),
            selectinload(PedidoAvulso.itens).selectinload(ItemPedidoAvulso.produto),
        )
        .filter(PedidoAvulso.status_pagamento == STATUS_PAGAMENTO_PENDENTE)
        .order_by(PedidoAvulso.data_pedido.asc(), PedidoAvulso.id.asc())
        .all()
    )

    resultado = []
    for pedido in pedidos:
        # Total pelo preco gravado em cada item (nao pelo preco atual do produto).
        valor_total = pedido.valor_frete + sum(
            (item.preco_unitario * item.quantidade for item in pedido.itens),
            Decimal("0.00"),
        )
        resultado.append(
            PedidoPendente(
                pedido_id=pedido.id,
                data_pedido=pedido.data_pedido,
                cliente=pedido.cliente,
                itens=[
                    ItemPendente(
                        produto_id=item.produto_id,
                        produto_nome=item.produto.nome,
                        quantidade=item.quantidade,
                        preco_unitario=item.preco_unitario,
                    )
                    for item in pedido.itens
                ],
                valor_frete=pedido.valor_frete,
                valor_total=valor_total,
            )
        )
    return resultado
