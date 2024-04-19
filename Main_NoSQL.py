import csv
from flask import Flask, jsonify, request
import pymongo

app = Flask(__name__)
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['carros_db']
collection = db['carros']

CSV_FILE = "C:/Users/User/Desktop/Cars_AI/CarsData.csv"

def criar_banco_de_dados():
    # Verificar se a coleção já existe
    if 'carros' in db.list_collection_names():
        print("Coleção 'carros' já existe no banco de dados.")
        return
    
    try:
        # Leitura do arquivo CSV e inserção dos dados no MongoDB
        with open(CSV_FILE, 'r', encoding='utf-8') as arquivo_csv:
            leitor_csv = csv.DictReader(arquivo_csv)
            for linha in leitor_csv:
                # Remover espaços extras dos valores lidos do CSV
                carro = {chave.strip(): valor.strip() for chave, valor in linha.items()}
                # Verificar se o carro já existe na coleção
                if not collection.find_one({'MODEL': carro['MODEL']}):
                    collection.insert_one(carro)
            print("Dados do arquivo CSV inseridos no banco de dados com sucesso.")
    except Exception as error:
        print(f"Erro ao inserir dados do CSV no banco de dados: {error}")

@ app.route('/carros', methods=['GET'])
def obter_carros():
    try:
        modelos = [carro['MODEL'] for carro in collection.find({}, {'_id': 0, 'MODEL': 1})]
        return jsonify(modelos), 200
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

@app.route('/carros/marca/<marca>', methods=['GET'])
def obter_carros_por_marca(marca):
    try:
        modelos = [carro['MODEL'] for carro in collection.find({'MANUFACTURER': marca}, {'_id': 0, 'MODEL': 1})]
        if modelos:
            return jsonify(modelos), 200
        else:
            return jsonify({"mensagem": f"Nenhum carro encontrado para a marca '{marca}'"}), 404
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

@ app.route('/carros/modelo/<modelo>', methods=['GET'])
def obter_carro_por_modelo(modelo):
    try:
        carro = collection.find_one({'MODEL': modelo}, {'_id': 0})
        if carro:
            return jsonify(carro), 200
        else:
            return jsonify({"mensagem": "Nenhum carro encontrado com esse modelo"}), 404
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

@ app.route('/adicionar/carros', methods=['POST'])
def adicionar_carro():
    try:
        dados = request.json
        collection.insert_one(dados)
        return jsonify({"mensagem": "Carro adicionado com sucesso"}), 201
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

@ app.route('/update/carros/<modelo>', methods=['PUT'])
def atualizar_carro(modelo):
    try:
        dados = request.json
        result = collection.update_one({'MODEL': modelo}, {'$set': dados})
        if result.modified_count > 0:
            return jsonify({"mensagem": "Carro atualizado com sucesso"}), 200
        else:
            return jsonify({"erro": "Modelo de carro não encontrado"}), 404
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

@ app.route('/deletar/carros/<modelo>', methods=['DELETE'])
def deletar_carro(modelo):
    try:
        result = collection.delete_one({'MODEL': modelo})
        if result.deleted_count > 0:
            return jsonify({"mensagem": "Carro deletado com sucesso"}), 200
        else:
            return jsonify({"erro": "Modelo de carro não encontrado"}), 404
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    # Chamar a função para criar o banco de dados e inserir dados do CSV, se necessário
    criar_banco_de_dados()
    # Executar o aplicativo Flask
    app.run(debug=True)
