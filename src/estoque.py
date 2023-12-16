import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import database as sv

class StockScreen(tk.Frame):
    def __init__(self, master, return_callback):
        super().__init__(master)
        self.master = master
        self.return_callback = return_callback

        self.master.title("Estoque")
        self.master.geometry("600x550")  # Definindo tamanho fixo para a janela

        self.estoque_title = tk.Label(self, text="Estoque:", font=("Helvetica", 20))
        self.estoque_title.pack(pady=10)

        # Lista de produtos
        self.product_list_frame = tk.Frame(self)
        self.product_list_frame.pack(pady=20)

        # Preencher a lista de produtos
        self.populate_product_list()

        # Botão para adicionar novo produto
        self.add_button = tk.Button(self, text="Adicionar Produto", bg="green", fg="white", command=self.add_product)
        self.add_button.pack()

        # Botão para voltar à tela inicial
        self.back_button = tk.Button(self, text="Voltar", command=self.return_to_home)
        self.back_button.pack(pady=10)

    def return_to_home(self):
        self.pack_forget()
        self.return_callback()

    def populate_product_list(self):
        # Conectar ao banco de dados
        conn = sqlite3.connect('Gansos.db')
        cursor = conn.cursor()

        # Selecionar todos os produtos
        cursor.execute('SELECT ProdutoID, ProdutoNome, ProdutoQuantidade, ProdutoPreco FROM Estoque')
        products = cursor.fetchall()

        # Adicionar produtos à lista com linhas entre eles
        # Criar um widget Canvas para a lista de produtos
        canvas = tk.Canvas(self.product_list_frame, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.configure(width=460,height=360)

        # Adicionar uma barra de rolagem vertical ao Canvas
        scrollbar = tk.Scrollbar(self.product_list_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Criar um Frame para conter os widgets de produtos
        product_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=product_frame, anchor=tk.NW)

        # Adicionar produtos à lista com linhas entre eles
        for i, product in enumerate(products):
            product_info = f"{product[1]} - Quantidade: {product[2]} - Preço: R$ {product[3]:.2f}"

            # Adicionar uma linha após o primeiro produto
            if i > 0:
                line = tk.Frame(product_frame, height=1, bg="gray", relief=tk.SUNKEN)
                line.pack(fill=tk.X, padx=10, pady=5)

            product_item_frame = tk.Frame(product_frame, bg="white")
            product_item_frame.pack(fill=tk.X, padx=10, pady=5)

            product_label = tk.Label(product_item_frame, bg="white", text=product_info, font=("Helvetica", 12, "bold"), justify=tk.CENTER)
            product_label.pack(pady=5)

            # Botões de edição e exclusão
            edit_button = tk.Button(product_item_frame, text="Editar", justify=tk.CENTER, command=lambda prod_id=product[0]: self.edit_product(prod_id))
            edit_button.pack(side=tk.RIGHT, padx=3)

            delete_button = tk.Button(product_item_frame, text="Excluir", bg="red", fg="white", justify=tk.CENTER, command=lambda prod_id=product[0]: self.delete_product(prod_id))
            delete_button.pack(side=tk.RIGHT, padx=3)

        # Configurar a barra de rolagem para rolar com o Canvas
        product_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

        # Configurar a função de rolagem ao usar a roda do mouse
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

        # Fechar a conexão
        conn.close()

    def add_product(self):
        product_name = simpledialog.askstring("Adicionar Produto", "Digite o nome do produto:")
        product_quantity = simpledialog.askinteger("Adicionar Produto", "Digite a quantidade do produto:")
        product_price = simpledialog.askfloat("Adicionar Produto", "Digite o preço do produto:")

        if product_name and product_quantity is not None and product_price is not None:
            conn = sqlite3.connect('Gansos.db')
            cursor = conn.cursor()

            # Inserir novo produto
            cursor.execute('INSERT INTO Estoque (ProdutoNome, ProdutoQuantidade, ProdutoPreco) VALUES (?, ?, ?)',
                           (product_name, product_quantity, product_price))
            conn.commit()

            conn.close()
            messagebox.showinfo("Adicionar Produto", "Produto adicionado com sucesso")
            # Atualizar a lista de produtos
            self.clear_product_list()
            self.populate_product_list()

    def edit_product(self, product_id):
        attribute_choice = simpledialog.askstring("Escolher Atributo", "Escolha o atributo a ser editado (nome, quantidade, preço):")
        if attribute_choice:
            attribute_choice = attribute_choice.lower()  # Converter para minúsculas para facilitar comparação

            valid_attributes = ['nome', 'quantidade', 'preço']
            if attribute_choice in valid_attributes:
                conn = sqlite3.connect('Gansos.db')
                cursor = conn.cursor()

                # Selecionar informações do produto para edição
                cursor.execute('SELECT ProdutoNome, ProdutoQuantidade, ProdutoPreco FROM Estoque WHERE ProdutoID = ?', (product_id,))
                product_info = cursor.fetchone()

                conn.close()

                if product_info:
                    # Mostrar a tela de edição com o valor antigo e um espaço para o novo valor
                    old_value = product_info[valid_attributes.index(attribute_choice)]  # Obter o valor antigo do atributo escolhido
                    new_value = simpledialog.askstring("Editar Produto", f"Novo valor para {attribute_choice.capitalize()}:",
                                                       initialvalue=str(old_value))

                    if new_value is not None:
                        conn = sqlite3.connect('Gansos.db')
                        cursor = conn.cursor()

                        # Atualizar informações do produto com base no atributo escolhido
                        if attribute_choice == 'nome':
                            cursor.execute('UPDATE Estoque SET ProdutoNome = ? WHERE ProdutoID = ?', (new_value, product_id))
                        elif attribute_choice == 'quantidade':
                            cursor.execute('UPDATE Estoque SET ProdutoQuantidade = ? WHERE ProdutoID = ?', (new_value, product_id))
                        elif attribute_choice == 'preço':
                            cursor.execute('UPDATE Estoque SET ProdutoPreco = ? WHERE ProdutoID = ?', (new_value, product_id))
                        messagebox.showinfo("Editar Produto", "Produto editado com sucesso")
                        conn.commit()
                        conn.close()

                        # Atualizar a lista de produtos
                        self.clear_product_list()
                        self.populate_product_list()
            else:
                messagebox.showwarning("Atributo Inválido", "Escolha um atributo válido (nome, quantidade, preço).")

    def delete_product(self, product_id):
        response = messagebox.askquestion("Excluir Produto", "Tem certeza que deseja excluir este produto?")
        if response == 'yes':
            conn = sqlite3.connect('Gansos.db')
            cursor = conn.cursor()

            # Excluir produto
            cursor.execute('DELETE FROM Estoque WHERE ProdutoID = ?', (product_id,))
            conn.commit()
            messagebox.showinfo("Deletar Produto", "Produto deletado com sucesso")
            conn.close()

            # Atualizar a lista de produtos
            self.clear_product_list()
            self.populate_product_list()


    def clear_product_list(self):
        for widget in self.product_list_frame.winfo_children():
            widget.destroy()