import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

janela = tk.Tk()
janela.geometry("900x700")
janela.config(bg="White")
janela.resizable(False, False)

frame_principal = tk.Frame(janela,bg="white")
frame_principal.pack(side="right", fill="both", expand=True)

tk.Label(frame_principal, 
         text="Bem-vindo ao Sistema de Gestão de Projetos",
         font=("Arial", 16),
         bg="white").pack(pady=20)  

barra = tk.Frame(janela,
                 bg="gray",
                 width=200)

barra.pack(side="left", fill="y")

titulo_barra = tk.Label(barra,
                    text="Menu", 
                    font=("Arial", 25), 
                    bg="light gray", 
                    fg="black")

titulo_barra.pack(pady=10, padx=100)




















janela.mainloop()