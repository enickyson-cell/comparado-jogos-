from flask import Flask, render_template, request, redirect, url_for

from banco import (
    criar_banco,
    listar_tarefas,
    buscar_tarefa,
    inserir_tarefa,
    atualizar_tarefa,
    alternar_status,
    excluir_tarefa,
)


app = Flask(__name__)

criar_banco()


@app.route("/")
def index():
    tarefas = listar_tarefas()

    return render_template("index.html", tarefas=tarefas)

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        disciplina = request.form["disciplina"].strip()
        descricao = request.form["descricao"].strip()
        data_entrega = request.form["data_entrega"]

        inserir_tarefa(
            titulo,
            disciplina,
            descricao,
            data_entrega
        )

        return redirect(url_for("index"))

    return render_template("cadastrar.html")
@app.route("/status/<int:id_tarefa>", methods=["POST"])
def status(id_tarefa):
    alternar_status(id_tarefa)

    return redirect(url_for("index"))
@app.route("/editar/<int:id_tarefa>", methods=["GET", "POST"])
def editar(id_tarefa):
    tarefa = buscar_tarefa(id_tarefa)

    if tarefa is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        disciplina = request.form["disciplina"].strip()
        descricao = request.form["descricao"].strip()
        data_entrega = request.form["data_entrega"]

        atualizar_tarefa(
            id_tarefa,
            titulo,
            disciplina,
            descricao,
            data_entrega
        )

        return redirect(url_for("index"))

    return render_template("editar.html", tarefa=tarefa)
@app.route("/excluir/<int:id_tarefa>", methods=["POST"])
def excluir(id_tarefa):
    excluir_tarefa(id_tarefa)

    return redirect(url_for("index"))
if __name__ == "__main__":
    app.run(debug=True)