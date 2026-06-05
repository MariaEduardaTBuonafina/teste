from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os

from database import get_connection, init_db

app = Flask(__name__)
CORS(app)

init_db()

# ==========================================
# ROTA INICIAL
# ==========================================

@app.route("/")
def home():
    return jsonify({
        "mensagem": "API funcionando",
        "status": "ok"
    })


# ==========================================
# LISTAR LANÇAMENTOS
# ==========================================

@app.route("/lancamentos", methods=["GET"])
def listar_lancamentos():

    conn = get_connection()

    lancamentos = conn.execute("""
        SELECT *
        FROM lancamentos
        ORDER BY id ASC
    """).fetchall()

    conn.close()

    return jsonify([dict(l) for l in lancamentos])


# ==========================================
# ADICIONAR LANÇAMENTO
# ==========================================

@app.route("/lancamentos", methods=["POST"])
def adicionar_lancamento():

    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Nenhum dado enviado"}), 400

    descricao = dados.get("descricao", "").strip()
    valor = dados.get("valor")
    tipo = dados.get("tipo")
    categoria = dados.get("categoria", "Outros")

    if not descricao:
        return jsonify({"erro": "Descrição obrigatória"}), 400

    if valor is None:
        return jsonify({"erro": "Valor obrigatório"}), 400

    if tipo not in ["receita", "gasto"]:
        return jsonify({"erro": "Tipo inválido"}), 400

    agora = datetime.now()

    data = agora.strftime("%d/%m/%Y")
    mes = agora.strftime("%Y-%m")

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lancamentos
        (descricao, valor, tipo, categoria, data, mes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        descricao,
        float(valor),
        tipo,
        categoria,
        data,
        mes
    ))

    conn.commit()

    novo_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "id": novo_id,
        "descricao": descricao,
        "valor": valor,
        "tipo": tipo,
        "categoria": categoria,
        "data": data,
        "mes": mes
    }), 201


# ==========================================
# EXCLUIR UM LANÇAMENTO
# ==========================================

@app.route("/lancamentos/<int:id>", methods=["DELETE"])
def excluir_lancamento(id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM lancamentos
        WHERE id = ?
    """, (id,))

    conn.commit()

    removidos = cursor.rowcount

    conn.close()

    if removidos == 0:
        return jsonify({
            "erro": "Lançamento não encontrado"
        }), 404

    return jsonify({
        "mensagem": "Lançamento excluído"
    })


# ==========================================
# EXCLUIR TODOS
# ==========================================

@app.route("/lancamentos", methods=["DELETE"])
def excluir_todos():

    conn = get_connection()

    conn.execute("""
        DELETE FROM lancamentos
    """)

    conn.commit()
    conn.close()

    return jsonify({
        "mensagem": "Todos os lançamentos foram removidos"
    })


# ==========================================
# RESUMO GERAL
# ==========================================

@app.route("/resumo", methods=["GET"])
def resumo():

    conn = get_connection()

    receitas = conn.execute("""
        SELECT COALESCE(SUM(valor),0)
        FROM lancamentos
        WHERE tipo='receita'
    """).fetchone()[0]

    gastos = conn.execute("""
        SELECT COALESCE(SUM(valor),0)
        FROM lancamentos
        WHERE tipo='gasto'
    """).fetchone()[0]

    mes_atual = datetime.now().strftime("%Y-%m")

    receitas_mes = conn.execute("""
        SELECT COALESCE(SUM(valor),0)
        FROM lancamentos
        WHERE tipo='receita'
        AND mes=?
    """, (mes_atual,)).fetchone()[0]

    gastos_mes = conn.execute("""
        SELECT COALESCE(SUM(valor),0)
        FROM lancamentos
        WHERE tipo='gasto'
        AND mes=?
    """, (mes_atual,)).fetchone()[0]

    conn.close()

    return jsonify({
        "saldo_atual": round(receitas - gastos, 2),
        "total_receitas": round(receitas, 2),
        "total_gastos": round(gastos, 2),
        "receitas_mes": round(receitas_mes, 2),
        "gastos_mes": round(gastos_mes, 2),
        "saldo_mes": round(receitas_mes - gastos_mes, 2)
    })


# ==========================================
# RELATÓRIOS MENSAIS
# ==========================================

@app.route("/relatorios", methods=["GET"])
def relatorios():

    conn = get_connection()

    meses = conn.execute("""
        SELECT DISTINCT mes
        FROM lancamentos
        ORDER BY mes DESC
    """).fetchall()

    resultado = []

    for m in meses:

        mes = m["mes"]

        receitas = conn.execute("""
            SELECT COALESCE(SUM(valor),0)
            FROM lancamentos
            WHERE tipo='receita'
            AND mes=?
        """, (mes,)).fetchone()[0]

        gastos = conn.execute("""
            SELECT COALESCE(SUM(valor),0)
            FROM lancamentos
            WHERE tipo='gasto'
            AND mes=?
        """, (mes,)).fetchone()[0]

        maior_gasto = conn.execute("""
            SELECT descricao, valor
            FROM lancamentos
            WHERE tipo='gasto'
            AND mes=?
            ORDER BY valor DESC
            LIMIT 1
        """, (mes,)).fetchone()

        resultado.append({
            "mes": mes,
            "receitas": receitas,
            "gastos": gastos,
            "saldo": receitas - gastos,
            "maior_gasto": dict(maior_gasto) if maior_gasto else None
        })

    conn.close()

    return jsonify(resultado)


# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    porta = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=porta,
        debug=True
    )