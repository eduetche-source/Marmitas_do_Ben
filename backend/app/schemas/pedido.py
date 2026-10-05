from pydantic import BaseModel
from typing import List

class ItemPedidoSchema(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreateSchema(BaseModel):
    cliente_id: int
    itens: List[ItemPedidoSchema]
