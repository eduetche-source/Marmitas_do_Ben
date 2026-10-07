from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AssinaturaCreateSchema(BaseModel):
    cliente_id: int
    plano_marmitas: Literal[12, 16, 20, 24]


class AssinaturaResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    plano_marmitas: int
    saldo_restante: int
    status: str
    data_inicio: Optional[datetime] = None


class EscolhaCreateSchema(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class EscolhaResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    produto_id: int
    quantidade: int
    data_escolha: Optional[datetime] = None
