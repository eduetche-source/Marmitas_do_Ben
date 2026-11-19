from dataclasses import dataclass
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.assinatura import Assinatura, CompraAssinatura, EscolhaAssinante
from ..models.cliente import Cliente
from ..models.produto import Produto
from .cronograma import obter_ciclo_cardapio_atual

STATUS_PENDENTE = "Pendente"
STATUS_ATIVA = "Ativa"
STATUS_ENCERRADA = "Encerrada"

# Situacao do pagamento de cada compra (compras_assinatura.status_pagamento).
COMPRA_PENDENTE = "Pendente"
COMPRA_PAGA = "Paga"
COMPRA_CANCELADA = "Cancelada"


class AssinaturaError(Exception):
    """Base das excecoes de dominio do modulo de assinaturas."""


class ClienteNaoEncontradoError(AssinaturaError):
    pass


class AssinaturaJaExisteError(AssinaturaError):
    pass


class AssinaturaNaoEncontradaError(AssinaturaError):
    pass


class AssinaturaNaoAtivaError(AssinaturaError):
    pass


class ProdutoNaoEncontradoError(AssinaturaError):
    pass


class ProdutoForaDoCicloError(AssinaturaError):
    pass


class SaldoInsuficienteError(AssinaturaError):
    pass


class CompraPendenteError(AssinaturaError):
    """Ja existe uma compra do cliente aguardando pagamento."""


class SemCompraPendenteError(AssinaturaError):
    """Nao ha compra do cliente aguardando pagamento."""


def contratar_assinatura(db: Session, cliente_id: int, plano_marmitas: int) -> Assinatura:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise ClienteNaoEncontradoError(cliente_id)

    existente = db.query(Assinatura).filter(Assinatura.cliente_id == cliente_id).first()
    if existente is not None:
        raise AssinaturaJaExisteError(cliente_id)

    # Saldo comeca em 0: so e creditado quando o pagamento da compra
    # for confirmado.
    nova = Assinatura(
        cliente_id=cliente_id,
        plano_marmitas=plano_marmitas,
        saldo_restante=0,
        status=STATUS_PENDENTE,
    )
    db.add(nova)

    db.add(
        CompraAssinatura(
            cliente_id=cliente_id,
            plano_marmitas=plano_marmitas,
            status_pagamento=COMPRA_PENDENTE,
        )
    )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AssinaturaJaExisteError(cliente_id)

    db.refresh(nova)
    return nova


@dataclass
class ResultadoEscolha:
    escolha: EscolhaAssinante
    saldo_restante: int


def escolher_marmita(
    db: Session, cliente_id: int, produto_id: int, quantidade: int
) -> ResultadoEscolha:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise ClienteNaoEncontradoError(cliente_id)

    # with_for_update trava a linha da assinatura ate o commit: duas escolhas
    # simultaneas nao conseguem gastar o mesmo saldo.
    assinatura = (
        db.query(Assinatura)
        .filter(Assinatura.cliente_id == cliente_id)
        .with_for_update()
        .first()
    )
    if assinatura is None:
        raise AssinaturaNaoEncontradaError(cliente_id)

    if assinatura.status != STATUS_ATIVA:
        raise AssinaturaNaoAtivaError(cliente_id)

    produto = db.get(Produto, produto_id)
    if produto is None:
        raise ProdutoNaoEncontradoError(produto_id)

    if not produto.ativo or produto.ciclo_cardapio != obter_ciclo_cardapio_atual():
        raise ProdutoForaDoCicloError(produto_id)

    if quantidade > assinatura.saldo_restante:
        raise SaldoInsuficienteError(quantidade)

    assinatura.saldo_restante -= quantidade
    saldo_restante = assinatura.saldo_restante
    escolha = EscolhaAssinante(
        cliente_id=cliente_id,
        produto_id=produto_id,
        quantidade=quantidade,
    )
    db.add(escolha)

    # Um unico commit: saldo e escolha sao gravados juntos.
    db.commit()
    db.refresh(escolha)
    return ResultadoEscolha(escolha=escolha, saldo_restante=saldo_restante)


def _consultar_compra_pendente(db: Session, cliente_id: int) -> Optional[CompraAssinatura]:
    """Devolve a compra do cliente aguardando pagamento, ou None.
    Pelo indice unico do banco, existe no maximo uma."""
    return (
        db.query(CompraAssinatura)
        .filter(
            CompraAssinatura.cliente_id == cliente_id,
            CompraAssinatura.status_pagamento == COMPRA_PENDENTE,
        )
        .first()
    )


@dataclass
class ResultadoConsultaAssinatura:
    assinatura: Assinatura
    compra_pendente: Optional[CompraAssinatura]


def consultar_assinatura(db: Session, cliente_id: int) -> ResultadoConsultaAssinatura:
    # Somente leitura: nao trava nada e nao faz commit.
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise ClienteNaoEncontradoError(cliente_id)

    assinatura = db.query(Assinatura).filter(Assinatura.cliente_id == cliente_id).first()
    if assinatura is None:
        raise AssinaturaNaoEncontradaError(cliente_id)

    return ResultadoConsultaAssinatura(
        assinatura=assinatura,
        compra_pendente=_consultar_compra_pendente(db, cliente_id),
    )


def renovar_assinatura(db: Session, cliente_id: int, plano_marmitas: int) -> CompraAssinatura:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise ClienteNaoEncontradoError(cliente_id)

    # with_for_update trava a linha: duas renovacoes simultaneas do mesmo
    # cliente sao atendidas uma de cada vez.
    assinatura = (
        db.query(Assinatura)
        .filter(Assinatura.cliente_id == cliente_id)
        .with_for_update()
        .first()
    )
    if assinatura is None:
        raise AssinaturaNaoEncontradaError(cliente_id)

    # So pode haver uma compra aguardando pagamento por cliente.
    if _consultar_compra_pendente(db, cliente_id) is not None:
        raise CompraPendenteError(cliente_id)

    # A renovacao so registra a compra. Saldo, plano e status da assinatura
    # mudam apenas quando o pagamento for confirmado: enquanto isso, uma
    # assinatura Ativa continua usando as sobras normalmente.
    compra = CompraAssinatura(
        cliente_id=cliente_id,
        plano_marmitas=plano_marmitas,
        status_pagamento=COMPRA_PENDENTE,
    )
    db.add(compra)

    try:
        db.commit()
    except IntegrityError:
        # Indice unico do banco: barrou uma segunda compra Pendente.
        db.rollback()
        raise CompraPendenteError(cliente_id)

    db.refresh(compra)
    return compra


def _buscar_compra_pendente(db: Session, cliente_id: int) -> tuple[Assinatura, CompraAssinatura]:
    """Passos comuns de confirmar e cancelar: valida o cliente, trava a
    assinatura e devolve a compra aguardando pagamento."""
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise ClienteNaoEncontradoError(cliente_id)

    # with_for_update trava a assinatura: duas operacoes simultaneas sobre a
    # mesma compra (ex.: confirmar duas vezes) sao atendidas uma de cada vez.
    assinatura = (
        db.query(Assinatura)
        .filter(Assinatura.cliente_id == cliente_id)
        .with_for_update()
        .first()
    )
    if assinatura is None:
        raise AssinaturaNaoEncontradaError(cliente_id)

    compra = _consultar_compra_pendente(db, cliente_id)
    if compra is None:
        raise SemCompraPendenteError(cliente_id)

    return assinatura, compra


def confirmar_pagamento(db: Session, cliente_id: int) -> Assinatura:
    assinatura, compra = _buscar_compra_pendente(db, cliente_id)

    # Pagamento confirmado: so agora o plano entra no saldo.
    # Sobras nao se perdem: o plano e somado ao saldo atual.
    compra.status_pagamento = COMPRA_PAGA
    assinatura.saldo_restante += compra.plano_marmitas
    assinatura.plano_marmitas = compra.plano_marmitas
    assinatura.status = STATUS_ATIVA

    # Um unico commit: compra e assinatura sao gravadas juntas.
    db.commit()
    db.refresh(assinatura)
    return assinatura


def cancelar_compra(db: Session, cliente_id: int) -> Assinatura:
    assinatura, compra = _buscar_compra_pendente(db, cliente_id)

    # Compra nao paga nunca entrou no saldo: nada a descontar.
    compra.status_pagamento = COMPRA_CANCELADA

    # Assinatura Pendente = primeira compra, nunca paga: o cliente desistiu
    # antes de comecar. Nos outros casos (renovacao), o status nao muda e as
    # sobras ja pagas continuam valendo.
    if assinatura.status == STATUS_PENDENTE:
        assinatura.status = STATUS_ENCERRADA

    db.commit()
    db.refresh(assinatura)
    return assinatura