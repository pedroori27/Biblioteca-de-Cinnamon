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
import csv
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

# Arquivo onde as contas serão salvas
ARQUIVO_CONTAS_CSV = "conta.csv"

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
        self.salvar_csv()  # salva as contas no conta.csv sempre que uma nova conta é criada
        return nova_conta

    # Salva todas as contas cadastradas no arquivo conta.csv
    def salvar_csv(self):
        with open(ARQUIVO_CONTAS_CSV, mode="w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["id", "usuario", "senha", "administrador"])
            for conta in self.contas.values():
                escritor.writerow([conta.id, conta.usuario, conta.senha, conta.administrador])

    # Carrega as contas salvas anteriormente no arquivo conta.csv (se ele existir)
    def carregar_csv(self):
        try: # Acho esse try/except meio desnecassário, mas como não tenho custume de usar, coloquei pra ir ganhando prática. Se o arquivo não existir, não há nada pra carregar, então apenas ignora.
            with open(ARQUIVO_CONTAS_CSV, mode="r", newline="", encoding="utf-8") as arquivo:
                leitor = csv.DictReader(arquivo)
                for linha in leitor:
                    conta = Conta.__new__(Conta)  # não chama __init__ pra manter o id que já estava salvo
                    conta.id = int(linha["id"])
                    conta.usuario = linha["usuario"]
                    conta.senha = linha["senha"]
                    conta.administrador = linha["administrador"] == "True"
                    conta.emprestimos = []
                    self.contas[conta.usuario] = conta
        except FileNotFoundError:
            pass  # ainda não existe conta.csv, então não há nada pra carregar
 
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
    def __init__(self, nome, autor, ano, codigo_isbn, nota=0):
        self.nome = nome
        self.autor = autor
        self.ano = ano
        self.codigo_isbn = codigo_isbn
        self.tipo = "Livro"  # Pode ser "Manhwa", "Novel", etc.
        self.emprestado = False
        self.nota = nota

    def __str__(self):
        return f"{self.nome}, autor: {self.autor}, ano: {self.ano}, tipo: {self.tipo}, nota: {self.nota}"

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
banco_contas.carregar_csv()  # restaura as contas salvas em conta.csv, se existirem
usuario_atual = UsuarioAtual(banco_contas)
biblioteca = Biblioteca()

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
    livros_frame.pack_forget()
    adicionar_livro_frame.pack_forget()

def abrir_inicio():
    esconder_telas()
    start_frame.pack(fill="both", expand=True)


def abrir_home():
    esconder_telas()
    home_frame.pack(fill="both", expand=True)

# Atualiza a lista de livros exibida na tela de livros
def atualizar_lista_livros():
    for item in livros_tree.get_children():
        livros_tree.delete(item)
    for livro in biblioteca.livros:
        status = "Emprestado" if livro.emprestado else "Disponível"
        livros_tree.insert("", tk.END, values=(
            livro.nome, livro.autor, livro.ano, livro.codigo_isbn, livro.tipo, status, f"{livro.nota}/10"
        ))
 
 
# Abre a tela com a lista de livros para empréstimo (disponível para todos os usuários logados)
def abrir_livros():
    esconder_telas()
    atualizar_lista_livros()
    livros_frame.pack(fill="both", expand=True)

# Abre a tela com a lista de livros para empréstimo (disponível para todos os usuários logados)
def abrir_livros():
    esconder_telas()
    atualizar_lista_livros()
    livros_frame.pack(fill="both", expand=True)
 
 
# Limpa os campos do formulário de adicionar livro
def limpar_campos_livro():
    livro_titulo_entry.delete(0, tk.END)
    livro_autor_entry.delete(0, tk.END)
    livro_ano_entry.delete(0, tk.END)
    livro_isbn_entry.delete(0, tk.END)
    livro_nota_entry.delete(0, tk.END)
 
 
# Abre a aba de adicionar livro, apenas para administradores
def abrir_adicionar_livro():
    if not usuario_atual.eh_admin():
        messagebox.showwarning("Acesso negado", "Apenas administradores podem adicionar livros.")
        return
    esconder_telas()
    adicionar_livro_frame.pack(fill="both", expand=True)
 
 
# Cadastra um novo livro na biblioteca (apenas administradores)
def adicionarLivro():
    if not usuario_atual.eh_admin():
        messagebox.showwarning("Acesso negado", "Apenas administradores podem adicionar livros.")
        return
 
    nome = livro_titulo_entry.get().strip()
    autor = livro_autor_entry.get().strip()
    ano_texto = livro_ano_entry.get().strip()
    codigo_isbn = livro_isbn_entry.get().strip()
    nota_texto = livro_nota_entry.get().strip()
 
    if not nome or not autor or not ano_texto or not codigo_isbn or not nota_texto:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return
 
    if not ano_texto.isdigit():
        messagebox.showwarning("Aviso", "O ano deve ser um número.")
        return
 
    if not nota_texto.isdigit() or not (1 <= int(nota_texto) <= 10):
        messagebox.showwarning("Aviso", "A nota deve ser um número inteiro de 1 a 10.")
        return
 
    novo_livro = Livro(nome, autor, int(ano_texto), codigo_isbn, int(nota_texto))
    biblioteca.adicionar_livro(novo_livro)
 
    messagebox.showinfo("Sucesso", f"Livro '{nome}' adicionado com sucesso!")
    limpar_campos_livro()

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
library_menu.add_command(label="Livros", command=abrir_livros)
library_menu.add_command(label="Adicionar Livro (Admin)", command=abrir_adicionar_livro)
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

# FRAME DE LIVROS (lista de livros para empréstimo, com status e nota)
livros_frame = tk.Frame(
    app,
    bg=COR_CREME
)
 
livros_frame.columnconfigure(0, weight=1)
livros_frame.rowconfigure(1, weight=1)
 
# FRAME DE ADICIONAR LIVRO (apenas administradores)
adicionar_livro_frame = tk.Frame(
    app,
    bg=COR_CREME
)
 
adicionar_livro_frame.columnconfigure(0, weight=1)
adicionar_livro_frame.rowconfigure(tuple(range(15)), weight=1)

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

# TELA DE LIVROS
livros_title_label = tk.Label(
    livros_frame,
    text="Livros para Empréstimo",
    bg=COR_CREME,
    fg=COR_CAFE,
    font=("Georgia", 26, "bold")
)
 
livros_title_label.grid(row=0, column=0, pady=20)
 
 
livros_tree = ttk.Treeview(
    livros_frame,
    columns=("titulo", "autor", "ano", "isbn", "tipo", "status", "nota"),
    show="headings"
)
 
livros_tree.heading("titulo", text="Título")
livros_tree.heading("autor", text="Autor")
livros_tree.heading("ano", text="Ano")
livros_tree.heading("isbn", text="Código/ISBN")
livros_tree.heading("tipo", text="Tipo")
livros_tree.heading("status", text="Status")
livros_tree.heading("nota", text="Nota")
 
livros_tree.column("titulo", width=280)
livros_tree.column("autor", width=200)
livros_tree.column("ano", width=80, anchor="center")
livros_tree.column("isbn", width=150, anchor="center")
livros_tree.column("tipo", width=120, anchor="center")
livros_tree.column("status", width=120, anchor="center")
livros_tree.column("nota", width=80, anchor="center")
 
livros_tree.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
 
 
livros_voltar_button = ttk.Button(
    livros_frame,
    text="Voltar para Home",
    command=abrir_home,
    style="Cinnamon.TButton"
)
 
livros_voltar_button.grid(row=2, column=0, pady=15)
 
# TELA DE ADICIONAR LIVRO (ADMIN)
adicionar_livro_title_label = tk.Label(
    adicionar_livro_frame,
    text="Adicionar Livro (Administrador)",
    bg=COR_CREME,
    fg=COR_CAFE,
    font=("Georgia", 24, "bold")
)
 
adicionar_livro_title_label.grid(row=0, column=0, pady=20)
 
 
livro_titulo_label = tk.Label(
    adicionar_livro_frame,
    text="Título:",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)
 
livro_titulo_label.grid(row=1, column=0)
 
 
livro_titulo_entry = ttk.Entry(
    adicionar_livro_frame
)
 
livro_titulo_entry.grid(
    row=2,
    column=0,
    padx=400,
    pady=5,
    sticky="ew"
)
 
 
livro_autor_label = tk.Label(
    adicionar_livro_frame,
    text="Autor:",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)
 
livro_autor_label.grid(row=3, column=0)
 
 
livro_autor_entry = ttk.Entry(
    adicionar_livro_frame
)
 
livro_autor_entry.grid(
    row=4,
    column=0,
    padx=400,
    pady=5,
    sticky="ew"
)
 
 
livro_ano_label = tk.Label(
    adicionar_livro_frame,
    text="Ano:",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)
 
livro_ano_label.grid(row=5, column=0)
 
 
livro_ano_entry = ttk.Entry(
    adicionar_livro_frame
)
 
livro_ano_entry.grid(
    row=6,
    column=0,
    padx=400,
    pady=5,
    sticky="ew"
)
 
 
livro_isbn_label = tk.Label(
    adicionar_livro_frame,
    text="Código/ISBN:",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)
 
livro_isbn_label.grid(row=7, column=0)
 
 
livro_isbn_entry = ttk.Entry(
    adicionar_livro_frame
)
 
livro_isbn_entry.grid(
    row=8,
    column=0,
    padx=400,
    pady=5,
    sticky="ew"
)

livro_tipo_entry = ttk.Entry(
    adicionar_livro_frame
)

livro_tipo_entry.grid(
    row=10,
    column=0,
    padx=400,
    pady=5,
    sticky="ew"
)

livro_tipo_label = tk.Label(
    adicionar_livro_frame,
    text="Tipo (Livro, Manhwa, Novel, etc.):",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)

livro_tipo_label.grid(row=9, column=0)

livro_nota_label = tk.Label(
    adicionar_livro_frame,
    text="Nota (1 a 10):",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)
 
livro_nota_label.grid(row=11, column=0)
 
 
livro_nota_entry = ttk.Entry(
    adicionar_livro_frame
)
 
livro_nota_entry.grid(
    row=12,
    column=0,
    padx=400,
    pady=5,
    sticky="ew"
)
 
 
adicionar_livro_submit_button = ttk.Button(
    adicionar_livro_frame,
    text="Adicionar Livro",
    command=adicionarLivro,
    style="Cinnamon.TButton"
)
 
adicionar_livro_submit_button.grid(row=13, column=0, pady=15)
 
 
adicionar_livro_voltar_button = ttk.Button(
    adicionar_livro_frame,
    text="Voltar para Home",
    command=abrir_home,
    style="Cinnamon.TButton"
)
 
adicionar_livro_voltar_button.grid(row=14, column=0)

# INÍCIO
if __name__ == "__main__": # Bom pra saber quando vai abrir
    abrir_inicio()
    app.mainloop()