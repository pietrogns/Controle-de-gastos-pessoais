import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

ARQUIVO = "movimentacoes.json"

ROXO = "#5B21D6"
ROXO_ESCURO = "#4A18B0"
FUNDO = "#EAF0FA"
BRANCO = "#FFFFFF"
VERDE = "#43A047"
VERMELHO = "#E53935"
AZUL = "#1E88E5"
CINZA = "#9AA5B8"
TEXTO = "#1F2A44"


# ---------------------------------------------------------------
# Persistência (JSON)
# ---------------------------------------------------------------
def carregar_dados():
    """Carrega o JSON; se o arquivo não existir, cria um vazio."""
    if not os.path.exists(ARQUIVO):
        salvar_dados([])
        return []
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        messagebox.showwarning("Aviso", "Arquivo corrompido. Um novo será criado.")
        salvar_dados([])
        return []


def salvar_dados(movimentacoes):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(movimentacoes, f, ensure_ascii=False, indent=4)


# ---------------------------------------------------------------
# Regras de negócio
# ---------------------------------------------------------------
def proximo_id(movimentacoes):
    return max((m["id"] for m in movimentacoes), default=0) + 1


def converter_valor(texto):
    """Converte texto em float. Retorna None se inválido, negativo ou zero."""
    try:
        valor = float(texto.strip().replace("R$", "").replace(".", "").replace(",", ".")
                      if "," in texto else texto.strip())
    except ValueError:
        return None
    return valor if valor > 0 else None


def validar_data(texto):
    try:
        datetime.strptime(texto.strip(), "%d/%m/%Y %H:%M")
        return True
    except ValueError:
        return False


def adicionar_movimentacao(movimentacoes, descricao, valor, tipo, data):
    mov = {
        "id": proximo_id(movimentacoes),
        "descricao": descricao,
        "valor": round(valor, 2),
        "tipo": tipo,
        "data": data,
    }
    movimentacoes.append(mov)
    salvar_dados(movimentacoes)
    return mov


def excluir_movimentacao(movimentacoes, id_mov):
    for m in movimentacoes:
        if m["id"] == id_mov:
            movimentacoes.remove(m)
            salvar_dados(movimentacoes)
            return True
    return False


def total_por_tipo(movimentacoes, tipo):
    return sum(m["valor"] for m in movimentacoes if m["tipo"] == tipo)


def calcular_saldo(movimentacoes):
    return total_por_tipo(movimentacoes, "Receita") - total_por_tipo(movimentacoes, "Despesa")


def moeda(valor):
    texto = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-R$ {texto}" if valor < 0 else f"R$ {texto}"


# ---------------------------------------------------------------
# Interface
# ---------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Controle Financeiro Pessoal")
        self.geometry("1050x650")
        self.minsize(950, 600)
        self.configure(bg=FUNDO)

        self.movimentacoes = carregar_dados()

        self._estilo()
        self._montar_menu_lateral()

        self.area = tk.Frame(self, bg=FUNDO)
        self.area.pack(side="left", fill="both", expand=True, padx=25, pady=20)

        self.mostrar_dashboard()

    # ---------- estilo ----------
    def _estilo(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", rowheight=28, font=("Segoe UI", 10),
                    background=BRANCO, fieldbackground=BRANCO, borderwidth=0)
        s.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                    background=FUNDO, foreground=TEXTO)
        s.map("Treeview", background=[("selected", ROXO)])

    # ---------- menu lateral (as 7 opções) ----------
    def _montar_menu_lateral(self):
        lateral = tk.Frame(self, bg=ROXO, width=210)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)

        tk.Label(lateral, text="▮▮▮  Finanças", bg=ROXO, fg="white",
                 font=("Segoe UI", 15, "bold")).pack(pady=(25, 30))

        opcoes = [
            ("＋  Adicionar Receita", lambda: self.mostrar_formulario("Receita")),
            ("－  Adicionar Despesa", lambda: self.mostrar_formulario("Despesa")),
            ("☰  Listar Movimentações", self.mostrar_lista),
            ("◔  Consultar Saldo", self.mostrar_dashboard),
            ("✖  Excluir Movimentação", self.mostrar_exclusao),
            ("📄  Gerar Relatório", self.mostrar_relatorio),
            ("⏻  Sair", self.sair),
        ]
        for texto, comando in opcoes:
            b = tk.Button(lateral, text=texto, command=comando, anchor="w",
                          bg=ROXO, fg="white", activebackground=ROXO_ESCURO,
                          activeforeground="white", relief="flat", bd=0,
                          font=("Segoe UI", 11), padx=20, pady=10, cursor="hand2")
            b.pack(fill="x")

    def limpar_area(self):
        for w in self.area.winfo_children():
            w.destroy()

    def titulo(self, texto):
        tk.Label(self.area, text=texto, bg=FUNDO, fg=TEXTO,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 15))

    # ---------- componentes ----------
    def card(self, pai, titulo, valor, cor, col):
        c = tk.Frame(pai, bg=BRANCO, padx=15, pady=12,
                     highlightbackground="#DDE4F0", highlightthickness=1)
        c.grid(row=0, column=col, padx=6, sticky="ew")
        pai.grid_columnconfigure(col, weight=1)
        tk.Label(c, text=titulo, bg=BRANCO, fg=CINZA,
                 font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(c, text=valor, bg=BRANCO, fg=cor,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")

    def cards_resumo(self):
        linha = tk.Frame(self.area, bg=FUNDO)
        linha.pack(fill="x", pady=(0, 15))
        saldo = calcular_saldo(self.movimentacoes)
        self.card(linha, "Saldo atual", moeda(saldo), AZUL if saldo >= 0 else VERMELHO, 0)
        self.card(linha, "Receitas", moeda(total_por_tipo(self.movimentacoes, "Receita")), VERDE, 1)
        self.card(linha, "Despesas", moeda(total_por_tipo(self.movimentacoes, "Despesa")), VERMELHO, 2)
        self.card(linha, "Movimentações", str(len(self.movimentacoes)), ROXO, 3)

    def grafico_rosca(self, pai, receitas, despesas):
        cv = tk.Canvas(pai, width=260, height=260, bg=BRANCO, highlightthickness=0)
        x0, y0, x1, y1 = 30, 30, 230, 230
        total = receitas + despesas
        if total == 0:
            cv.create_arc(x0, y0, x1, y1, start=0, extent=359.9,
                          style="arc", width=36, outline="#DDE4F0")
        else:
            ext_rec = receitas / total * 360
            ext_des = 360 - ext_rec
            if ext_rec > 0:
                cv.create_arc(x0, y0, x1, y1, start=90, extent=min(ext_rec, 359.9),
                              style="arc", width=36, outline=VERDE)
            if ext_des > 0:
                cv.create_arc(x0, y0, x1, y1, start=90 + ext_rec, extent=min(ext_des, 359.9),
                              style="arc", width=36, outline=VERMELHO)
        cv.create_text(130, 122, text="Saldo", fill=CINZA, font=("Segoe UI", 9))
        saldo = receitas - despesas
        cv.create_text(130, 145, text=moeda(saldo), fill=TEXTO, font=("Segoe UI", 12, "bold"))
        return cv

    def tabela(self, pai, dados, altura=12):
        cols = ("id", "data", "tipo", "descricao", "valor")
        tv = ttk.Treeview(pai, columns=cols, show="headings", height=altura)
        for c, t, w in (("id", "ID", 50), ("data", "Data/Hora", 140), ("tipo", "Tipo", 90),
                        ("descricao", "Descrição", 260), ("valor", "Valor", 120)):
            tv.heading(c, text=t)
            tv.column(c, width=w, anchor="w" if c == "descricao" else "center")
        tv.tag_configure("Receita", foreground=VERDE)
        tv.tag_configure("Despesa", foreground=VERMELHO)
        for m in dados:
            tv.insert("", "end", values=(m["id"], m["data"], m["tipo"],
                                         m["descricao"], moeda(m["valor"])), tags=(m["tipo"],))
        return tv

    # ---------- telas ----------
    def mostrar_dashboard(self):
        self.limpar_area()
        self.titulo("Dashboard")
        self.cards_resumo()

        corpo = tk.Frame(self.area, bg=FUNDO)
        corpo.pack(fill="both", expand=True)

        esq = tk.Frame(corpo, bg=BRANCO, padx=15, pady=10)
        esq.pack(side="left", fill="y", padx=(0, 10))
        tk.Label(esq, text="Receitas x Despesas", bg=BRANCO, fg=TEXTO,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        rec = total_por_tipo(self.movimentacoes, "Receita")
        des = total_por_tipo(self.movimentacoes, "Despesa")
        self.grafico_rosca(esq, rec, des).pack()
        leg = tk.Frame(esq, bg=BRANCO)
        leg.pack()
        tk.Label(leg, text="● Receitas", fg=VERDE, bg=BRANCO).pack(side="left", padx=8)
        tk.Label(leg, text="● Despesas", fg=VERMELHO, bg=BRANCO).pack(side="left", padx=8)

        dir_ = tk.Frame(corpo, bg=BRANCO, padx=15, pady=10)
        dir_.pack(side="left", fill="both", expand=True)
        tk.Label(dir_, text="Últimas movimentações", bg=BRANCO, fg=TEXTO,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        ultimas = list(reversed(self.movimentacoes[-6:]))
        self.tabela(dir_, ultimas, altura=7).pack(fill="both", expand=True)

    def mostrar_formulario(self, tipo):
        self.limpar_area()
        self.titulo(f"Adicionar {tipo}")
        cor = VERDE if tipo == "Receita" else VERMELHO

        form = tk.Frame(self.area, bg=BRANCO, padx=30, pady=25)
        form.pack(anchor="w")

        def campo(rotulo, linha, inicial=""):
            tk.Label(form, text=rotulo, bg=BRANCO, fg=TEXTO,
                     font=("Segoe UI", 10)).grid(row=linha, column=0, sticky="w", pady=8)
            e = tk.Entry(form, font=("Segoe UI", 11), width=32, relief="solid", bd=1)
            e.grid(row=linha, column=1, padx=15)
            e.insert(0, inicial)
            return e

        e_desc = campo("Descrição:", 0)
        e_valor = campo("Valor (R$):", 1)
        e_data = campo("Data/Hora:", 2, datetime.now().strftime("%d/%m/%Y %H:%M"))

        def salvar():
            descricao = e_desc.get().strip()
            valor = converter_valor(e_valor.get())
            data = e_data.get().strip()
            if not descricao:
                messagebox.showerror("Erro", "A descrição não pode ficar vazia.")
            elif valor is None:
                messagebox.showerror("Erro", "Valor inválido! Informe um número maior que zero.")
            elif not validar_data(data):
                messagebox.showerror("Erro", "Data inválida! Use o formato dd/mm/aaaa hh:mm.")
            else:
                mov = adicionar_movimentacao(self.movimentacoes, descricao, valor, tipo, data)
                messagebox.showinfo("Sucesso",
                                    f"{tipo} '{mov['descricao']}' de {moeda(mov['valor'])} "
                                    f"cadastrada com ID {mov['id']}!")
                self.mostrar_dashboard()

        tk.Button(form, text=f"Salvar {tipo}", command=salvar, bg=cor, fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=6,
                  cursor="hand2").grid(row=3, column=1, sticky="w", padx=15, pady=(15, 0))

    def mostrar_lista(self):
        self.limpar_area()
        self.titulo("Movimentações")
        if not self.movimentacoes:
            tk.Label(self.area, text="Nenhuma movimentação cadastrada.", bg=FUNDO,
                     fg=CINZA, font=("Segoe UI", 12)).pack(anchor="w")
            return
        self.tabela(self.area, self.movimentacoes, altura=16).pack(fill="both", expand=True)

    def mostrar_exclusao(self):
        self.limpar_area()
        self.titulo("Excluir Movimentação")
        tv = self.tabela(self.area, self.movimentacoes, altura=12)
        tv.pack(fill="both", expand=True)

        barra = tk.Frame(self.area, bg=FUNDO)
        barra.pack(fill="x", pady=12)
        tk.Label(barra, text="ID da movimentação:", bg=FUNDO, fg=TEXTO,
                 font=("Segoe UI", 10)).pack(side="left")
        e_id = tk.Entry(barra, width=8, font=("Segoe UI", 11), relief="solid", bd=1)
        e_id.pack(side="left", padx=10)

        def ao_selecionar(_):
            sel = tv.selection()
            if sel:
                e_id.delete(0, "end")
                e_id.insert(0, tv.item(sel[0])["values"][0])
        tv.bind("<<TreeviewSelect>>", ao_selecionar)

        def excluir():
            texto = e_id.get().strip()
            if not texto.isdigit():
                messagebox.showerror("Erro", "Informe um ID numérico válido.")
                return
            id_mov = int(texto)
            if not messagebox.askyesno("Confirmar", f"Excluir a movimentação {id_mov}?"):
                return
            if excluir_movimentacao(self.movimentacoes, id_mov):
                messagebox.showinfo("Sucesso", f"Movimentação {id_mov} excluída!")
                self.mostrar_exclusao()
            else:
                messagebox.showerror("Erro", f"Não existe movimentação com ID {id_mov}.")

        tk.Button(barra, text="Excluir", command=excluir, bg=VERMELHO, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=4,
                  cursor="hand2").pack(side="left")

    def mostrar_relatorio(self):
        self.limpar_area()
        self.titulo("Relatório Financeiro")
        self.cards_resumo()

        rec = total_por_tipo(self.movimentacoes, "Receita")
        des = total_por_tipo(self.movimentacoes, "Despesa")
        saldo = rec - des
        qtd_rec = sum(1 for m in self.movimentacoes if m["tipo"] == "Receita")
        qtd_des = len(self.movimentacoes) - qtd_rec

        caixa = tk.Frame(self.area, bg=BRANCO, padx=30, pady=25)
        caixa.pack(anchor="w", fill="x")
        linhas = [
            ("Total de receitas:", moeda(rec)),
            ("Total de despesas:", moeda(des)),
            ("Saldo atual:", moeda(saldo)),
            ("Quantidade de movimentações:",
             f"{len(self.movimentacoes)}  ({qtd_rec} receitas, {qtd_des} despesas)"),
        ]
        for i, (r, v) in enumerate(linhas):
            tk.Label(caixa, text=r, bg=BRANCO, fg=TEXTO,
                     font=("Segoe UI", 12)).grid(row=i, column=0, sticky="w", pady=6)
            tk.Label(caixa, text=v, bg=BRANCO, fg=TEXTO,
                     font=("Segoe UI", 12, "bold")).grid(row=i, column=1, sticky="w", padx=25)

    def sair(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair? Seus dados já estão salvos."):
            self.destroy()


if __name__ == "__main__":
    App().mainloop()