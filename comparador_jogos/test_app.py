import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import requests
import banco
import app as site

class Fluxos(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original = banco.NOME_BANCO
        banco.NOME_BANCO = str(Path(self.temp.name) / 'teste.db')
        banco.criar_banco()
        site.app.config['TESTING'] = True
        self.client = site.app.test_client()

    def tearDown(self):
        banco.NOME_BANCO = self.original
        self.temp.cleanup()

    def token(self):
        self.client.get('/cadastrar')
        with self.client.session_transaction() as sess:
            return sess['csrf']

    def test_paginas(self):
        for pagina in ['/', '/explorar', '/biblioteca', '/sobre', '/cadastrar']:
            with self.subTest(pagina=pagina):
                r = self.client.get(pagina)
                self.assertEqual(r.status_code, 200)
                self.assertIn(b'checkpoint', r.data)
        self.assertEqual(self.client.get('/editar/999').status_code, 404)
        self.assertEqual(self.client.get('/inexistente').status_code, 404)
        self.assertEqual(self.client.get('/?q=Hades').status_code, 302)

    def test_cadastro_edicao_e_validacao(self):
        dados = dict(csrf_token=self.token(), nome='Hades', loja='Steam', preco_normal='50', preco_atual='25')
        self.assertEqual(self.client.post('/cadastrar', data=dados).status_code, 302)
        jogos = banco.listar_jogos()
        self.assertEqual(len(jogos), 1)
        id_jogo = jogos[0][0]
        self.assertEqual(self.client.get(f'/editar/{id_jogo}').status_code, 200)
        dados['preco_atual'] = '20'
        self.assertEqual(self.client.post(f'/editar/{id_jogo}', data=dados).status_code, 302)
        self.assertEqual(banco.buscar_jogo(id_jogo)[3], 20)
        self.assertIn(b'Hades', self.client.get('/biblioteca?q=hades').data)
        for valor in ['-1', 'nan', 'inf', '60', 'abc']:
            dados['preco_atual'] = valor
            self.assertEqual(self.client.post('/cadastrar', data=dados).status_code, 200)
        self.assertEqual(len(banco.listar_jogos()), 1)
        self.assertEqual(self.client.post('/cadastrar', data={}).status_code, 400)

    @patch.object(site, 'pesquisar_api', return_value=[])
    def test_busca_vazia(self, mock):
        self.assertIn('Nenhum jogo encontrado', self.client.get('/explorar?q=ausente').text)

    @patch.object(site, 'pesquisar_api', side_effect=requests.Timeout())
    def test_api_indisponivel(self, mock):
        r = self.client.get('/explorar?q=Hades')
        self.assertEqual(r.status_code, 200)
        self.assertIn('Não foi possível', r.text)

    @patch.object(site, 'buscar_cotacao_dolar', return_value=5)
    @patch.object(site, 'buscar_ofertas', return_value={'deals': [dict(storeID='1', retailPrice='20', price='10', dealID='a'), dict(storeID='7', retailPrice='20', price='5', dealID='b')]})
    @patch.object(site, 'pesquisar_api', return_value=[dict(gameID='1', external='Hades', thumb='https://example.com/a.jpg'), dict(gameID='2', external='Hades II', thumb='https://example.com/b.jpg')])
    def test_comparacao_e_selecao(self, busca, ofertas, cotacao):
        r = self.client.get('/explorar?q=Hades&jogo=2')
        self.assertEqual(r.status_code, 200)
        ofertas.assert_called_once_with('2')
        self.assertIn('R$ 25,00', r.text)
        self.assertLess(r.text.index('GOG'), r.text.index('Steam'))
        self.assertIn('Outros resultados', r.text)

if __name__ == '__main__':
    unittest.main()
