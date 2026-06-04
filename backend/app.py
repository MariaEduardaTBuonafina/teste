# Importamos as ferramentas necessárias
from flask import Flask, jsonify, request  # request lê dados enviados pelo frontend
from flask_cors import CORS                 # Permite comunicação entre frontend e backend
import os                                   # Acessa variáveis de ambiente
from datetime import datetime               # Trabalha com datas

# Criamos a aplicação Flask
app = Flask(__name__)
CORS(app)

# -------------------------------------------------------
# BANCO DE DADOS EM MEMÓRIA
# Em um projeto real, usaríamos um banco como PostgreSQL.
# Para simplificar, guardamos os lançamentos em uma lista Python.
# A lista reinicia quando o servidor reinicia — isso é esperado para este projeto.
# -------------------------------------------------------
lancamentos = []   # Lista que guarda todos os lançamentos (gastos e receitas)
proximo_id = 1     # Contador para gerar IDs únicos para cada lançamento

# -------------------------------------------------------
# ROTAS (endpoints) da API
# -------------------------------------------------------

# Rota principal — testa se o servidor está no ar
@app.route('/')
def inicio():
    return jsonify({"mensagem": "API do Gerenciador de Gastos funcionando!", "status": "ok"})


# GET /lancamentos — retorna todos os lançamentos cadastrados
@app.route('/lancamentos', methods=['GET'])
def get_lancamentos():
    return jsonify(lancamentos)


# POST /lancamentos — adiciona um novo lançamento (gasto ou receita)
@app.route('/lancamentos', methods=['POST'])
def add_lancamento():
    global proximo_id  # Precisamos do "global" para modificar a variável de fora da função

    # request.get_json() lê o corpo da requisição enviada pelo frontend
    dados = request.get_json()

    # Validação: verificamos se os campos obrigatórios foram enviados
    if not dados:
        return jsonify({"erro": "Nenhum dado enviado"}), 400
    if 'descricao' not in dados or not dados['descricao'].strip():
        return jsonify({"erro": "Descrição é obrigatória"}), 400
    if 'valor' not in dados:
        return jsonify({"erro": "Valor é obrigatório"}), 400
    if 'tipo' not in dados or dados['tipo'] not in ['gasto', 'receita']:
        return jsonify({"erro": "Tipo deve ser 'gasto' ou 'receita'"}), 400

    # Criamos o objeto do novo lançamento
    novo = {
        "id": proximo_id,
        "descricao": dados['descricao'].strip(),
        "valor": float(dados['valor']),         # Garantimos que o valor seja número
        "tipo": dados['tipo'],                  # "gasto" ou "receita"
        "data": datetime.now().strftime("%d/%m/%Y"),  # Data de hoje formatada
        "mes": datetime.now().strftime("%Y-%m")       # Mês para filtrar depois (ex: "2025-06")
    }

    lancamentos.append(novo)  # Adicionamos à lista
    proximo_id += 1           # Incrementamos o contador de IDs

    # Retornamos o lançamento criado com status 201 (Created)
    return jsonify(novo), 201


# DELETE /lancamentos/<id> — exclui um lançamento pelo ID
@app.route('/lancamentos/<int:id>', methods=['DELETE'])
def delete_lancamento(id):
    global lancamentos

    # Filtramos a lista mantendo todos EXCETO o que tem o ID informado
    lancamentos_filtrados = [l for l in lancamentos if l['id'] != id]

    # Se o tamanho não mudou, o ID não existia
    if len(lancamentos_filtrados) == len(lancamentos):
        return jsonify({"erro": "Lançamento não encontrado"}), 404

    lancamentos = lancamentos_filtrados
    return jsonify({"mensagem": "Lançamento excluído com sucesso"})


# DELETE /lancamentos - exclui TODOS os lançamentos
@app.route('/lancamentos', methods=['DELETE'])
def delete_todos_lancamentos():
    global lancamentos
    global proximo_id

    lancamentos = []
    proximo_id = 1

    return jsonify({
        "mensagem": "Todos os lançamentos foram excluídos com sucesso"
    })


# GET /resumo — calcula saldo atual e total do mês
@app.route('/resumo', methods=['GET'])
def get_resumo():
    mes_atual = datetime.now().strftime("%Y-%m")  # Mês atual no formato "2025-06"

    total_receitas = 0.0
    total_gastos = 0.0
    receitas_mes = 0.0
    gastos_mes = 0.0

    # Percorremos todos os lançamentos calculando os totais
    for l in lancamentos:
        if l['tipo'] == 'receita':
            total_receitas += l['valor']
            if l['mes'] == mes_atual:
                receitas_mes += l['valor']
        else:  # gasto
            total_gastos += l['valor']
            if l['mes'] == mes_atual:
                gastos_mes += l['valor']

    return jsonify({
        "saldo_atual": round(total_receitas - total_gastos, 2),   # Saldo geral
        "total_receitas": round(total_receitas, 2),
        "total_gastos": round(total_gastos, 2),
        "receitas_mes": round(receitas_mes, 2),                   # Só do mês atual
        "gastos_mes": round(gastos_mes, 2),
        "saldo_mes": round(receitas_mes - gastos_mes, 2)          # Saldo só do mês
    })


# -------------------------------------------------------
# INICIALIZAÇÃO DO SERVIDOR
# -------------------------------------------------------
if __name__ == '__main__':
    porta = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=porta, debug=True)