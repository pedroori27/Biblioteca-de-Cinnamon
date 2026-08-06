"""
Objetivo:
Cadastrar livros (título, autor, ano de publicação, código/ISBN, status: disponível ou emprestado)
Registrar empréstimo de um livro (muda o status para "emprestado")
Registrar devolução de um livro (muda o status de volta para "disponível")
Listar todos os livros cadastrados, com seus status
Buscar um livro por título ou autor
Ordenar a listagem de livros (por título, autor ou ano)
Para registrar livros novos precisa de acesso de adminstrador
adicionar tempo que deve ser devoluido e conta
criar tela com foto
usar hash?
"""
import tkinter  as tk
from tkinter import ttk, messagebox, Menu
from tkinter.messagebox import showerror, showwarning, showinfo

# Criação de conta (administrador apenas no codigo base)
class Conta:
    def __init__(self, usuario, senha, administrador=False):
        self.usuario = usuario
        self.senha = senha
        self.administrador = administrador

    def login(self, usuario, senha):
        return self.usuario == usuario and self.senha == senha

admin = Conta("admin", "1111", administrador=True)

# Classe para criação de livros
class Livros():
    # Cadastra os livros
    def __init__(self, nome, autor, ano, codigoIsbn, status):
        self.nome = nome
        self.autor = autor
        self.ano = ano
        self.codigoIsbn = codigoIsbn
        self.stadus = status

    # teste de print
    def __str__(self):
        return f"{self.nome}, autor: {self.autor}, ano: {self.ano}"

    # Permite o emprestimo do livro
    def emprestar(self):
        if self.emprestar == 1: # 1 significa que ele foi emprestado
            return "não foi possivel emprestar"
        self.emprestar = 1

    # Devolução do livro emprestado
    def devolucao(self):
        if self.emprestar == 0: # 0 significa que ele não foi emprestado
            return "não foi emprestado"

class biblioteca():
    # Mostra a lista de livros
    def livros():
        pass

    #Menu principal
    def menuPrincipal():
        pass

def abrirBiblioteca(): # Abre o banco na tela de escolher entre registro e login
    home.grid(row=0, column=0, sticky="nsew") # nsew significa que vai se alinhar com os 4 cantos da tela
    MenuBiblioteca.mainloop()

MenuBiblioteca = tk.Tk()
MenuBiblioteca.geometry("500x500")
MenuBiblioteca.title('Banco')
MenuBiblioteca.rowconfigure(0, weight=1)
MenuBiblioteca.columnconfigure(0, weight=1)

home = tk.Frame(MenuBiblioteca, bg="#A3713B")

abrirBiblioteca()