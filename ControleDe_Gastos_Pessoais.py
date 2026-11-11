
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import json
from datetime import datetime
import os

# NOME DO ARQUIVO ONDE OS DADOS SERÃO SALVOS
ARQUIVO = "movimentacoes.json"

# Lista que guarda todas as movimentações
movimentacoes = []


janela = tk.Tk()
janela.title("Controle de Gastos Pessoais")
janela.geometry("800x620")
janela.resizable(False, False)

# TÍTULO
titulo = tk.Label(
    janela,
    text="CONTROLE DE GASTOS PESSOAIS",
    font=("Arial", 18, "bold")
)
titulo.pack(pady=15)

# FUNÇÃO PARA CARREGAR OS DADOS
def carregar_dados():
    global movimentacoes

    if os.path.exists(ARQUIVO):
        arquivo = open(ARQUIVO, "r", encoding="utf-8")
        movimentacoes = json.load(arquivo)
        arquivo.close()
    else:
        movimentacoes = []
        salvar_dados()


# FUNÇÃO PARA SALVAR OS DADOS
def salvar_dados():
    arquivo = open(ARQUIVO, "w", encoding="utf-8")
    json.dump(movimentacoes, arquivo, indent=4, ensure_ascii=False)
    arquivo.close()


# FUNÇÃO PARA CALCULAR O SALDO
def calcular_saldo():
    saldo = 0

    for item in movimentacoes:
        if item["tipo"] == "Receita":
            saldo = saldo + item["valor"]
        else:
            saldo = saldo - item["valor"]

    return saldo


# FUNÇÃO PARA ATUALIZAR OS VALORES NA TELA
def atualizar_tela():
    total_receitas = 0
    total_despesas = 0

    for item in movimentacoes:
        if item["tipo"] == "Receita":
            total_receitas = total_receitas + item["valor"]
        else:
            total_despesas = total_despesas + item["valor"]

    saldo = calcular_saldo()

    texto_receitas.config(
        text=f"Receitas: R$ {total_receitas:.2f}"
    )

    texto_despesas.config(
        text=f"Despesas: R$ {total_despesas:.2f}"
    )

    texto_saldo.config(
        text=f"Saldo atual: R$ {saldo:.2f}"
    )


# FUNÇÃO PARA ADICIONAR RECEITA OU DESPESA
def adicionar_movimentacao(tipo):

    descricao = simpledialog.askstring(
        "Descrição",
        "Digite a descrição da movimentação:"
    )

    if descricao is None:
        return

    if descricao.strip() == "":
        messagebox.showerror("Erro", "Digite uma descrição!")
        return

    valor = simpledialog.askstring(
        "Valor",
        "Digite o valor da movimentação:"
    )

    if valor is None:
        return

    try:
        valor = float(valor.replace(",", "."))
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor válido!")
        return

    if valor <= 0:
        messagebox.showerror(
            "Erro",
            "O valor deve ser maior que zero!"
        )
        return

    # Criando um identificador para a movimentação
    identificador = 1

    for item in movimentacoes:
        if item["id"] >= identificador:
            identificador = item["id"] + 1

    # Criando o dicionário da movimentação
    nova_movimentacao = {
        "id": identificador,
        "tipo": tipo,
        "descricao": descricao,
        "valor": valor,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    movimentacoes.append(nova_movimentacao)

    salvar_dados()
    atualizar_tela()
    listar_movimentacoes()

    messagebox.showinfo(
        "Sucesso",
        tipo + " cadastrada com sucesso!"
    )


# FUNÇÃO PARA LISTAR AS MOVIMENTAÇÕES
def listar_movimentacoes():

    for item in tabela.get_children():
        tabela.delete(item)

    for item in movimentacoes:
        tabela.insert(
            "",
            "end",
            values=(
                item["id"],
                item["tipo"],
                item["descricao"],
                f"R$ {item['valor']:.2f}",
                item["data"]
            )
        )


# FUNÇÃO PARA EXCLUIR UMA MOVIMENTAÇÃO
def excluir_movimentacao():

    identificador = simpledialog.askinteger(
        "Excluir movimentação",
        "Digite o ID da movimentação que deseja excluir:"
    )

    if identificador is None:
        return

    encontrado = False

    for item in movimentacoes:
        if item["id"] == identificador:
            movimentacoes.remove(item)
            encontrado = True
            break

    if encontrado:
        salvar_dados()
        atualizar_tela()
        listar_movimentacoes()

        messagebox.showinfo(
            "Sucesso",
            "Movimentação excluída!"
        )
    else:
        messagebox.showerror(
            "Erro",
            "Movimentação não encontrada!"
        )


# FUNÇÃO PARA GERAR O RELATÓRIO
def gerar_relatorio():

    total_receitas = 0
    total_despesas = 0

    for item in movimentacoes:
        if item["tipo"] == "Receita":
            total_receitas = total_receitas + item["valor"]
        else:
            total_despesas = total_despesas + item["valor"]

    saldo = calcular_saldo()
    quantidade = len(movimentacoes)

    relatorio = (
        f"TOTAL DE RECEITAS: R$ {total_receitas:.2f}\n\n"
        f"TOTAL DE DESPESAS: R$ {total_despesas:.2f}\n\n"
        f"SALDO ATUAL: R$ {saldo:.2f}\n\n"
        f"QUANTIDADE DE MOVIMENTAÇÕES: {quantidade}"
    )

    messagebox.showinfo("Relatório Financeiro", relatorio)

# ÁREA DOS VALORES
texto_receitas = tk.Label(
    janela,
    text="Receitas: R$ 0.00",
    font=("Arial", 12, "bold"),
    fg="green"
)
texto_receitas.pack()

texto_despesas = tk.Label(
    janela,
    text="Despesas: R$ 0.00",
    font=("Arial", 12, "bold"),
    fg="red"
)
texto_despesas.pack()

texto_saldo = tk.Label(
    janela,
    text="Saldo atual: R$ 0.00",
    font=("Arial", 15, "bold")
)
texto_saldo.pack(pady=10)


# BOTÕES DO SISTEMA
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=10)

botao_receita = tk.Button(
    frame_botoes,
    text="Adicionar Receita",
    width=18,
    command=lambda: adicionar_movimentacao("Receita")
)
botao_receita.grid(row=0, column=0, padx=5)

botao_despesa = tk.Button(
    frame_botoes,
    text="Adicionar Despesa",
    width=18,
    command=lambda: adicionar_movimentacao("Despesa")
)
botao_despesa.grid(row=0, column=1, padx=5)

botao_excluir = tk.Button(
    frame_botoes,
    text="Excluir Movimentação",
    width=18,
    command=excluir_movimentacao
)
botao_excluir.grid(row=0, column=2, padx=5)

botao_relatorio = tk.Button(
    frame_botoes,
    text="Gerar Relatório",
    width=18,
    command=gerar_relatorio
)
botao_relatorio.grid(row=0, column=3, padx=5)


# TABELA DE MOVIMENTAÇÕES
colunas = (
    "ID",
    "Tipo",
    "Descrição",
    "Valor",
    "Data/Hora"
)

tabela = ttk.Treeview(
    janela,
    columns=colunas,
    show="headings",
    height=15
)

for coluna in colunas:
    tabela.heading(coluna, text=coluna)

tabela.column("ID", width=45, anchor="center")
tabela.column("Tipo", width=100, anchor="center")
tabela.column("Descrição", width=200)
tabela.column("Valor", width=120, anchor="center")
tabela.column("Data/Hora", width=180, anchor="center")

tabela.pack(pady=20)


# BOTÃO PARA SAIR
botao_sair = tk.Button(
    janela,
    text="Sair",
    width=15,
    bg="red",
    command=janela.destroy
)
botao_sair.pack()


# INICIANDO O PROGRAMA
carregar_dados()
atualizar_tela()
listar_movimentacoes()

janela.mainloop()