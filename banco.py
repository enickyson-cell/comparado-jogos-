import sqlite3

NOME_BANCO = "jogos.db"


def conectar():
    return sqlite3.connect(NOME_BANCO)


def criar_banco():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco_normal REAL NOT NULL,
            preco_atual REAL NOT NULL,
            loja TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


def listar_jogos():
    conexao = conectar()

    jogos = conexao.execute("""
        SELECT * FROM jogos
        ORDER BY id DESC
    """).fetchall()

    conexao.close()

    return jogos
def inserir_jogo(nome, preco_normal, preco_atual, loja):
    conexao = conectar()

    conexao.execute("""
        INSERT INTO jogos (nome, preco_normal, preco_atual, loja)
        VALUES (?, ?, ?, ?)
    """, (nome, preco_normal, preco_atual, loja))

    conexao.commit()
    conexao.close()
def buscar_jogos(nome):
    conexao = conectar()

    jogos = conexao.execute("""
        SELECT * FROM jogos
        WHERE nome LIKE ?
        ORDER BY preco_atual ASC
    """, (f"%{nome}%",)).fetchall()

    conexao.close()

    return jogos
