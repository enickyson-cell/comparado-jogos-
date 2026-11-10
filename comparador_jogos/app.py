import math
import os
import secrets
import requests
from flask import Flask, abort, redirect, render_template, request, session, url_for
from banco import criar_banco, listar_jogos, inserir_jogo, buscar_jogo, atualizar_jogo

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
criar_banco()
NOMES_LOJAS = {'1': 'Steam', '2': 'GamersGate', '3': 'Green Man Gaming', '7': 'GOG', '8': 'EA', '11': 'Humble Store', '13': 'Ubisoft Store', '15': 'Fanatical', '21': 'WinGameStore', '23': 'GameBillet', '24': 'Epic Games Store', '25': 'Gamesplanet', '26': 'Gamesload', '27': 'IndieGala', '28': 'DreamGame'}


def consultar(url, **params):
    resposta = requests.get(url, params=params, headers={'User-Agent': 'ComparadorJogos/1.0'}, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


def pesquisar_api(nome):
    return consultar('https://www.cheapshark.com/api/1.0/games', title=nome)


def buscar_ofertas(game_id):
    return consultar('https://www.cheapshark.com/api/1.0/games', id=game_id)


def buscar_cotacao_dolar():
    cotacao = float(consultar('https://economia.awesomeapi.com.br/json/last/USD-BRL')['USDBRL']['bid'])
    if not math.isfinite(cotacao) or cotacao <= 0:
        raise ValueError('Cotação inválida')
    return cotacao


@app.template_filter('brl')
def brl(valor):
    return ('R$ {:,.2f}'.format(float(valor))).replace(',', 'X').replace('.', ',').replace('X', '.')


@app.context_processor
def formulario_contexto():
    if 'csrf' not in session:
        session['csrf'] = secrets.token_hex(24)
    return {'csrf_token': session['csrf']}


@app.before_request
def proteger_formulario():
    if request.method == 'POST' and (not session.get('csrf') or not secrets.compare_digest(session['csrf'], request.form.get('csrf_token', ''))):
        abort(400)


@app.route('/')
def index():
    if request.args.get('q'):
        return redirect(url_for('explorar', q=request.args['q']))
    return render_template('index.html', total=len(listar_jogos()))


@app.route('/explorar')
def explorar():
    pesquisa = request.args.get('q', '').strip()[:120]
    jogos, ofertas = [], []
    principal = None
    erro = None
    cotacao = None
    try:
        if pesquisa:
            jogos = pesquisar_api(pesquisa)
            if jogos:
                principal = next((j for j in jogos if str(j['gameID']) == request.args.get('jogo')), jogos[0])
                dados = buscar_ofertas(principal['gameID'])
                cotacao = buscar_cotacao_dolar()
                for original in dados.get('deals', []):
                    oferta = dict(original)
                    normal, atual = float(oferta['retailPrice']), float(oferta['price'])
                    if not all(math.isfinite(p) and p >= 0 for p in (normal, atual)):
                        continue
                    oferta.update(storeName=NOMES_LOJAS.get(str(oferta['storeID']), 'Loja #' + str(oferta['storeID'])), normalPriceBRL=normal*cotacao, salePriceBRL=atual*cotacao)
                    ofertas.append(oferta)
                ofertas.sort(key=lambda oferta: oferta['salePriceBRL'])
    except (requests.RequestException, ValueError, KeyError, TypeError):
        ofertas = []
        erro = 'Não foi possível consultar os preços agora. Tente novamente em instantes.'
    return render_template('explorar.html', pesquisa=pesquisa, jogos=jogos, principal=principal, ofertas=ofertas, erro=erro, cotacao=cotacao)


@app.route('/biblioteca')
def biblioteca():
    pesquisa = request.args.get('q', '').strip()
    jogos = [j for j in listar_jogos() if pesquisa.casefold() in j[1].casefold()]
    return render_template('biblioteca.html', jogos=jogos, pesquisa=pesquisa)


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


def salvar_formulario(jogo=None):
    erro = None
    if request.method == 'POST':
        try:
            nome, loja = request.form.get('nome', '').strip(), request.form.get('loja', '').strip()
            normal, atual = float(request.form.get('preco_normal', '')), float(request.form.get('preco_atual', ''))
            if not nome or not loja or len(nome) > 150 or len(loja) > 100:
                raise ValueError()
            if not all(math.isfinite(p) and 0 <= p <= 1000000 for p in (normal, atual)) or atual > normal:
                raise ValueError()
            if jogo:
                atualizar_jogo(jogo[0], nome, normal, atual, loja)
            else:
                inserir_jogo(nome, normal, atual, loja)
            return redirect(url_for('biblioteca', salvo=1))
        except ValueError:
            erro = 'Preencha nome e loja. Informe preços entre 0 e 1.000.000; o preço atual não pode superar o normal.'
    return render_template('editar.html' if jogo else 'cadastrar.html', jogo=jogo, erro=erro)


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    return salvar_formulario()


@app.route('/editar/<int:id_jogo>', methods=['GET', 'POST'])
def editar(id_jogo):
    jogo = buscar_jogo(id_jogo)
    if jogo is None:
        abort(404)
    return salvar_formulario(jogo)


@app.errorhandler(404)
def nao_encontrado(erro):
    return render_template('erro.html', titulo='Esse checkpoint não existe.', mensagem='A página ou o jogo que você procurou não foi encontrado.'), 404


@app.errorhandler(400)
def formulario_invalido(erro):
    return render_template('erro.html', titulo='Vamos tentar de novo?', mensagem='O formulário expirou ou é inválido. Abra a página novamente e envie os dados.'), 400


if __name__ == '__main__':
    app.run(debug=True)
