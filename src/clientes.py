import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import database as sv

class ClientScreen(tk.Frame):
    def __init__(self, master, return_callback):
        super().__init__(master)
        self.master = master
        self.return_callback = return_callback

        self.master.title("Clientes")
        self.master.geometry("600x550")  # Definindo tamanho fixo para a janela

        self.client_title = tk.Label(self, text="Clientes:", font=("Helvetica", 20))
        self.client_title.pack(pady=10)

        # Lista de clientes
        self.client_list_frame = tk.Frame(self)
        self.client_list_frame.pack(pady=20)

        # Preencher a lista de clientes
        self.populate_client_list()

        # Botão para adicionar novo cliente
        self.add_button = tk.Button(self, text="Adicionar Cliente", bg="green", fg="white", command=self.add_client)
        self.add_button.pack()

        # Botão para voltar à tela inicial
        self.back_button = tk.Button(self, text="Voltar", command=self.return_to_home)
        self.back_button.pack(pady=10)

    def return_to_home(self):
        self.pack_forget()
        self.return_callback()

    def populate_client_list(self):
        # Conectar ao banco de dados
        conn = sqlite3.connect('Gansos.db')
        cursor = conn.cursor()

        # Selecionar todos os clientes
        cursor.execute('SELECT ClienteID, ClienteNome, ComprasRealizadas, ValorTotalGasto FROM Cliente')
        clients = cursor.fetchall()

        # Criar um widget Canvas para a lista de clientes
        canvas = tk.Canvas(self.client_list_frame, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.configure(width=370, height=360)

        # Adicionar uma barra de rolagem vertical ao Canvas
        scrollbar = tk.Scrollbar(self.client_list_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Criar um Frame para conter os widgets de clientes
        client_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=client_frame, anchor=tk.NW)

        # Adicionar clientes à lista com linhas entre eles
        for i, client in enumerate(clients):
            client_nome = f"Nome: {client[1]}"
            client_info = f"Compras realizadas: {client[2]} | Total gasto: R$ {client[3]:.2f}"

            # Adicionar uma linha após o primeiro cliente
            if i > 0:
                line = tk.Frame(client_frame, height=1, bg="gray", relief=tk.SUNKEN)
                line.pack(fill=tk.X, padx=10, pady=5)

            client_item_frame = tk.Frame(client_frame, bg="white")
            client_item_frame.pack(fill=tk.X, padx=10, pady=5)

            client_label = tk.Label(client_item_frame, bg="white", text=client_nome, font=("Helvetica", 12, "bold"), justify=tk.CENTER)
            client_label.pack(pady=5)
            client_label = tk.Label(client_item_frame, bg="white", text=client_info, font=("Helvetica", 12), justify=tk.CENTER)
            client_label.pack(pady=5)
            # Botões de edição e exclusão
            edit_button = tk.Button(client_item_frame, text="Editar", justify=tk.CENTER, command=lambda cli_id=client[0]: self.edit_client(cli_id))
            edit_button.pack(side=tk.RIGHT, padx=3)

            delete_button = tk.Button(client_item_frame, text="Excluir", bg="red", fg="white", justify=tk.CENTER, command=lambda cli_id=client[0]: self.delete_client(cli_id))
            delete_button.pack(side=tk.RIGHT, padx=3)

        # Configurar a barra de rolagem para rolar com o Canvas
        client_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

        # Configurar a função de rolagem ao usar a roda do mouse
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        # Fechar a conexão
        conn.close()

    def add_client(self):
        client_name = simpledialog.askstring("Adicionar Cliente", "Digite o nome do cliente:")

        if client_name:
            conn = sqlite3.connect('Gansos.db')
            cursor = conn.cursor()

            # Inserir novo cliente
            cursor.execute('INSERT INTO Cliente (ClienteNome) VALUES (?)', (client_name,))
            conn.commit()

            conn.close()
            messagebox.showinfo("Adcicionar Cliente", "Cliente adicionado com sucesso")
            # Atualizar a lista de clientes
            self.clear_client_list()
            self.populate_client_list()

    def edit_client(self, client_id):
        new_name = simpledialog.askstring("Editar Cliente", "Novo nome para o cliente:")

        if new_name:
            conn = sqlite3.connect('Gansos.db')
            cursor = conn.cursor()

            # Atualizar informações do cliente
            cursor.execute('UPDATE Cliente SET ClienteNome = ? WHERE ClienteID = ?', (new_name, client_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Editar Cliente", "Cliente editado com sucesso")

            # Atualizar a lista de clientes
            self.clear_client_list()
            self.populate_client_list()

    def delete_client(self, client_id):
        response = messagebox.askquestion("Excluir Cliente", "Tem certeza que deseja excluir este cliente?")
        if response == 'yes':
            conn = sqlite3.connect('Gansos.db')
            cursor = conn.cursor()

            # Excluir cliente
            cursor.execute('DELETE FROM Cliente WHERE ClienteID = ?', (client_id,))
            conn.commit()

            conn.close()
            messagebox.showinfo("Deletar Cliente", "Cliente deletado com sucesso")
            # Atualizar a lista de clientes
            self.clear_client_list()
            self.populate_client_list()

    def clear_client_list(self):
        for widget in self.client_list_frame.winfo_children():
            widget.destroy()