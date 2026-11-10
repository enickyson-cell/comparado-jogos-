# Checkpoint — Comparador de jogos

Aplicação Flask para comparar ofertas de jogos para PC e manter uma coleção local de preços cadastrados manualmente.

## Executar

```powershell
python -m pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000 no navegador. No Windows, `py` pode substituir `python`.

## Páginas

- `/`: início.
- `/explorar`: pesquisa e comparação de ofertas.
- `/biblioteca`: coleção local com filtro por nome.
- `/cadastrar`: cadastro de jogos e preços.
- `/editar/<id>`: edição de um jogo cadastrado.
- `/sobre`: funcionamento e informações sobre os valores.

Os dados existentes de `jogos.db` são preservados. A coleção é compartilhada por quem acessa esta instalação, sem contas individuais. Preços cadastrados não são atualizados automaticamente.

A busca usa CheapShark e AwesomeAPI. Valores em reais são estimativas e podem diferir do preço final da loja. As consultas exigem internet.

## Testes

```powershell
python -m unittest -v test_app
```

Os testes usam banco temporário e simulam as APIs, sem alterar a coleção.

Para executar com vários processos, defina uma `SECRET_KEY` fixa no ambiente. O servidor iniciado por `app.py` usa modo de desenvolvimento.
