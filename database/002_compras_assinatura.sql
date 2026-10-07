CREATE TABLE IF NOT EXISTS compras_assinatura (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    plano_marmitas INT NOT NULL,
    data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_compras_assinatura_cliente_id
    ON compras_assinatura (cliente_id);

-- Historico retroativo: assinaturas criadas antes desta tabela existir.
INSERT INTO compras_assinatura (cliente_id, plano_marmitas, data_compra)
SELECT a.cliente_id, a.plano_marmitas, a.data_inicio
FROM assinaturas a
WHERE NOT EXISTS (
    SELECT 1 FROM compras_assinatura c WHERE c.cliente_id = a.cliente_id
);
