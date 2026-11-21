import os
from typing import Optional
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector 

app = FastAPI(title="Explorador de Banco de Dados API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST","127.0.0.1")


DB_CONFIG = {
    "host":DB_HOST,
    "user":"****",
    "password":"****",
    "database":"bd2025"
}

def exec_procedure(nome_procedure: str, params: Optional[tuple] = None):
    try:

        conexao = mysql.connector.connect(**DB_CONFIG)
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
        raise HTTPException(status_code=500, detail=f"Erro no Banco de Dados: {str(e)} ")


@app.get("/api/bancos")
def listar_bancos():
    dados = exec_procedure("call ls_bancos();")
    return {"bancos":dados}

@app.get("/api/bancos/{banco}/tabelas")
def listarTabelas(banco: str): 
    dados = exec_procedure("call ls_tabelas_do_banco(%s);",(banco,))
    return {"tabelas":dados}

@app.get("/api/bancos/{banco}/tabelas/{tabela}/colunas")
def listarColunas(banco: str,tabela: str): 
    dados = exec_procedure("call ls_colunas_da_tabela(%s,%s);",(banco,tabela))
    return {"colunas":dados}

@app.get("/api/bancos/{banco}/tabelas/{tabela}/tabela_ladoN")
def listarTabela_ladoN(banco: str,tabela: str): 
    dados = exec_procedure("call ls_tabela_ladoN(%s,%s);",(banco,tabela))
    return {"tabela_ladoN": dados}

@app.get("/api/bancos/{banco}/tabelas/{tabela}/tabela_lado1")
def listarTabela_lado1(banco: str,tabela: str): 
    dados = exec_procedure("call ls_tabela_lado1(%s,%s);",(banco,tabela))
    return {"tabela_lado1": dados}

