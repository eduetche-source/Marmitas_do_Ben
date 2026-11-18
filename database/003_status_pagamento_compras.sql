-- Situacao do pagamento de cada compra de plano.
-- O saldo da assinatura so e creditado quando a compra vira 'Paga'.
-- Re-executavel: pode rodar mais de uma vez sem erro.

-- 1) Coluna nova. As compras ja existentes entram como 'Paga', porque
--    no modelo antigo o saldo delas ja tinha sido somado na assinatura.
ALTER TABLE compras_assinatura
    ADD COLUMN IF NOT EXISTS status_pagamento VARCHAR(20) NOT NULL DEFAULT 'Paga';

-- 2) A partir de agora, toda compra nova nasce 'Pendente'.
ALTER TABLE compras_assinatura
    ALTER COLUMN status_pagamento SET DEFAULT 'Pendente';

-- 3) No maximo UMA compra Pendente por cliente (indice unico parcial).
CREATE UNIQUE INDEX IF NOT EXISTS uq_compras_assinatura_pendente_por_cliente
    ON compras_assinatura (cliente_id)
    WHERE status_pagamento = 'Pendente';
