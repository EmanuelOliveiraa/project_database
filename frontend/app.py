import os
from flask import Flask, render_template, request
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

API_URL = "http://127.0.0.1:8000"

@app.route("/", methods=["GET", "POST"])
@app.route("/venda", methods=["GET", "POST"])
def tela_venda():
    mensagem = None
    sucesso = False

    # Se o usuário clicou em "Confirmar Venda"
    if request.method == "POST":
        payload = {
            "filial": int(request.form.get("filial", 1)),
            "clicodigo": int(request.form.get("clicodigo")),
            "funcodigo": int(request.form.get("funcodigo")),
            "fpcodigo": int(request.form.get("fpcodigo", 1)),
            "produto_codigo": int(request.form.get("produto_codigo")),
            "itvqtde": int(request.form.get("itvqtde"))
        }

        try:
            res = requests.post(f"{API_URL}/api/vendas", json=payload, timeout=5)
            dados_res = res.json()

            if res.status_code == 200:
                sucesso = dados_res.get("sucesso", False)
                id_gerado = dados_res.get("idvenda")
                msg_banco = dados_res.get("mensagem")
                mensagem = f"{msg_banco} (Venda #{id_gerado})" if sucesso else msg_banco
            else:
                mensagem = f"Erro na API: {dados_res.get('detail', 'Erro desconhecido')}"
        except Exception as e:
            mensagem = f"Falha de comunicação com o backend: {str(e)}"

    # Carrega as listas atualizadas para preencher os <select>
    opcoes = {
        "clientes": [],
        "vendedores": [],
        "produtos": [],
        "filiais": [],
        "formas_pagamento": []
    }
    try:
        res_opcoes = requests.get(f"{API_URL}/api/opcoes-venda", timeout=5)
        if res_opcoes.status_code == 200:
            opcoes = res_opcoes.json()
    except Exception as e:
        if not mensagem:
            mensagem = f"Erro ao carregar listas do banco: {str(e)}"

    return render_template(
        "index.html",
        clientes=opcoes["clientes"],
        vendedores=opcoes["vendedores"],
        produtos=opcoes["produtos"],
        filiais=opcoes["filiais"],
        formas_pagamento=opcoes["formas_pagamento"],
        mensagem=mensagem,
        sucesso=sucesso
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
