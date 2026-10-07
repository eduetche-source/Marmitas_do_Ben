from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.assinatura import Assinatura
from ..models.cliente import Cliente

STATUS_PENDENTE = "Pendente"
STATUS_ATIVA = "Ativa"
STATUS_ENCERRADA = "Encerrada"


class AssinaturaError(Exception):
    """Base das excecoes de dominio do modulo de assinaturas."""


class ClienteNaoEncontradoError(AssinaturaError):
    pass


class AssinaturaJaExisteError(AssinaturaError):
    pass


def contratar_assinatura(db: Session, cliente_id: int, plano_marmitas: int) -> Assinatura:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise ClienteNaoEncontradoError(cliente_id)

    existente = db.query(Assinatura).filter(Assinatura.cliente_id == cliente_id).first()
    if existente is not None:
        raise AssinaturaJaExisteError(cliente_id)

    nova = Assinatura(
        cliente_id=cliente_id,
        plano_marmitas=plano_marmitas,
        saldo_restante=plano_marmitas,
        status=STATUS_PENDENTE,
    )
    db.add(nova)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AssinaturaJaExisteError(cliente_id)

    db.refresh(nova)
    return nova
