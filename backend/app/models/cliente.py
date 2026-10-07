from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from ..database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(
        String(100),
        nullable=False,
    )

    whatsapp = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    email = Column(
        String(100),
        unique=True,
        nullable=True,
    )

    rua = Column(
        String(150),
        nullable=False,
    )

    numero = Column(
        String(20),
        nullable=False,
    )

    bairro = Column(
        String(50),
        nullable=False,
    )

    cidade = Column(
        String(50),
        nullable=False,
        default="Porto Alegre",
    )

    distancia_km = Column(
        Numeric(5, 2),
        nullable=True,
    )

    # Um cliente pode ter no máximo uma assinatura,
    # pois assinaturas.cliente_id é UNIQUE.
    assinatura = relationship(
        "Assinatura",
        back_populates="cliente",
        uselist=False,
    )

    # Um cliente pode possuir várias escolhas de marmitas.
    escolhas_assinante = relationship(
        "EscolhaAssinante",
        back_populates="cliente",
        cascade="all, delete-orphan",
    )

    # Historico de compras de plano (contratacao inicial e renovacoes).
    compras_assinatura = relationship(
        "CompraAssinatura",
        back_populates="cliente",
        cascade="all, delete-orphan",
    )

    # Um cliente pode realizar vários pedidos avulsos.
    pedidos_avulsos = relationship(
        "PedidoAvulso",
        back_populates="cliente",
    )
