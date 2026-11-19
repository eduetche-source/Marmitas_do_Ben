from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class ItemPedidoSchema(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreateSchema(BaseModel):
    cliente_id: int
    itens: List[ItemPedidoSchema]


# Saida das rotas de admin: GET /pedidos-pendentes, confirmar pagamento
# e cancelar pedido.

class ClienteResumoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    whatsapp: str


class ItemPedidoDetalheSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: Decimal


class PedidoDetalheSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pedido_id: int
    data_pedido: Optional[datetime] = None
    status_pagamento: str
    cliente: ClienteResumoSchema
    itens: List[ItemPedidoDetalheSchema]
    valor_frete: Decimal
    valor_total: Decimal
