from pathlib import Path
import sqlite3
from contextlib import contextmanager

NOME_BANCO = str(Path(__file__).with_name('jogos.db'))


@contextmanager
def conectar():
    conexao = sqlite3.connect(NOME_BANCO)
    try:
        with conexao:
            yield conexao
    finally:
        conexao.close()


def criar_banco():
    with conectar() as conexao:
        conexao.execute('''CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL,
            preco_normal REAL NOT NULL, preco_atual REAL NOT NULL, loja TEXT NOT NULL
        )''')


def listar_jogos():
    with conectar() as conexao:
        return conexao.execute('SELECT * FROM jogos ORDER BY id DESC').fetchall()


def buscar_jogos(nome):
    with conectar() as conexao:
        return conexao.execute('SELECT * FROM jogos WHERE nome LIKE ? ORDER BY preco_atual', (f'%{nome}%',)).fetchall()


def buscar_jogo(id_jogo):
    with conectar() as conexao:
        return conexao.execute('SELECT * FROM jogos WHERE id = ?', (id_jogo,)).fetchone()


def inserir_jogo(nome, preco_normal, preco_atual, loja):
    with conectar() as conexao:
        conexao.execute('INSERT INTO jogos (nome, preco_normal, preco_atual, loja) VALUES (?, ?, ?, ?)', (nome, preco_normal, preco_atual, loja))


def atualizar_jogo(id_jogo, nome, preco_normal, preco_atual, loja):
    with conectar() as conexao:
        conexao.execute('UPDATE jogos SET nome=?, preco_normal=?, preco_atual=?, loja=? WHERE id=?', (nome, preco_normal, preco_atual, loja, id_jogo))
