import sqlite3
conn = sqlite3.connect('Gansos.db')
cursor = conn.cursor()

# Conectar ao banco de dados (se não existir, será criado)
def criarTabelas():
    conn = sqlite3.connect('Gansos.db')
    cursor = conn.cursor()
    
    # Tabela Estoque
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Estoque (
            ProdutoID INTEGER PRIMARY KEY,
            ProdutoNome TEXT NOT NULL,
            ProdutoPreco REAL NOT NULL,
            ProdutoQuantidade INTEGER NOT NULL,
            ProdutoQuantidadeVendida INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # Tabela Cliente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Cliente (
            ClienteID INTEGER PRIMARY KEY,
            ClienteNome TEXT NOT NULL,
            ComprasRealizadas INTEGER DEFAULT 0,
            ValorTotalGasto REAL DEFAULT 0.0,
            QuantidadeMediaProdutos REAL DEFAULT 0,
            ProdutoMaisComprado TEXT
        )
    ''')

    # Tabela Compras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Compras (
            CompraID INTEGER PRIMARY KEY,
            ClienteID INTEGER,
            ValorTotal REAL,
            FOREIGN KEY (ClienteID) REFERENCES Cliente(ClienteID)
        )
    ''')

    # Tabela ItensCompra
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ItensCompra (
            ItemID INTEGER PRIMARY KEY,
            CompraID INTEGER,
            ProdutoID INTEGER,
            Quantidade INTEGER,
            PrecoUnitario REAL,
            FOREIGN KEY (CompraID) REFERENCES Compras(CompraID),
            FOREIGN KEY (ProdutoID) REFERENCES Estoque(ProdutoID)
        )
    ''')

    # Salvar as alterações e fechar a conexão
    conn.commit()
    conn.close()

def criarProdutosInciais():
    conn = sqlite3.connect('Gansos.db')
    cursor = conn.cursor()
    # Verifica se existem produtos na tabela Estoque
    cursor.execute("SELECT COUNT(*) FROM Estoque")
    count = cursor.fetchone()[0]

    if count == 0:  # Se não houver produtos, adiciona os iniciais
        initial_products = [
            ("Leite", 3.80, 500),
            ("Queijo", 8.90, 600),
            ("Pão de forma", 9.20, 400),
            ("Manteiga", 14.80, 300),
            ("Sal", 2.60, 400),
            ("Coca Cola", 10.0, 500)
        ]
        
        cursor.executemany("INSERT INTO Estoque (ProdutoNome, ProdutoPreco, ProdutoQuantidade) VALUES (?, ?, ?)", initial_products)

    conn.commit()
    conn.close()

def criarClientesInciais():
    conn = sqlite3.connect('Gansos.db')
    cursor = conn.cursor()
    # Verifica se existem produtos na tabela Estoque
    cursor.execute("SELECT COUNT(*) FROM Cliente")
    count = cursor.fetchone()[0]

    if count == 0:  # Se não houver produtos, adiciona os iniciais
        initial_clients = [
            "Lucas Lopes",
            "Lucas Lima",
            "Vitor Albuquerque",
            "Wadson Daniel",
            "Henrique Moura",
            "Gustavo Santos",
            "Mariana Ferreira",
            "Clara Batista",
            "Enzo Araujo",
            "Ian Carlos"
        ]
        for cliente in initial_clients:
            cursor.execute("INSERT INTO Cliente (ClienteNome) VALUES (?)", (cliente,))
            
    conn.commit()
    conn.close()

# ---------- FUNÇÕES PARA REALIZAR UMA COMPRA ----------
def obter_cliente_id(nome_cliente):
    cursor.execute("SELECT ClienteID FROM Cliente WHERE ClienteNome=?", (nome_cliente,))
    result = cursor.fetchone()
    return result[0] if result else None

def adicionar_cliente(nome_cliente):
    cursor.execute("INSERT INTO Cliente (ClienteNome) VALUES (?)", (nome_cliente,))
    conn.commit()
    return cursor.lastrowid

def obter_produto_info(nome_produto):
    cursor.execute("SELECT ProdutoID, ProdutoPreco, ProdutoQuantidade, ProdutoQuantidadeVendida FROM Estoque WHERE ProdutoNome=?", (nome_produto,))
    return cursor.fetchone()

def registrar_compra(cliente_id, produto_id, quantidade, valor_total):
    cursor.execute("INSERT INTO Compras (ClienteID, ValorTotal) VALUES (?, ?)", (cliente_id, valor_total))
    compra_id = cursor.lastrowid
    cursor.execute("INSERT INTO ItensCompra (CompraID, ProdutoID, Quantidade, PrecoUnitario) VALUES (?, ?, ?, ?)", (compra_id, produto_id, quantidade, valor_total / quantidade))
    cursor.execute("UPDATE Estoque SET ProdutoQuantidadeVendida = ProdutoQuantidadeVendida + ? WHERE ProdutoID=?", (quantidade, produto_id))
    conn.commit()

def atualizar_estatisticas_cliente(cliente_id, valor_total, quantidade, produto_nome):
    cursor.execute("UPDATE Cliente SET ComprasRealizadas = ComprasRealizadas + 1, ValorTotalGasto = ValorTotalGasto + ?, QuantidadeMediaProdutos = (QuantidadeMediaProdutos * ComprasRealizadas + ?) / (ComprasRealizadas + 1), ProdutoMaisComprado = ? WHERE ClienteID=?", (valor_total, quantidade, produto_nome, cliente_id))
    conn.commit()

def atualizar_quantidade_estoque(produto_id, quantidade_comprada, quantidade_vendida):
    cursor.execute("UPDATE Estoque SET ProdutoQuantidade = ProdutoQuantidade - ?, ProdutoQuantidadeVendida = ProdutoQuantidadeVendida + ? WHERE ProdutoID=?", (quantidade_comprada, quantidade_vendida, produto_id))
    conn.commit()

# -------- FUNÇÃO PARA EXIBIR OS DADOS DA ULTIMA COMPRA --------
def obter_ultima_compra():
    cursor.execute('''
        SELECT C.CompraID, CL.ClienteNome, E.ProdutoNome, C.ValorTotal
        FROM Compras C
        JOIN Cliente CL ON C.ClienteID = CL.ClienteID
        JOIN ItensCompra IC ON C.CompraID = IC.CompraID
        JOIN Estoque E ON IC.ProdutoID = E.ProdutoID
        ORDER BY C.CompraID DESC
        LIMIT 1
    ''')
    return cursor.fetchone()
