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
import random
import tkinter  as tk
from tkinter import ttk, messagebox, Menu
from tkinter.messagebox import showerror, showwarning, showinfo

# CORES
COR_CARAMELO = "#C68B59"
COR_CAFE = "#5C4033"
COR_MARROM = "#8B5E3C"
COR_CREME = "#FFF4E0"
COR_BEGE = "#E8D3B9"
COR_BRANCO = "#FFFDF8"
COR_TEXTO = "#3E2723"

# Criação de conta (administrador apenas no codigo base)
class Conta:
    def __init__(self, usuario, senha, ids_existentes, administrador=False):
        self.usuario = usuario
        self.senha = senha
        # id único, igual ao NewUser do sistema bancário
        self.id = random.randrange(1000000, 9999999)
        while self.id in ids_existentes:
            self.id = random.randrange(1000000, 9999999)
        self.administrador = administrador
        self.emprestimos = []  # livros que esta conta está com empréstimo ativo

    def __str__(self):
        tipo = "Administrador" if self.administrador else "Usuário"
        return f"ID: {self.id}, Usuário: {self.usuario}, Tipo: {tipo}"

    def __repr__(self):
            return self.__str__()

# Classe para gerenciar o usuário atual
class BancoDeContas:
    def __init__(self):
        self.contas = {}          # usuario (str) -> Conta
        self.usuario_atual = None
 
    def criar_conta(self, usuario, senha, administrador=False):
        if usuario in self.contas:
            return None  # nome de usuário já existe
        ids_existentes = [c.id for c in self.contas.values()]
        nova_conta = Conta(usuario, senha, ids_existentes, administrador)
        self.contas[usuario] = nova_conta
        return nova_conta
 
    def login(self, usuario, senha):
        conta = self.contas.get(usuario)
        if conta is not None and conta.senha == senha:
            self.usuario_atual = conta
            return True
        self.usuario_atual = None
        return False
 
    def logout(self):
        self.usuario_atual = None

class UsuarioAtual:
    def __init__(self, banco):
        self.banco = banco
 
    def entrar(self, conta):
        self.banco.usuario_atual = conta
 
    def sair(self):
        self.banco.logout()
 
    def esta_logado(self):
        return self.banco.usuario_atual is not None
 
    def eh_admin(self):
        return self.esta_logado() and self.banco.usuario_atual.administrador
 
    @property
    def conta(self):
        return self.banco.usuario_atual

# Classe para criação de livros
class Livro:
    def __init__(self, nome, autor, ano, codigo_isbn):
        self.nome = nome
        self.autor = autor
        self.ano = ano
        self.codigo_isbn = codigo_isbn
        self.emprestado = False

    def __str__(self):
        return f"{self.nome}, autor: {self.autor}, ano: {self.ano}"

    def emprestar(self):
        if self.emprestado:
            return False, "Não foi possível emprestar: o livro já está emprestado."
        self.emprestado = True
        return True, "Livro emprestado com sucesso."

    def devolucao(self):
        if not self.emprestado:
            return False, "Esse livro não está emprestado."
        self.emprestado = False
        return True, "Livro devolvido com sucesso."

# Classe para gerenciar os livros da biblioteca
class Biblioteca:
    def __init__(self):
        self.livros = []
 
    def adicionar_livro(self, livro):
        self.livros.append(livro)
 
    def buscar(self, termo):
        termo = termo.lower().strip()
        return [
            livro for livro in self.livros
            if termo in livro.nome.lower() or termo in livro.autor.lower()
        ]
 
    def ordenar(self, chave="nome"):
        self.livros.sort(key=lambda livro: getattr(livro, chave))

# instancias globais
banco_contas = BancoDeContas()
usuario_atual = UsuarioAtual(banco_contas)

# Conta administradora padrão, já cadastrada de fábrica
banco_contas.criar_conta("admin", "1111", administrador=True)

# Abrir campo de segurança (login/registro)
def limpar_campos_seguranca():
    register_username_entry.delete(0, tk.END)
    register_password_entry.delete(0, tk.END)
    login_username_entry.delete(0, tk.END)
    login_password_entry.delete(0, tk.END)
 
 
def esconder_seguranca():
    security_window.withdraw()
    limpar_campos_seguranca()
 
 
def centralizar_seguranca(largura=400, altura=450):
    security_window.update_idletasks()
    x = (security_window.winfo_screenwidth() // 2) - (largura // 2)
    y = (security_window.winfo_screenheight() // 2) - (altura // 2)
    security_window.geometry(f"{largura}x{altura}+{x}+{y}")
 
 
def abrir_login():
    register_frame.pack_forget()
    login_frame.pack(fill="both", expand=True)
    centralizar_seguranca()
    security_window.deiconify()
    security_window.lift()
 
 
def abrir_registro():
    login_frame.pack_forget()
    register_frame.pack(fill="both", expand=True)
    centralizar_seguranca()
    security_window.deiconify()
    security_window.lift()

# Registro
def registrarUsuario():
    usuario = register_username_entry.get().strip()
    senha = register_password_entry.get()
 
    if not usuario or not senha:
        messagebox.showwarning("Aviso", "Preencha usuário e senha.")
        return
    if len(senha) < 4:
        messagebox.showwarning("Aviso", "A senha deve ter no mínimo 4 caracteres.")
        return
 
    nova_conta = banco_contas.criar_conta(usuario, senha)
    if nova_conta is None:
        messagebox.showerror("Erro", "Esse nome de usuário já está em uso.")
        return
 
    messagebox.showinfo("Sucesso", f"Conta criada com sucesso, {usuario}!")
    limpar_campos_seguranca()
    abrir_login()
 
# Login 
def realizarLogin():
    usuario = login_username_entry.get().strip()
    senha = login_password_entry.get()
 
    if banco_contas.login(usuario, senha):
        limpar_campos_seguranca()
        security_window.withdraw()
        abrir_home()
    else:
        messagebox.showwarning("Aviso", "Usuário ou senha inválidos.")
 
# Logout
def realizarLogout():
    usuario_atual.sair()
    abrir_inicio()


# Função para esconder as telas de início e home
def esconder_telas():
    start_frame.pack_forget()
    home_frame.pack_forget()


def abrir_inicio():
    esconder_telas()
    start_frame.pack(fill="both", expand=True)


def abrir_home():
    esconder_telas()
    home_frame.pack(fill="both", expand=True)

# JANELA PRINCIPAL
app = tk.Tk()

app.title("Biblioteca de Cinnamon")
app.geometry("1366x768")
app.minsize(1366, 768)
app.configure(bg=COR_CREME)

app.rowconfigure(0, weight=1)
app.columnconfigure(0, weight=1)

# ESTILO DOS WIDGETS
style = ttk.Style()

style.configure(
    "Cinnamon.TButton",
    font=("Arial", 12),
    padding=10
)

style.configure(
    "Cinnamon.TLabel",
    background=COR_CREME,
    foreground=COR_TEXTO,
    font=("Arial", 12)
)

# BARRA DE MENU
menu_bar = tk.Menu(
    app,
    bg=COR_CAFE,
    fg=COR_CREME,
    activebackground=COR_CARAMELO,
    activeforeground=COR_BRANCO
)

app.config(menu=menu_bar)

library_menu = tk.Menu(
    menu_bar,
    tearoff=0,
    bg=COR_BRANCO,
    fg=COR_TEXTO,
    activebackground=COR_CARAMELO,
    activeforeground=COR_BRANCO
)

library_menu.add_command(label="Home", command=abrir_home)
library_menu.add_command(label="Logout", command=realizarLogout)

menu_bar.add_cascade(label="Menu", menu=library_menu)

# JANELA DE SEGURANÇA
security_window = tk.Toplevel(app)

security_window.geometry("400x450")
security_window.title("Biblioteca de Cinnamon - Segurança")
security_window.configure(bg=COR_CREME)

security_window.columnconfigure(0, weight=1)
security_window.rowconfigure(0, weight=1)

security_window.withdraw()

security_window.protocol(
    "WM_DELETE_WINDOW",
    esconder_seguranca
)

# FRAME DA TELA INICIAL
start_frame = tk.Frame(
    app,
    bg=COR_CREME
)

start_frame.columnconfigure(0, weight=1)
start_frame.rowconfigure((0, 1, 2, 3), weight=1)

# FRAME DE REGISTRO
register_frame = tk.Frame(
    security_window,
    bg=COR_CREME
)

register_frame.columnconfigure(0, weight=1)
register_frame.rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

# FRAME DE LOGIN
login_frame = tk.Frame(
    security_window,
    bg=COR_CREME
)

login_frame.columnconfigure(0, weight=1)
login_frame.rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

# FRAME DA HOME
home_frame = tk.Frame(
    app,
    bg=COR_CREME
)

home_frame.columnconfigure(0, weight=1)
home_frame.rowconfigure((0, 1, 2), weight=1)

# TELA INICIAL
title_label = tk.Label(
    start_frame,
    text="Biblioteca de Cinnamon",
    bg=COR_CREME,
    fg=COR_CAFE,
    font=("Georgia", 32, "bold")
)

title_label.grid(row=0, column=0, pady=30)


subtitle_label = tk.Label(
    start_frame,
    text="Conhecimento pode ser doce como canela",
    bg=COR_CREME,
    fg=COR_MARROM,
    font=("Georgia", 14, "italic")
)

subtitle_label.grid(row=0, column=0, pady=(90, 0))


register_button = ttk.Button(
    start_frame,
    text="Registro",
    command=abrir_registro,
    style="Cinnamon.TButton"
)

register_button.grid(row=1, column=0, pady=10)


login_button = ttk.Button(
    start_frame,
    text="Login",
    command=abrir_login,
    style="Cinnamon.TButton"
)

login_button.grid(row=2, column=0, pady=10)


exit_button = ttk.Button(
    start_frame,
    text="Sair",
    command=app.destroy,
    style="Cinnamon.TButton"
)

exit_button.grid(row=3, column=0, pady=10)

# TELA DE REGISTRO
register_title_label = tk.Label(
    register_frame,
    text="Criar conta",
    bg=COR_CREME,
    fg=COR_CAFE,
    font=("Georgia", 22, "bold")
)

register_title_label.grid(row=0, column=0, pady=20)


register_username_label = tk.Label(
    register_frame,
    text="Usuário:",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)

register_username_label.grid(row=1, column=0)


register_username_entry = ttk.Entry(
    register_frame
)

register_username_entry.grid(
    row=2,
    column=0,
    padx=40,
    pady=5,
    sticky="ew"
)


register_password_label = tk.Label(
    register_frame,
    text="Senha:",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)

register_password_label.grid(row=3, column=0)


register_password_entry = ttk.Entry(
    register_frame,
    show="*"
)

register_password_entry.grid(
    row=4,
    column=0,
    padx=40,
    pady=5,
    sticky="ew"
)


register_submit_button = ttk.Button(
    register_frame,
    text="Registrar",
    command=registrarUsuario,
    style="Cinnamon.TButton"
)

register_submit_button.grid(row=5, column=0, pady=15)


register_back_button = ttk.Button(
    register_frame,
    text="Voltar para Login",
    command=abrir_login,
    style="Cinnamon.TButton"
)

register_back_button.grid(row=6, column=0)

# TELA DE LOGIN
login_title_label = tk.Label(
    login_frame,
    text="Login",
    bg=COR_CREME,
    fg=COR_CAFE,
    font=("Georgia", 22, "bold")
)

login_title_label.grid(row=0, column=0, pady=20)


login_username_label = tk.Label(
    login_frame,
    text="Usuário:",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)

login_username_label.grid(row=1, column=0)


login_username_entry = ttk.Entry(
    login_frame
)

login_username_entry.grid(
    row=2,
    column=0,
    padx=40,
    pady=5,
    sticky="ew"
)


login_password_label = tk.Label(
    login_frame,
    text="Senha:",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)

login_password_label.grid(row=3, column=0)


login_password_entry = ttk.Entry(
    login_frame,
    show="*"
)

login_password_entry.grid(
    row=4,
    column=0,
    padx=40,
    pady=5,
    sticky="ew"
)


login_submit_button = ttk.Button(
    login_frame,
    text="Entrar",
    command=realizarLogin,
    style="Cinnamon.TButton"
)

login_submit_button.grid(row=5, column=0, pady=15)


login_register_button = ttk.Button(
    login_frame,
    text="Criar conta",
    command=abrir_registro,
    style="Cinnamon.TButton"
)

login_register_button.grid(row=6, column=0)

# HOME
home_title_label = tk.Label(
    home_frame,
    text="Biblioteca de Cinnamon",
    bg=COR_CREME,
    fg=COR_CAFE,
    font=("Georgia", 32, "bold")
)

home_title_label.grid(row=0, column=0, pady=40)


home_welcome_label = tk.Label(
    home_frame,
    text="Bem-vindo à biblioteca!",
    bg=COR_CREME,
    fg=COR_MARROM,
    font=("Georgia", 18)
)

home_welcome_label.grid(row=1, column=0)


home_info_label = tk.Label(
    home_frame,
    text="Use o menu acima para navegar pela biblioteca.",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 12)
)

home_info_label.grid(row=2, column=0, pady=20)

# INÍCIO
abrir_inicio()

app.mainloop()