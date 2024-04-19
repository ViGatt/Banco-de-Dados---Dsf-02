from flask import Flask, jsonify, request
import sqlite3
import os
import csv

app = Flask(__name__)
DATABASE_URI = 'DBCars.db'
CSV_FILE = "C:/Users/User/Desktop/Cars_AI/CarsData.csv"
def criar_tabela_carros():
    try:
        if not os.path.exists(DATABASE_URI):
            open(DATABASE_URI, 'w').close()  # Cria o arquivo do banco de dados se não existir
            
            # Criação da tabela CARROS
            Data_Base = sqlite3.connect(DATABASE_URI)
            db_cursor = Data_Base.cursor()
            db_cursor.execute('''CREATE TABLE IF NOT EXISTS "CARROS" (
                                "MODEL" varchar(50) PRIMARY KEY,
                                "YEAR" integer,
                                "PRECO" float,
                                "TRANSMISSAO" varchar(50),
                                "MILHAGEM" integer,
                                "COMBUSTIVEL" varchar(50),
                                "TAXA" integer,
                                "MPG" integer,
                                "ENGINE" float,
                                "MANUFACTURER" varchar(50)
                                )''')
            Data_Base.commit()
            print("Tabela 'CARROS' criada com sucesso.")
            
            # Leitura do arquivo CSV e inserção dos dados distintos no banco de dados
            with open(CSV_FILE, 'r', encoding='utf-8') as arquivo_csv:
                leitor_csv = csv.DictReader(arquivo_csv)
                for i in leitor_csv:
                    # Remover espaços extras dos valores lidos do CSV
                    i = {chave.strip(): valor.strip() for chave, valor in i.items()}
                    db_cursor.execute('''INSERT OR IGNORE INTO CARROS (MODEL, YEAR, PRECO, TRANSMISSAO, MILHAGEM, COMBUSTIVEL, TAXA, MPG, ENGINE, MANUFACTURER) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (i['MODEL'], i['YEAR'], i['PRECO'], i['TRANSMISSAO'], i['MILHAGEM'], 
                        i['COMBUSTIVEL'], i['TAXA'], i['MPG'], i['ENGINE'], i['MANUFACTURER']))
                Data_Base.commit()
                Data_Base.close()
                print("Dados distintos do arquivo CSV inseridos no banco de dados com sucesso.")
    except Exception as Error:
        print(f"Erro ao criar tabela 'CARROS' e inserir dados distintos do CSV: {Error}")

# Obter JSON com todos os modelos existentes no Banco de Dados
@app.route('/carros', methods=['GET'])
def obter_carros():
    try:
        Data_Base = sqlite3.connect(DATABASE_URI)
        db_cursor = Data_Base.cursor()
        db_cursor.execute('SELECT MODEL FROM CARROS')
        modelos = [row[0] for row in db_cursor.fetchall()]
        Data_Base.close()

        return jsonify(modelos), 200
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

# Obter JSON com as informações do carro desejado
@app.route('/carros/marca/<marca>', methods=['GET'])
def obter_carros_por_marca(marca):
    try:
        Data_Base = sqlite3.connect(DATABASE_URI)
        db_cursor = Data_Base.cursor()
        db_cursor.execute(f"SELECT MODEL FROM CARROS WHERE MANUFACTURER = '{marca}'")
        modelos = [row[0] for row in db_cursor.fetchall()]
        Data_Base.close() 

        if modelos:
            return jsonify(modelos), 200
        else:
            return jsonify({"mensagem": "Nenhum carro encontrado para esse fabricante"}), 404
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500
    
# Obter informações do carro passado pelo get
@app.route('/carros/modelo/<modelo>', methods=['GET'])
def obter_carro_por_modelo(modelo):
    try:
        Data_Base = sqlite3.connect(DATABASE_URI)
        db_cursor = Data_Base.cursor()
        db_cursor.execute(f"SELECT * FROM CARROS WHERE MODEL = '{modelo}'")
        carro = db_cursor.fetchone()
        Data_Base.close()

        if carro:
            # Convertendo a linha do banco de dados para um dicionário para facilitar a serialização JSON
            carro_info = {
                "model": carro[0],
                "year": carro[1],
                "preco": carro[2],
                "transmissao": carro[3],
                "milhagem": carro[4],
                "combustivel": carro[5],
                "taxa": carro[6],
                "mpg": carro[7],
                "engine": carro[8],
                "manufacturer": carro[9]
            }
            return jsonify(carro_info), 200
        else:
            return jsonify({"mensagem": "Nenhum carro encontrado com esse modelo"}), 404
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500
    
# Realizar a adção de algum carro/especificações passadas por um JSON
@app.route('/adicionar/carros', methods=['POST'])
def adicionar_carro():
    try:
        dados = request.json
        if not dados:
            return jsonify({"erro": "Dados de atualização ausentes"}), 400
        
        Data_Base = sqlite3.connect(DATABASE_URI)
        db_cursor = Data_Base.cursor()
        db_cursor.execute('''INSERT INTO CARROS (MODEL, YEAR, PRECO, TRANSMISSAO, MILHAGEM, COMBUSTIVEL, TAXA, MPG, ENGINE, MANUFACTURER) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    tuple(dados.values()))
        Data_Base.commit()
        Data_Base.close()

        return jsonify({"mensagem": "Carro adicionado com sucesso"}), 201
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

# Atualizar o modelo/informações do carro pelo JSON passado
@app.route('/update/carros/<modelo>', methods=['PUT'])
def atualizar_carro(modelo):
    try:
        dados = request.json
        if not dados:
            return jsonify({"erro": "Dados de atualização ausentes"}), 400
        
        Data_Base = sqlite3.connect(DATABASE_URI)
        db_cursor = Data_Base.cursor()

        # Verificar se o modelo existe antes de atualizar
        db_cursor.execute(f"SELECT 1 FROM CARROS WHERE MODEL = '{modelo}'")
        if not db_cursor.fetchone():
            Data_Base.close()
            return jsonify({"erro": "Modelo de carro não encontrado"}), 404

        # Atualizar o carro
        db_cursor.execute('''UPDATE CARROS SET YEAR=?, PRECO=?, TRANSMISSAO=?, MILHAGEM=?, COMBUSTIVEL=?, TAXA=?, MPG=?, ENGINE=?, MANUFACTURER=? 
                             WHERE MODEL=?''', 
                    (dados.get('YEAR'), dados.get('PRECO'), dados.get('TRANSMISSAO'), dados.get('MILHAGEM'), 
                     dados.get('COMBUSTIVEL'), dados.get('TAXA'), dados.get('MPG'), dados.get('ENGINE'), 
                     dados.get('MANUFACTURER'), modelo))
        Data_Base.commit()
        Data_Base.close()   

        return jsonify({"mensagem": "Carro atualizado com sucesso"}), 200
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

#Deletar o carro informado
@app.route('/deletar/carros/<modelo>', methods=['DELETE'])
def deletar_carro(modelo):
    try:
        Data_Base = sqlite3.connect(DATABASE_URI)
        db_cursor = Data_Base.cursor()
        db_cursor.execute(f"DELETE FROM CARROS WHERE MODEL='{modelo}'")
        Data_Base.commit()
        Data_Base.close()

        return jsonify({"mensagem": "Carro deletado com sucesso"}), 200
    except Exception:
        return jsonify({"erro": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    criar_tabela_carros()
    app.run(debug=True)
