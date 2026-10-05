-- Inserindo as 8 marmitas reais do início do negócio (Cardápios 1 e 2)

-- CARDÁPIO 1 (Ativas na primeira semana)
INSERT INTO produtos (nome, descricao, preco, ativo) VALUES 
('Carne de Panela', 'Carne de panela macia, acompanhada de arroz integral com sementes e legumes refogados.', 23.90, TRUE),
('Frango em Tiras', 'Tiras de frango grelhadas, acompanhadas de arroz integral com sementes e legumes refogados.', 23.90, TRUE),
('Frango Desfiado com Purê', 'Frango desfiado suculento, acompanhado de purê de batata inglesa e legumes refogados.', 23.90, TRUE),
('Escondidinho de Carne', 'Delicioso escondidinho de aipim cremoso recheado com carne de panela.', 23.90, TRUE);

-- CARDÁPIO 2 (Ocultas, aguardando a troca de semana)
INSERT INTO produtos (nome, descricao, preco, ativo) VALUES 
('Almôndegas com Arroz', 'Almôndegas caseiras, acompanhadas de arroz integral com sementes e legumes refogados.', 23.90, FALSE),
('Frango Teriyaki', 'Frango ao molho teriyaki, acompanhado de arroz integral com sementes e legumes refogados.', 23.90, FALSE),
('Guisado com Purê', 'Guisado perfeitamente temperado, acompanhado de purê de batata inglesa e legumes refogados.', 23.90, FALSE),
('Escondidinho de Frango', 'Delicioso escondidinho de aipim cremoso recheado com frango desfiado.', 23.90, FALSE);






-- Inserindo clientes fictícios de teste (Porto Alegre)

INSERT INTO clientes (nome, whatsapp, email, rua, numero, bairro, cidade, distancia_km) VALUES 
('Carlos Silva', '51999991111', 'carlos.silva@email.com', 'Avenida Protásio Alves', '2500', 'Petrópolis', 'Porto Alegre', 4.50),
('Mariana Souza', '51999992222', 'mariana.souza@email.com', 'Rua Padre Chagas', '120', 'Moinhos de Vento', 'Porto Alegre', 7.20);






-- Simulação de um Pedido Avulso (Carlos Silva comprando 3 marmitas)

-- 1. Inserimos o pedido na tabela mãe (Status começa como 'Pendente' via DEFAULT)
INSERT INTO pedidos_avulsos (cliente_id, valor_frete) 
VALUES (1, 10.00);

-- 2. Inserimos os itens do pedido na tabela pivô
-- Usamos 'currval' ou o ID manual do pedido. Como é o primeiro pedido do banco, o ID dele é 1.
INSERT INTO itens_pedido_avulso (pedido_id, produto_id, quantidade) VALUES 
(1, 1, 2), -- 2x Carne de Panela (produto_id 1) dentro do pedido 1
(1, 3, 1); -- 1x Frango Desfiado com Purê (produto_id 3) dentro do pedido 1





-- Simulação de Assinatura (Mariana Souza escolhendo o plano de 16 marmitas)

-- 1. Mariana contrata o plano de 16 marmitas (Saldo inicial começa cheio: 16)
INSERT INTO assinaturas (cliente_id, plano_marmitas, saldo_restante) 
VALUES (2, 16, 16);

-- 2. Mariana escolhe suas 4 marmitas para a entrega da primeira segunda-feira
-- Ela escolhe 2 de Carne de Panela (id 1) e 2 de Frango em Tiras (id 2)
INSERT INTO escolhas_assinante (cliente_id, produto_id, quantity) VALUES 
(2, 1, 2), 
(2, 2, 2);

-- 3. Atualizamos o saldo restante da Mariana (Tinha 16, gastou 4, sobra 12)
UPDATE assinaturas 
SET saldo_restante = 12 
WHERE cliente_id = 2;

