import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector

app = FastAPI(title="Explorador de Banco de Dados e Vendas API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")

DB_CONFIG = {
    "host": DB_HOST,
    "user": "emanuel",
    "password": "1A2bc3d45!",
    "database": "bd2025"
}

class VendaInput(BaseModel):
    filial: int
    clicodigo: int
    funcodigo: int
    fpcodigo: int
    produto_codigo: int
    itvqtde: int

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def exec_procedure(nome_procedure: str, params: Optional[tuple] = None):
    try:
        conexao = get_connection()
        cursor = conexao.cursor()
        
        if params:
            cursor.execute(nome_procedure, params)
        else:
            cursor.execute(nome_procedure)

        resultados = cursor.fetchall()

        while cursor.nextset():
            pass

        cursor.close()
        conexao.close()

        return [linha[0] for linha in resultados]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no Banco de Dados: {str(e)}")


# --- ROTAS ORIGINAIS (EXPLORADOR DE BANCO) ---

@app.get("/api/bancos")
def listar_bancos():
    dados = exec_procedure("call ls_bancos();")
    return {"bancos": dados}

@app.get("/api/bancos/{banco}/tabelas")
def listarTabelas(banco: str):
    dados = exec_procedure("call ls_tabelas_do_banco(%s);", (banco,))
    return {"tabelas": dados}

@app.get("/api/bancos/{banco}/tabelas/{tabela}/colunas")
def listarColunas(banco: str, tabela: str):
    dados = exec_procedure("call ls_colunas_da_tabela(%s,%s);", (banco, tabela))
    return {"colunas": dados}

@app.get("/api/bancos/{banco}/tabelas/{tabela}/tabela_ladoN")
def listarTabela_ladoN(banco: str, tabela: str):
    dados = exec_procedure("call ls_tabela_ladoN(%s,%s);", (banco, tabela))
    return {"tabela_ladoN": dados}

@app.get("/api/bancos/{banco}/tabelas/{tabela}/tabela_lado1")
def listarTabela_lado1(banco: str, tabela: str):
    dados = exec_procedure("call ls_tabela_lado1(%s,%s);", (banco, tabela))
    return {"tabela_lado1": dados}


# --- NOVAS ROTAS (TELA DE VENDAS) ---

@app.get("/api/opcoes-venda")
def obter_opcoes_venda():
    dados = {
        "clientes": [],
        "vendedores": [],
        "produtos": [],
        "filiais": [],
        "formas_pagamento": [],
        "erros": []
    }
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        consultas = {
            "clientes": "SELECT clicodigo AS id, clinome AS nome FROM cliente ORDER BY clinome",
            "vendedores": "SELECT funcodigo AS id, funnome AS nome FROM funcionario ORDER BY funnome",
            "produtos": "SELECT procodigo AS id, pronome AS nome, COALESCE(propreco, 0) AS preco, COALESCE(prosaldo, 0) AS saldo FROM produto ORDER BY pronome",
            "filiais": "SELECT filcodigo AS id, filnome AS nome FROM filial ORDER BY filnome",
            "formas_pagamento": "SELECT fpcodigo AS id, fpdescricao AS nome FROM formapagamento ORDER BY fpdescricao"
        }

        for chave, sql in consultas.items():
            try:
                cursor.execute(sql)
                dados[chave] = cursor.fetchall()
            except Exception as e:
                dados["erros"].append(f"{chave}: {str(e)}")

        cursor.close()
        conn.close()
        return dados

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão: {str(e)}")

@app.post("/api/vendas")
def registrar_venda(venda: VendaInput):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Gera o próximo idvenda automaticamente
        cursor.execute("SELECT COALESCE(MAX(vencodigo), 0) + 1 FROM venda")
        proximo_idvenda = cursor.fetchone()[0]

        # Gera anomes atual (ex: '202611')
        anomes_atual = datetime.now().strftime("%Y%m")

        # Executa a procedure fazer_venda
        params = (
            proximo_idvenda,
            anomes_atual,
            venda.filial,
            venda.clicodigo,
            venda.funcodigo,
            venda.fpcodigo,
            venda.produto_codigo,
            venda.itvqtde
        )
        cursor.execute("CALL fazer_venda(%s, %s, %s, %s, %s, %s, %s, %s);", params)

        # Captura a mensagem retornada pelo SELECT dentro da procedure
        resultado = cursor.fetchone()
        mensagem = resultado[0] if resultado else "Operação finalizada."

        while cursor.nextset():
            pass

        conn.commit()
        cursor.close()
        conn.close()

        sucesso = "concluida" in mensagem.lower()
        return {
            "sucesso": sucesso,
            "idvenda": proximo_idvenda if sucesso else None,
            "mensagem": mensagem
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar venda: {str(e)}")
