CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2) NOT NULL DEFAULT 23.90,
    ativo BOOLEAN NOT NULL DEFAULT FALSE
);

-- Criação da tabela de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    whatsapp VARCHAR(20) NOT NULL UNIQUE, -- Fundamental para o seu fluxo de MVP
    email VARCHAR(100) UNIQUE,
    rua VARCHAR(150) NOT NULL,
    numero VARCHAR(20) NOT NULL,
    bairro VARCHAR(50) NOT NULL,
    cidade VARCHAR(50) NOT NULL DEFAULT 'Porto Alegre', -- Define sua cidade atual por padrão
    distancia_km DECIMAL(5, 2) -- O Back-end vai calcular e salvar a distância aqui
);

-- 1. Tabela mãe dos pedidos avulsos
CREATE TABLE IF NOT EXISTS pedidos_avulsos (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL,
    data_pedido TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valor_frete DECIMAL(10, 2) NOT NULL,
    status_pagamento VARCHAR(20) NOT NULL DEFAULT 'Pendente', -- 'Pendente' ou 'Pago'
    
    -- Chave estrangeira ligando o pedido ao cliente
    CONSTRAINT fk_cliente_pedido FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- 2. Tabela pivô/intermediária (Itens do Pedido)
CREATE TABLE IF NOT EXISTS itens_pedido_avulso (
    id SERIAL PRIMARY KEY,
    pedido_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    
    -- Chaves estrangeiras ligando aos respectivos pais
    CONSTRAINT fk_pedido FOREIGN KEY (pedido_id) REFERENCES pedidos_avulsos(id) ON DELETE CASCADE,
    CONSTRAINT fk_produto FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- 1. Criamos a tabela de assinaturas que estava faltando no Beekeeper
CREATE TABLE IF NOT EXISTS assinaturas (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL UNIQUE, 
    plano_marmitas INT NOT NULL,    
    saldo_restante INT NOT NULL,    
    status VARCHAR(20) NOT NULL DEFAULT 'Pendente', 
    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cliente_assinatura FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- 2. Criamos a tabela de escolhas do assinante
CREATE TABLE IF NOT EXISTS escolhas_assinante (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    data_escolha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cliente_escolha FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    CONSTRAINT fk_produto_escolha FOREIGN KEY (produto_id) REFERENCES produtos(id)
);



