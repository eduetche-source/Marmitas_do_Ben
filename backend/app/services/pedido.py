from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from ..models.cliente import Cliente
from ..models.produto import Produto, PedidoAvulso, ItemPedidoAvulso
from .cronograma import calcular_data_entrega_pedido, obter_ciclo_cardapio_atual

STATUS_PAGAMENTO_PENDENTE = "Pendente"
STATUS_PAGAMENTO_PAGO = "Pago"
STATUS_PAGAMENTO_CANCELADO = "Cancelado"
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


class PedidoNaoEncontradoError(PedidoError):
    def __init__(self, pedido_id: int):
        super().__init__(pedido_id)
        self.pedido_id = pedido_id


class PedidoNaoPendenteError(PedidoError):
    """O pedido ja foi pago ou cancelado."""

    def __init__(self, pedido_id: int, status_atual: str):
        super().__init__(pedido_id, status_atual)
        self.pedido_id = pedido_id
        self.status_atual = status_atual


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
class ItemPedidoDetalhe:
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: Decimal


@dataclass
class PedidoDetalhe:
    pedido_id: int
    data_pedido: datetime
    status_pagamento: str
    cliente: Cliente
    itens: list[ItemPedidoDetalhe]
    valor_frete: Decimal
    valor_total: Decimal


def _montar_detalhe(pedido: PedidoAvulso) -> PedidoDetalhe:
    # Total pelo preco gravado em cada item (nao pelo preco atual do produto).
    valor_total = pedido.valor_frete + sum(
        (item.preco_unitario * item.quantidade for item in pedido.itens),
        Decimal("0.00"),
    )
    return PedidoDetalhe(
        pedido_id=pedido.id,
        data_pedido=pedido.data_pedido,
        status_pagamento=pedido.status_pagamento,
        cliente=pedido.cliente,
        itens=[
            ItemPedidoDetalhe(
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


def listar_pedidos_pendentes(db: Session) -> list[PedidoDetalhe]:
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

    return [_montar_detalhe(pedido) for pedido in pedidos]


def _buscar_pedido_pendente(db: Session, pedido_id: int) -> PedidoAvulso:
    """Passos comuns de confirmar e cancelar: trava o pedido e garante
    que ele ainda esta aguardando pagamento."""
    # with_for_update trava a linha: confirmar e cancelar ao mesmo tempo
    # (ou confirmar duas vezes) sao atendidos um de cada vez.
    pedido = (
        db.query(PedidoAvulso)
        .filter(PedidoAvulso.id == pedido_id)
        .with_for_update()
        .first()
    )
    if pedido is None:
        raise PedidoNaoEncontradoError(pedido_id)

    if pedido.status_pagamento != STATUS_PAGAMENTO_PENDENTE:
        raise PedidoNaoPendenteError(pedido_id, pedido.status_pagamento)

    return pedido


def confirmar_pagamento_pedido(db: Session, pedido_id: int) -> PedidoDetalhe:
    pedido = _buscar_pedido_pendente(db, pedido_id)
    pedido.status_pagamento = STATUS_PAGAMENTO_PAGO
    db.commit()
    return _montar_detalhe(pedido)


def cancelar_pedido(db: Session, pedido_id: int) -> PedidoDetalhe:
    # So pedido Pendente pode ser cancelado: devolucao de pedido Pago
    # seria outro fluxo (ainda nao existe).
    pedido = _buscar_pedido_pendente(db, pedido_id)
    pedido.status_pagamento = STATUS_PAGAMENTO_CANCELADO
    db.commit()
    return _montar_detalhe(pedido)
