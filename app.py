from flask import Flask, render_template, request, redirect, url_for
import requests

from banco import (
    criar_banco,
    listar_jogos,
    inserir_jogo,
    buscar_jogos
)
app = Flask(__name__)

criar_banco()

def pesquisar_api(nome):
    url = "https://www.cheapshark.com/api/1.0/games"

    resposta = requests.get(
        url,
        params={"title": nome},
        headers={
            "User-Agent": "ComparadorJogos/1.0"
        },
        timeout=10
    )

    resposta.raise_for_status()

    return resposta.json()
def buscar_cotacao_dolar():
    url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"

    resposta = requests.get(
        url,
        timeout=10
    )

    resposta.raise_for_status()

    dados = resposta.json()

    return float(dados["USDBRL"]["bid"])
def buscar_lojas():
    url = "https://www.cheapshark.com/api/1.0/stores"

    resposta = requests.get(
        url,
        timeout=10
    )

    resposta.raise_for_status()

    return resposta.json()
def buscar_ofertas(game_id):
    url = "https://www.cheapshark.com/api/1.0/games"

    resposta = requests.get(
        url,
        params={"id": game_id},
        headers={
            "User-Agent": "ComparadorJogos/1.0"
        },
        timeout=10
    )

    resposta.raise_for_status()

    return resposta.json()
NOMES_LOJAS = {
    "1": "Steam",
    "2": "GamersGate",
    "3": "GreenManGaming",
    "7": "GOG",
    "8": "Origin",
    "11": "Humble Store",
    "13": "Ubisoft Store",
    "15": "Fanatical",
    "21": "WinGameStore",
    "23": "GameBillet",
    "24": "Epic Games Store",
    "25": "Gamesplanet",
    "26": "Gamesload",
    "27": "IndieGala",
    "28": "DreamGame"
}

@app.route("/")
def index():

    pesquisa = request.args.get("q", "").strip()

    jogos = []
    ofertas = []

    if pesquisa:

        jogos = pesquisar_api(pesquisa)

        if jogos:

         jogo_principal = jogos[0]
         print("JOGO PRINCIPAL:", jogo_principal)

        game_id = jogo_principal["gameID"]

        dados = buscar_ofertas(game_id)

        ofertas = dados.get("deals", [])

        cotacao = buscar_cotacao_dolar()

           
        for oferta in ofertas:
                print("STORE ID:", oferta.get("storeID"))
                preco_normal = float(
                    oferta.get("retailPrice", 0)
                )

                preco_atual = float(
                    oferta.get("price", 0)
                )
                oferta["storeName"] = NOMES_LOJAS.get(
                   str(oferta["storeID"]),
                   f"Loja #{oferta['storeID']}"
)
                oferta["normalPriceBRL"] = preco_normal * cotacao
                oferta["salePriceBRL"] = preco_atual * cotacao

        ofertas.sort(
                key=lambda oferta: oferta.get("salePriceBRL", float("inf"))
)

        if ofertas:
                   ofertas[0]["mais_barato"] = True
 
    return render_template(
    "index.html",
    jogos=jogos,
    ofertas=ofertas,
    pesquisa=pesquisa,
    jogo_principal=jogo_principal if jogos else None
)
    
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():

    if request.method == "POST":

        nome = request.form["nome"].strip()
        preco_normal = float(request.form["preco_normal"])
        preco_atual = float(request.form["preco_atual"])
        loja = request.form["loja"].strip()

        inserir_jogo(
            nome,
            preco_normal,
            preco_atual,
            loja
        )

        return redirect(url_for("index"))

    return render_template("cadastrar.html")


if __name__ == "__main__":
    app.run(debug=True)
