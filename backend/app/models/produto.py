from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Numeric,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from ..database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    nome = Column(
        String,
        nullable=False,
    )

    descricao = Column(
        String,
        nullable=True,
    )

    preco = Column(
        Numeric(10, 2),
        nullable=False,
    )

    ativo = Column(
        Boolean,
        default=True,
    )

    ciclo_cardapio = Column(
        Integer,
        default=1,
    )

    # Itens de pedidos avulsos que utilizam este produto.
    itens_pedidos = relationship(
        "ItemPedidoAvulso",
        back_populates="produto",
    )

    # Escolhas de assinantes que utilizam este produto.
    escolhas_assinante = relationship(
        "EscolhaAssinante",
        back_populates="produto",
    )


class PedidoAvulso(Base):
    __tablename__ = "pedidos_avulsos"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id"),
        nullable=False,
    )

    data_pedido = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=True,
    )

    valor_frete = Column(
        Numeric(10, 2),
        default=10.00,
    )

    status_pagamento = Column(
        String,
        default="Pendente",
    )

    # Cliente que realizou o pedido.
    cliente = relationship(
        "Cliente",
        back_populates="pedidos_avulsos",
    )

    # Itens pertencentes ao pedido.
    itens = relationship(
        "ItemPedidoAvulso",
        back_populates="pedido",
        cascade="all, delete-orphan",
    )


class ItemPedidoAvulso(Base):
    __tablename__ = "itens_pedido_avulso"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    pedido_id = Column(
        Integer,
        ForeignKey("pedidos_avulsos.id"),
        nullable=False,
    )

    produto_id = Column(
        Integer,
        ForeignKey("produtos.id"),
        nullable=False,
    )

    quantidade = Column(
        Integer,
        nullable=False,
    )

    pedido = relationship(
        "PedidoAvulso",
        back_populates="itens",
    )

    produto = relationship(
        "Produto",
        back_populates="itens_pedidos",
    )

