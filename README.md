📚 Biblioteca de Cinnamon

Um sistema de gerenciamento de biblioteca com interface gráfica em desktop, feito em Python + Tkinter. Permite cadastrar livros, controlar empréstimos e devoluções, e gerenciar contas de usuários e administradores — tudo com persistência simples em arquivos CSV.

"Conhecimento pode ser doce como canela" 🍂

Sobre o projeto

O Biblioteca de Cinnamon simula o funcionamento de uma biblioteca real: usuários criam uma conta, fazem login, navegam pelo acervo, pesquisam e organizam a listagem de livros, pegam livros emprestados e os devolvem quando quiserem. Administradores têm acesso a uma tela exclusiva para cadastrar novos livros no acervo.

Funcionalidades:
    
    - Autenticação de usuários
    - criptografia de senhas
    - Registro de nova conta (usuário/senha)
    - Login e logout
    - Dois tipos de conta: usuário comum e administrador
    - Conta de administrador padrão já cadastrada de fábrica
    - Gerenciamento de livros
    - Listagem de todos os livros do acervo, com título, autor, ano, código/ISBN, tipo, status (Disponível/Emprestado) e nota
    - Cadastro de novos livros (somente administradores), com título, autor, ano, código/ISBN, tipo (Livro, Manhwa, Novel, - etc.) e nota (1 a 10)
    - Busca de livros por título ou autor
    - Organização da listagem por título, autor, ano ou nota, em ordem crescente ou decrescente
    - Empréstimos
    - Empréstimo de um livro disponível para o usuário logado
    - Devolução de livros, tanto pela tela de Livros quanto pela tela de Meus Empréstimos
    - Tela "Meus Empréstimos", com os livros atualmente emprestados pelo usuário logado
    - Persistência de dados
    - Contas salvas em conta.csv
    - Livros (e o status de cada empréstimo) salvos em livro.csv
    - Os dados são recarregados automaticamente sempre que o programa é aberto

Tecnologias utilizadas:
    Python 3
    Tkinter / ttk — interface gráfica
    csv — persistência de dados (biblioteca padrão do Python)
    hashlib — criptografia das senhas
