from dataclasses import dataclass

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


class AssinaturaPendenteError(AssinaturaError):
    pass


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


def renovar_assinatura(db: Session, cliente_id: int, plano_marmitas: int) -> Assinatura:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise ClienteNaoEncontradoError(cliente_id)

    # with_for_update trava a linha: duas renovacoes simultaneas nao se perdem.
    assinatura = (
        db.query(Assinatura)
        .filter(Assinatura.cliente_id == cliente_id)
        .with_for_update()
        .first()
    )
    if assinatura is None:
        raise AssinaturaNaoEncontradaError(cliente_id)

    # Pendente = ja existe uma compra aguardando pagamento.
    if assinatura.status == STATUS_PENDENTE:
        raise AssinaturaPendenteError(cliente_id)

    # Sobras nao se perdem: o plano comprado e somado ao saldo atual.
    assinatura.saldo_restante += plano_marmitas
    assinatura.plano_marmitas = plano_marmitas
    assinatura.status = STATUS_PENDENTE

    db.add(
        CompraAssinatura(
            cliente_id=cliente_id,
            plano_marmitas=plano_marmitas,
        )
    )

    # Um unico commit: saldo, status e historico sao gravados juntos.
    db.commit()
    db.refresh(assinatura)
    return assinatura