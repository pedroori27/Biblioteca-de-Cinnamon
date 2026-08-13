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

# Arquivo onde os livros (e seus empréstimos) serão salvos
ARQUIVO_LIVROS_CSV = "livro.csv"

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
    def __init__(self, nome, autor, ano, codigo_isbn, tipo, nota=0):
        self.nome = nome
        self.autor = autor
        self.ano = ano
        self.codigo_isbn = codigo_isbn
        self.tipo = tipo  # Pode ser "Manhwa", "Novel", etc.
        self.emprestado = False
        self.nota = nota
        self.emprestado_por = None  # usuário que está com o livro, ou None

    def __str__(self):
        return f"{self.nome}, autor: {self.autor}, ano: {self.ano}, tipo: {self.tipo}, nota: {self.nota}"

    def emprestar(self, usuario=None):
        if self.emprestado:
            return False, "Não foi possível emprestar: o livro já está emprestado."
        self.emprestado = True
        self.emprestado_por = usuario
        return True, "Livro emprestado com sucesso."

    def devolucao(self):
        if not self.emprestado:
            return False, "Esse livro não está emprestado."
        self.emprestado = False
        self.emprestado_por = None
        return True, "Livro devolvido com sucesso."

# Classe para gerenciar os livros da biblioteca
class Biblioteca:
    def __init__(self):
        self.livros = []
 
    def adicionar_livro(self, livro):
        self.livros.append(livro)
        self.salvar_csv()  # salva os livros no livro.csv sempre que um novo livro é cadastrado
 
    def buscar(self, termo):
        termo = termo.lower().strip()
        return [
            livro for livro in self.livros
            if termo in livro.nome.lower() or termo in livro.autor.lower()
        ]
 
    def ordenar(self, chave="nome"):
        self.livros.sort(key=lambda livro: getattr(livro, chave))
 
        # Salva todos os livros cadastrados (com status de empréstimo) no arquivo livro.csv
    def salvar_csv(self):
        with open(ARQUIVO_LIVROS_CSV, mode="w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["nome", "autor", "ano", "codigo_isbn", "tipo", "nota", "emprestado", "emprestado_por"])
            for livro in self.livros:
                escritor.writerow([
                    livro.nome, livro.autor, livro.ano, livro.codigo_isbn, livro.tipo,
                    livro.nota, livro.emprestado, livro.emprestado_por or ""
                ])
 
    # Carrega os livros salvos anteriormente no arquivo livro.csv (se ele existir),
    # e reconstrói os empréstimos ativos na conta de cada usuário dono do livro.
    # Linhas com dados corrompidos/incompatíveis (de versões antigas do arquivo)
    # são ignoradas com um aviso no console, em vez de derrubar o programa inteiro.
    def carregar_csv(self):
        try:
            with open(ARQUIVO_LIVROS_CSV, mode="r", newline="", encoding="utf-8") as arquivo:
                leitor = csv.DictReader(arquivo)
                for numero_linha, linha in enumerate(leitor, start=2):  # linha 1 é o cabeçalho
                    try:
                        tipo = linha.get("tipo") or "Livro"
                        livro = Livro(
                            linha["nome"], linha["autor"], int(linha["ano"]),
                            linha["codigo_isbn"], tipo, int(linha["nota"])
                        )
                    except (KeyError, ValueError) as erro:
                        print(f"Aviso: linha {numero_linha} de {ARQUIVO_LIVROS_CSV} ignorada (dado inválido: {erro}).")
                        continue
 
                    livro.emprestado = linha["emprestado"] == "True"
                    emprestado_por = linha["emprestado_por"]
                    if livro.emprestado and emprestado_por:
                        livro.emprestado_por = emprestado_por
                        conta_dona = banco_contas.contas.get(emprestado_por)
                        if conta_dona is not None:
                            conta_dona.emprestimos.append(livro)
                    self.livros.append(livro)
        except FileNotFoundError:
            pass  # ainda não existe livro.csv, então não há nada pra carregar

# instancias globais
banco_contas = BancoDeContas()
banco_contas.carregar_csv()  # restaura as contas salvas em conta.csv, se existirem
usuario_atual = UsuarioAtual(banco_contas)
biblioteca = Biblioteca()
biblioteca.carregar_csv()

# Lista de livros atualmente exibida na tela de Livros (após busca e/ou organização).
# É usada para mapear corretamente a linha selecionada na tabela ao objeto Livro.
livros_exibidos = []

# Conta administradora padrão, já cadastrada de fábrica
banco_contas.criar_conta("admin", "1111", administrador=True)

# Traduz a opção escolhida no combobox de organização para o atributo real do Livro
MAPA_CHAVES_ORDENACAO = {
    "Nome": "nome",
    "Autor": "autor",
    "Ano": "ano",
    "Nota": "nota"
}


# Retorna o valor usado como chave de ordenação (texto é comparado sem diferenciar maiúsculas/minúsculas)
def obter_chave_ordenacao(livro, chave):
    valor = getattr(livro, chave)
    if isinstance(valor, str):
        return valor.lower()
    return valor

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
    if not usuario_atual.esta_logado():
                messagebox.showwarning("Aviso", "Não esta conectado a nenhuma conta.")
                return
    usuario_atual.sair()
    abrir_inicio()


# Função para esconder as telas de início e home
def esconder_telas():
    start_frame.pack_forget()
    home_frame.pack_forget()
    livros_frame.pack_forget()
    adicionar_livro_frame.pack_forget()
    meus_emprestimos_frame.pack_forget()

def abrir_inicio():
    esconder_telas()
    start_frame.pack(fill="both", expand=True)


def abrir_home():
    if not usuario_atual.esta_logado():
            messagebox.showwarning("Aviso", "Você precisa estar logado para ver.")
            return
    esconder_telas()
    home_frame.pack(fill="both", expand=True)

# Atualiza a lista de livros exibida na tela de livros.
# Se "lista" não for informada, exibe todos os livros da biblioteca (sem filtro).
def atualizar_lista_livros(lista=None):
    global livros_exibidos
    if lista is None:
        lista = biblioteca.livros
    livros_exibidos = lista
    for item in livros_tree.get_children():
        livros_tree.delete(item)
    for indice, livro in enumerate(livros_exibidos):
        status = "Emprestado" if livro.emprestado else "Disponível"
        livros_tree.insert("", tk.END, iid=str(indice), values=(
            livro.nome, livro.autor, livro.ano, livro.codigo_isbn, livro.tipo, status, f"{livro.nota}/10"
        ))

# Retorna o objeto Livro correspondente à linha selecionada na tabela, ou None
def obter_livro_selecionado():
    selecionado = livros_tree.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um livro na lista.")
        return None
    indice = int(selecionado[0])
    return livros_exibidos[indice]


# Reaplica, na tabela, o filtro de busca e a organização (ordenação) atualmente
# selecionados na tela de Livros. É chamada sempre que a lista precisa ser
# redesenhada (busca, organização, empréstimo, devolução, abertura da tela).
def atualizar_livros_com_filtros():
    termo = livros_busca_entry.get().strip()
    lista = biblioteca.buscar(termo) if termo else list(biblioteca.livros)

    chave = MAPA_CHAVES_ORDENACAO.get(livros_ordenar_combobox.get(), "nome")
    decrescente = livros_ordem_combobox.get() == "Decrescente"
    lista.sort(key=lambda livro: obter_chave_ordenacao(livro, chave), reverse=decrescente)

    atualizar_lista_livros(lista)


# Busca os livros pelo termo digitado (título ou autor) e atualiza a tabela
def buscarLivros():
    atualizar_livros_com_filtros()
    if not livros_exibidos:
        messagebox.showinfo("Busca", "Nenhum livro encontrado para essa busca.")


# Limpa o campo de busca e volta a exibir todos os livros (mantendo a organização atual)
def limparBuscaLivros():
    livros_busca_entry.delete(0, tk.END)
    atualizar_livros_com_filtros()


# Organiza (ordena) a lista de livros exibida de acordo com o critério e a ordem escolhidos
def ordenarListaLivros():
    atualizar_livros_com_filtros()
 
 
# Empresta o livro selecionado para o usuário logado
def emprestarLivro():
    if not usuario_atual.esta_logado():
        messagebox.showwarning("Aviso", "Você precisa estar logado para pegar emprestado um livro.")
        return
 
    livro = obter_livro_selecionado()
    if livro is None:
        return
 
    sucesso, mensagem = livro.emprestar(usuario_atual.conta.usuario)
    if sucesso:
        usuario_atual.conta.emprestimos.append(livro)
        messagebox.showinfo("Sucesso", mensagem)
    else:
        messagebox.showwarning("Aviso", mensagem)
 
    biblioteca.salvar_csv()
    atualizar_livros_com_filtros()
    atualizar_lista_meus_emprestimos()
 
 
# Devolve um livro específico, caso ele tenha sido emprestado pelo usuário logado.
# Usada tanto pela tela de Livros quanto pela tela de Meus Empréstimos.
def devolver_livro_objeto(livro):
    if not usuario_atual.esta_logado():
        messagebox.showwarning("Aviso", "Você precisa estar logado para devolver um livro.")
        return
 
    if livro not in usuario_atual.conta.emprestimos:
        messagebox.showwarning("Aviso", "Esse livro não está emprestado por você.")
        return
 
    sucesso, mensagem = livro.devolucao()
    if sucesso:
        usuario_atual.conta.emprestimos.remove(livro)
        messagebox.showinfo("Sucesso", mensagem)
    else:
        messagebox.showwarning("Aviso", mensagem)
 
    biblioteca.salvar_csv()
    atualizar_livros_com_filtros()
    atualizar_lista_meus_emprestimos()
 
 
# Devolve o livro selecionado na tela de Livros
def devolverLivro():
    livro = obter_livro_selecionado()
    if livro is None:
        return
    devolver_livro_objeto(livro)
 
 
# Atualiza a lista de livros exibida na tela "Meus Empréstimos"
def atualizar_lista_meus_emprestimos():
    for item in meus_emprestimos_tree.get_children():
        meus_emprestimos_tree.delete(item)
    if not usuario_atual.esta_logado():
        return
    for indice, livro in enumerate(usuario_atual.conta.emprestimos):
        meus_emprestimos_tree.insert("", tk.END, iid=str(indice), values=(
            livro.nome, livro.autor, livro.ano, livro.codigo_isbn, f"{livro.nota}/10"
        ))
 
 
# Retorna o livro selecionado na tela "Meus Empréstimos", ou None
def obter_livro_selecionado_meus_emprestimos():
    selecionado = meus_emprestimos_tree.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um livro na lista.")
        return None
    indice = int(selecionado[0])
    return usuario_atual.conta.emprestimos[indice]
 
 
# Devolve o livro selecionado na tela "Meus Empréstimos"
def devolverLivroMeusEmprestimos():
    livro = obter_livro_selecionado_meus_emprestimos()
    if livro is None:
        return
    devolver_livro_objeto(livro)
 
 
# Abre a tela "Meus Empréstimos", com os livros que o usuário logado está com empréstimo ativo
def abrir_meus_emprestimos():
    if not usuario_atual.esta_logado():
        messagebox.showwarning("Aviso", "Você precisa estar logado para ver.")
        return
    esconder_telas()
    atualizar_lista_meus_emprestimos()
    meus_emprestimos_frame.pack(fill="both", expand=True)


# Abre a tela com a lista de livros para empréstimo (disponível para todos os usuários logados)
def abrir_livros():
    if not usuario_atual.esta_logado():
            messagebox.showwarning("Aviso", "Você precisa estar logado para ver.")
            return
    esconder_telas()
    atualizar_livros_com_filtros()
    livros_frame.pack(fill="both", expand=True)
 
 
# Limpa os campos do formulário de adicionar livro
def limpar_campos_livro():
    livro_titulo_entry.delete(0, tk.END)
    livro_autor_entry.delete(0, tk.END)
    livro_ano_entry.delete(0, tk.END)
    livro_isbn_entry.delete(0, tk.END)
    livro_tipo_entry.delete(0, tk.END)
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
    tipo = livro_tipo_entry.get().strip()
    nota_texto = livro_nota_entry.get().strip()
 
    if not nome or not autor or not ano_texto or not codigo_isbn or not tipo or not nota_texto:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return
 
    if not ano_texto.isdigit():
        messagebox.showwarning("Aviso", "O ano deve ser um número.")
        return
 
    if not nota_texto.isdigit() or not (1 <= int(nota_texto) <= 10):
        messagebox.showwarning("Aviso", "A nota deve ser um número inteiro de 1 a 10.")
        return
 
    novo_livro = Livro(nome, autor, int(ano_texto), codigo_isbn, tipo, int(nota_texto))
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
library_menu.add_command(label="Meus Empréstimos", command=abrir_meus_emprestimos)
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
livros_frame.rowconfigure(2, weight=1)
 
# FRAME DE ADICIONAR LIVRO (apenas administradores)
adicionar_livro_frame = tk.Frame(
    app,
    bg=COR_CREME
)
 
adicionar_livro_frame.columnconfigure(0, weight=1)
adicionar_livro_frame.rowconfigure(tuple(range(15)), weight=1)

# FRAME DE MEUS EMPRÉSTIMOS (livros que o usuário logado está com empréstimo ativo)
meus_emprestimos_frame = tk.Frame(
    app,
    bg=COR_CREME
)
 
meus_emprestimos_frame.columnconfigure(0, weight=1)
meus_emprestimos_frame.rowconfigure(1, weight=1)

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


# --- Controles de busca e organização ---
livros_controles_frame = tk.Frame(
    livros_frame,
    bg=COR_CREME
)

livros_controles_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew")
livros_controles_frame.columnconfigure(0, weight=1)
livros_controles_frame.columnconfigure(1, weight=1)


# Busca (por título ou autor)
livros_busca_frame = tk.Frame(
    livros_controles_frame,
    bg=COR_CREME
)

livros_busca_frame.grid(row=0, column=0, padx=40, sticky="w")


livros_busca_label = tk.Label(
    livros_busca_frame,
    text="Buscar (título ou autor):",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)

livros_busca_label.grid(row=0, column=0, columnspan=3, sticky="w")


livros_busca_entry = ttk.Entry(
    livros_busca_frame,
    width=28
)

livros_busca_entry.grid(row=1, column=0, padx=(0, 5), pady=5)
livros_busca_entry.bind("<Return>", lambda evento: buscarLivros())


livros_busca_button = ttk.Button(
    livros_busca_frame,
    text="Buscar",
    command=buscarLivros,
    style="Cinnamon.TButton"
)

livros_busca_button.grid(row=1, column=1, padx=5)


livros_busca_limpar_button = ttk.Button(
    livros_busca_frame,
    text="Limpar",
    command=limparBuscaLivros,
    style="Cinnamon.TButton"
)

livros_busca_limpar_button.grid(row=1, column=2, padx=5)


# Organização (por nome, autor, ano ou nota)
livros_ordenar_frame = tk.Frame(
    livros_controles_frame,
    bg=COR_CREME
)

livros_ordenar_frame.grid(row=0, column=1, padx=40, sticky="e")


livros_ordenar_label = tk.Label(
    livros_ordenar_frame,
    text="Organizar por:",
    bg=COR_CREME,
    fg=COR_TEXTO,
    font=("Arial", 11)
)

livros_ordenar_label.grid(row=0, column=0, columnspan=3, sticky="w")


livros_ordenar_combobox = ttk.Combobox(
    livros_ordenar_frame,
    values=["Nome", "Autor", "Ano", "Nota"],
    state="readonly",
    width=10
)

livros_ordenar_combobox.current(0)
livros_ordenar_combobox.grid(row=1, column=0, padx=(0, 5), pady=5)
livros_ordenar_combobox.bind("<<ComboboxSelected>>", lambda evento: ordenarListaLivros())


livros_ordem_combobox = ttk.Combobox(
    livros_ordenar_frame,
    values=["Crescente", "Decrescente"],
    state="readonly",
    width=11
)

livros_ordem_combobox.current(0)
livros_ordem_combobox.grid(row=1, column=1, padx=5)
livros_ordem_combobox.bind("<<ComboboxSelected>>", lambda evento: ordenarListaLivros())


livros_ordenar_button = ttk.Button(
    livros_ordenar_frame,
    text="Organizar",
    command=ordenarListaLivros,
    style="Cinnamon.TButton"
)

livros_ordenar_button.grid(row=1, column=2, padx=5)
 
 
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
 
livros_tree.column("titulo", width=250)
livros_tree.column("autor", width=180)
livros_tree.column("ano", width=70, anchor="center")
livros_tree.column("isbn", width=130, anchor="center")
livros_tree.column("tipo", width=100, anchor="center")
livros_tree.column("status", width=110, anchor="center")
livros_tree.column("nota", width=70, anchor="center")
 
livros_tree.grid(row=2, column=0, padx=40, pady=10, sticky="nsew")
 
 
livros_botoes_frame = tk.Frame(
    livros_frame,
    bg=COR_CREME
)
 
livros_botoes_frame.grid(row=3, column=0, pady=10)
 
 
emprestar_button = ttk.Button(
    livros_botoes_frame,
    text="Emprestar Livro",
    command=emprestarLivro,
    style="Cinnamon.TButton"
)
 
emprestar_button.grid(row=0, column=0, padx=10)
 
 
devolver_button = ttk.Button(
    livros_botoes_frame,
    text="Devolver Livro",
    command=devolverLivro,
    style="Cinnamon.TButton"
)
 
devolver_button.grid(row=0, column=1, padx=10)
 
 
livros_voltar_button = ttk.Button(
    livros_frame,
    text="Voltar para Home",
    command=abrir_home,
    style="Cinnamon.TButton"
)
 
livros_voltar_button.grid(row=4, column=0, pady=15)

 
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

# TELA DE MEUS EMPRÉSTIMOS
meus_emprestimos_title_label = tk.Label(
    meus_emprestimos_frame,
    text="Meus Empréstimos",
    bg=COR_CREME,
    fg=COR_CAFE,
    font=("Georgia", 26, "bold")
)
 
meus_emprestimos_title_label.grid(row=0, column=0, pady=20)
 
 
meus_emprestimos_tree = ttk.Treeview(
    meus_emprestimos_frame,
    columns=("titulo", "autor", "ano", "isbn", "nota"),
    show="headings"
)
 
meus_emprestimos_tree.heading("titulo", text="Título")
meus_emprestimos_tree.heading("autor", text="Autor")
meus_emprestimos_tree.heading("ano", text="Ano")
meus_emprestimos_tree.heading("isbn", text="Código/ISBN")
meus_emprestimos_tree.heading("nota", text="Nota")
 
meus_emprestimos_tree.column("titulo", width=280)
meus_emprestimos_tree.column("autor", width=200)
meus_emprestimos_tree.column("ano", width=80, anchor="center")
meus_emprestimos_tree.column("isbn", width=150, anchor="center")
meus_emprestimos_tree.column("nota", width=80, anchor="center")
 
meus_emprestimos_tree.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
 
 
meus_emprestimos_devolver_button = ttk.Button(
    meus_emprestimos_frame,
    text="Devolver Livro",
    command=devolverLivroMeusEmprestimos,
    style="Cinnamon.TButton"
)
 
meus_emprestimos_devolver_button.grid(row=2, column=0, pady=10)
 
 
meus_emprestimos_voltar_button = ttk.Button(
    meus_emprestimos_frame,
    text="Voltar para Home",
    command=abrir_home,
    style="Cinnamon.TButton"
)
 
meus_emprestimos_voltar_button.grid(row=3, column=0, pady=15)

# INÍCIO
if __name__ == "__main__": # Bom pra saber quando vai abrir
    abrir_inicio()
    app.mainloop()