-- Preco unitario de cada item do pedido avulso, gravado no momento da venda.
-- Assim, mudar o preco de um produto nao altera o valor dos pedidos antigos.
-- Re-executavel: pode rodar mais de uma vez sem erro.

-- 1) Coluna nova (comeca vazia nos itens ja existentes).
ALTER TABLE itens_pedido_avulso
    ADD COLUMN IF NOT EXISTS preco_unitario DECIMAL(10, 2);

-- 2) Itens antigos nao guardaram o preco: usamos o preco atual do produto,
--    que e a melhor informacao disponivel.
UPDATE itens_pedido_avulso AS i
SET preco_unitario = p.preco
FROM produtos AS p
WHERE i.produto_id = p.id
  AND i.preco_unitario IS NULL;

-- 3) A partir de agora, todo item precisa ter preco.
ALTER TABLE itens_pedido_avulso
    ALTER COLUMN preco_unitario SET NOT NULL;
