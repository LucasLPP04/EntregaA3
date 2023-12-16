import sqlite3
import tkinter as tk
from tkinter import messagebox
import database as sv

class StatisticsScreen(tk.Frame):
    def __init__(self, master, return_callback):
        super().__init__(master)
        self.master = master
        self.return_callback = return_callback

        self.master.title("Estatísticas")
        self.master.geometry("600x550")  # Definindo tamanho fixo para a janela


        # Título da página
        self.stats_title = tk.Label(self, text="Estatísticas:", font=("Helvetica", 20))
        self.stats_title.pack(pady=10)

        # Botões de relatórios
        self.most_sold_button = tk.Button(self, text="Produtos Mais Vendidos", command=self.generate_most_sold_report)
        self.most_sold_button.pack(pady=5)

        self.product_by_customer_button = tk.Button(self, text="Produto por Cliente", command=self.generate_product_by_customer_report)
        self.product_by_customer_button.pack(pady=5)

        self.average_consumption_button = tk.Button(self, text="Consumo Médio do Cliente", command=self.generate_average_consumption_report)
        self.average_consumption_button.pack(pady=5)

        self.low_stock_button = tk.Button(self, text="Produto com Baixo Estoque", command=self.generate_low_stock_report)
        self.low_stock_button.pack(pady=5)

        # Botão para voltar à tela inicial
        self.back_button = tk.Button(self, text="Voltar", command=self.return_to_home)
        self.back_button.pack(pady=10)

    def return_to_home(self):
        self.pack_forget()
        self.return_callback()

    def generate_most_sold_report(self):
        conn = sqlite3.connect('Gansos.db')
        cursor = conn.cursor()
        # Consultar o banco de dados para obter os produtos mais vendidos
        cursor.execute('''
            SELECT ProdutoNome, SUM(Quantidade) as TotalVendido
            FROM ItensCompra IC
            JOIN Estoque E ON IC.ProdutoID = E.ProdutoID
            GROUP BY IC.ProdutoID
            ORDER BY TotalVendido DESC
            LIMIT 5
        ''')
        result = cursor.fetchall()

        # Exibir os resultados em uma caixa de mensagem
        report_text = "Produtos Mais Vendidos:\n\n"
        for row in result:
            report_text += f"{row[0]} - Total Vendido: {row[1]}\n"

        messagebox.showinfo("Relatório de Produtos Mais Vendidos", report_text)
        conn.commit()
        conn.close()
        
    def generate_product_by_customer_report(self):
        conn = sqlite3.connect('Gansos.db')
        cursor = conn.cursor()
        # Consultar o banco de dados para obter a quantidade de cada produto comprado por cliente
        cursor.execute('''
            SELECT CL.ClienteNome, E.ProdutoNome, SUM(IC.Quantidade) as TotalComprado
            FROM ItensCompra IC
            JOIN Compras C ON IC.CompraID = C.CompraID
            JOIN Cliente CL ON C.ClienteID = CL.ClienteID
            JOIN Estoque E ON IC.ProdutoID = E.ProdutoID
            GROUP BY CL.ClienteID, IC.ProdutoID
        ''')
        result = cursor.fetchall()

        # Exibir os resultados em uma caixa de mensagem
        report_text = "Relatório de Produto por Cliente:\n\n"
        for row in result:
            report_text += f"{row[0]} comprou {row[2]} unidades de {row[1]}\n"

        messagebox.showinfo("Relatório de Produto por Cliente", report_text)
        conn.commit()
        conn.close()

    def generate_average_consumption_report(self):
        conn = sqlite3.connect('Gansos.db')
        cursor = conn.cursor()
        # Consultar o banco de dados para obter a média de consumo por cliente
        cursor.execute('''
            SELECT ClienteNome, AVG(Quantidade) as ConsumoMedio
            FROM (
                SELECT CL.ClienteNome, IC.Quantidade
                FROM ItensCompra IC
                JOIN Compras C ON IC.CompraID = C.CompraID
                JOIN Cliente CL ON C.ClienteID = CL.ClienteID
            )
            GROUP BY ClienteNome
        ''')
        result = cursor.fetchall()

        # Exibir os resultados em uma caixa de mensagem
        report_text = "Relatório de Consumo Médio do Cliente:\n\n"
        for row in result:
            report_text += f"{row[0]} - Consumo Médio: {row[1]:.2f} unidades\n"

        messagebox.showinfo("Relatório de Consumo Médio do Cliente", report_text)
        conn.commit()
        conn.close()

    def generate_low_stock_report(self):
        conn = sqlite3.connect('Gansos.db')
        cursor = conn.cursor()
        # Consultar o banco de dados para obter produtos com baixo estoque
        cursor.execute('''
            SELECT ProdutoNome, ProdutoQuantidade
            FROM Estoque
            WHERE ProdutoQuantidade < 10
        ''')
        result = cursor.fetchall()

        # Exibir os resultados em uma caixa de mensagem
        report_text = "Relatório de Produto com Baixo Estoque:\n\n"
        for row in result:
            report_text += f"{row[0]} - Quantidade em Estoque: {row[1]}\n"

        messagebox.showinfo("Relatório de Produto com Baixo Estoque", report_text)
        conn.commit()
        conn.close()

