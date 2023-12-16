import sqlite3
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
import database as sv
from clientes import ClientScreen
from estoque import StockScreen
from estatisticas import StatisticsScreen
#--------------TELA INICIAL---------------
class HomeScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Sistema de Vendas")
        self.master.geometry("600x550")  # Definindo tamanho fixo para a janela principal

        image_path = "src/gansosLogo.png"
        self.logo_image = tk.PhotoImage(file=image_path)

        self.logo_label = tk.Label(self, image=self.logo_image)
        self.logo_label.pack(pady=10)
        
        self.logo_label = tk.Label(self, text="Gansos", font=("Helvetica", 20))
        self.logo_label.pack()

        # Última Compra
        self.last_purchase_frame = tk.Frame(self, bd=2, relief=tk.GROOVE)
        self.last_purchase_frame.pack(pady=20)

        self.last_purchase_label = tk.Label(self.last_purchase_frame, text="Última Compra", font=("Helvetica", 16))
        self.last_purchase_label.grid(row=0, column=0, pady=10)

        self.customer_label = tk.Label(self.last_purchase_frame, text="Cliente: ")
        self.customer_label.grid(row=1, column=0, padx=10, pady=5, sticky="W")

        self.products_label = tk.Label(self.last_purchase_frame, text="Produtos: ")
        self.products_label.grid(row=2, column=0, padx=10, pady=5, sticky="W")

        self.total_label = tk.Label(self.last_purchase_frame, text="Total: ")
        self.total_label.grid(row=3, column=0, padx=10, pady=5, sticky="W")

        # Botões
        self.new_sale_button = tk.Button(self, text="Nova Venda", command=self.new_sale)
        self.new_sale_button.pack(pady=16)

        self.custom_sale_button = tk.Button(self, text="Venda Personalizada", command=self.compra_personalizada)
        self.custom_sale_button.pack(pady=4)

        # Botões Inferiores
        self.clients_button = tk.Button(self, text="Clientes", command=self.show_clients)
        self.clients_button.pack(side=tk.RIGHT, padx=3, pady=10)

        self.stock_button = tk.Button(self, text="Estoque", command=self.show_stock)
        self.stock_button.pack(side=tk.RIGHT, padx=3, pady=10)

        self.stats_button = tk.Button(self, text="Estatísticas", command=self.show_stats)
        self.stats_button.pack(side=tk.RIGHT, padx=3, pady=10)

        self.preencher_ultima_compra()

    def preencher_ultima_compra(self):
        # Obter informações da última compra no banco de dados
        ultima_compra_info = sv.obter_ultima_compra()

        if ultima_compra_info is not None:
            compra_id, cliente_nome, produto_nome, total = ultima_compra_info

            # Preencher os rótulos com as informações da última compra
            self.customer_label.config(text=f"Cliente: {cliente_nome}")
            self.products_label.config(text=f"Produto: {produto_nome}")
            self.total_label.config(text=f"Total: R${total:.2f}")
        else:
            # Se não houver última compra, limpar os rótulos
            self.customer_label.config(text="Cliente: ")
            self.products_label.config(text="Produto: ")
            self.total_label.config(text="Total: ")

    def new_sale(self):
        self.nova_venda_aleatoria()
        # Atualizar informações da última compra
        self.preencher_ultima_compra()

    def compra_personalizada(self):
        # Pedir informações ao usuário

        cliente_nome = simpledialog.askstring("Compra Personalizada", "Digite o nome do cliente:")
        produto_nome = simpledialog.askstring("Compra Personalizada", "Digite o nome do produto:")
        quantidade = simpledialog.askinteger("Compra Personalizada", "Digite a quantidade desejada:")
        
        # Verificar se o cliente já existe no banco de dados
        cliente_id = sv.obter_cliente_id(cliente_nome)

        if cliente_id is None:
            # Se o cliente não existe, criar um novo registro
            cliente_id = sv.adicionar_cliente(cliente_nome)

        # Obter informações do produto
        produto_info = sv.obter_produto_info(produto_nome)

        if produto_info is None:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return

        produto_id, produto_preco, produto_quantidade, produto_quantidade_vendida = produto_info

        # Calcular o valor total da compra
        valor_total = quantidade * produto_preco

        # Exibir o valor total e confirmar a compra
        confirmacao = messagebox.askyesno("Confirmação de Compra", f"Cliente: {cliente_nome}\nProduto: {produto_nome}\nQuantidade: {quantidade}\nValor Total: {valor_total:.2f}\nConfirmar compra?")

        if confirmacao:
            # Atualizar dados no banco de dados
            sv.registrar_compra(cliente_id, produto_id, quantidade, valor_total)

            # Atualizar estatísticas do cliente
            sv.atualizar_estatisticas_cliente(cliente_id, valor_total, quantidade, produto_nome)

            # Atualizar quantidade no estoque
            sv.atualizar_quantidade_estoque(produto_id, quantidade, produto_quantidade_vendida)

            messagebox.showinfo("Compra Realizada", "Compra registrada com sucesso.")
            self.preencher_ultima_compra()

    def nova_venda_aleatoria(self):
        conn = sqlite3.connect('Gansos.db')
        cursor = conn.cursor()

        # Obter uma lista de todos os clientes
        cursor.execute("SELECT ClienteNome FROM Cliente")
        clientes = [cliente[0] for cliente in cursor.fetchall()]

        # Obter uma lista de todos os produtos no estoque
        cursor.execute("SELECT ProdutoNome FROM Estoque")
        produtos = [produto[0] for produto in cursor.fetchall()]

        # Escolher aleatoriamente um cliente, produto e quantidade
        cliente_aleatorio = random.choice(clientes)
        produto_aleatorio = random.choice(produtos)
        quantidade_aleatoria = random.randint(1, 5)

        # Obter informações do produto escolhido
        produto_info = sv.obter_produto_info(produto_aleatorio)

        if produto_info is not None:
            produto_id, produto_preco, produto_quantidade, produto_quantidade_vendida = produto_info
            valor_total = quantidade_aleatoria * produto_preco

            # Exibir informações e pedir confirmação
            confirmacao = messagebox.askyesno("Confirmação de Nova Venda",
                                            f"Cliente: {cliente_aleatorio}\nProduto: {produto_aleatorio}\nQuantidade: {quantidade_aleatoria}\nValor Total: {valor_total:.2f}\nConfirmar venda?")

            if confirmacao:
                # Registra a nova venda aleatória
                cliente_id = sv.obter_cliente_id(cliente_aleatorio)

                if cliente_id is None:
                    cliente_id = sv.adicionar_cliente(cliente_aleatorio)

                sv.registrar_compra(cliente_id, produto_id, quantidade_aleatoria, valor_total)
                sv.atualizar_estatisticas_cliente(cliente_id, valor_total, quantidade_aleatoria, produto_aleatorio)
                sv.atualizar_quantidade_estoque(produto_id, quantidade_aleatoria, produto_quantidade_vendida)

                messagebox.showinfo("Nova Venda Aleatória", "Venda registrada com sucesso.")
        conn.commit()
        conn.close()

    def show_clients(self):
        self.pack_forget()

        # Mostrar a tela de estoque
        client_screen = ClientScreen(self.master, self.return_to_home)
        client_screen.pack()

    def show_stock(self):
        # Esconder a tela inicial
        self.pack_forget()

        # Mostrar a tela de estoque
        stock_screen = StockScreen(self.master, self.return_to_home)
        stock_screen.pack()

    def return_to_home(self):
        # Esconder a tela de estoque
        self.pack()

    def show_stats(self):
        self.pack_forget()

        # Mostrar a tela de estatísticas
        stats_screen = StatisticsScreen(self.master, self.return_to_home)
        stats_screen.pack()

sv.criarTabelas()
sv.criarProdutosInciais()
sv.criarClientesInciais()

# Criar a janela principal
root = tk.Tk()
app = HomeScreen(root)
app.pack(fill=tk.BOTH, expand=True)
root.mainloop()