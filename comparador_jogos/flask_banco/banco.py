import sqlite3

NOME_BANCO = "tarefas.db"


def conectar():
    return sqlite3.connect(NOME_BANCO)


def criar_banco():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            descricao TEXT,
            data_entrega TEXT,
            status TEXT NOT NULL DEFAULT 'Pendente'
        )
    """)

    conexao.commit()
    conexao.close()


def listar_tarefas():
    conexao = conectar()

    tarefas = conexao.execute("""
        SELECT * FROM tarefas
        ORDER BY id DESC
    """).fetchall()

    conexao.close()

    return tarefas


def buscar_tarefa(id_tarefa):
    conexao = conectar()

    tarefa = conexao.execute(
        "SELECT * FROM tarefas WHERE id = ?",
        (id_tarefa,)
    ).fetchone()

    conexao.close()

    return tarefa


def inserir_tarefa(titulo, disciplina, descricao, data_entrega):
    conexao = conectar()

    conexao.execute("""
        INSERT INTO tarefas (titulo, disciplina, descricao, data_entrega)
        VALUES (?, ?, ?, ?)
    """, (titulo, disciplina, descricao, data_entrega))

    conexao.commit()
    conexao.close()


def atualizar_tarefa(id_tarefa, titulo, disciplina, descricao, data_entrega):
    conexao = conectar()

    conexao.execute("""
        UPDATE tarefas
        SET titulo = ?, disciplina = ?, descricao = ?, data_entrega = ?
        WHERE id = ?
    """, (titulo, disciplina, descricao, data_entrega, id_tarefa))

    conexao.commit()
    conexao.close()


def alternar_status(id_tarefa):
    conexao = conectar()

    conexao.execute("""
        UPDATE tarefas
        SET status = CASE
            WHEN status = 'Pendente' THEN 'Concluída'
            ELSE 'Pendente'
        END
        WHERE id = ?
    """, (id_tarefa,))

    conexao.commit()
    conexao.close()


def excluir_tarefa(id_tarefa):
    conexao = conectar()

    conexao.execute(
        "DELETE FROM tarefas WHERE id = ?",
        (id_tarefa,)
    )

    conexao.commit()
    conexao.close()