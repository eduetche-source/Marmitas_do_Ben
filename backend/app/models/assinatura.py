from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from ..database import Base


class Assinatura(Base):
    __tablename__ = "assinaturas"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    plano_marmitas = Column(
        Integer,
        nullable=False,
    )

    saldo_restante = Column(
        Integer,
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
        default="Pendente",
    )

    data_inicio = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=True,
    )

    cliente = relationship(
        "Cliente",
        back_populates="assinatura",
    )


class EscolhaAssinante(Base):
    __tablename__ = "escolhas_assinante"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id", ondelete="CASCADE"),
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
        default=1,
    )

    data_escolha = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=True,
    )

    cliente = relationship(
        "Cliente",
        back_populates="escolhas_assinante",
    )

    produto = relationship(
        "Produto",
        back_populates="escolhas_assinante",
    )
