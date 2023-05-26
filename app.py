from flask import Flask, request, jsonify
from bd import criar
from hashlib import sha256

app = Flask(__name__)

# rota de cadastro
@app.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()

    senha = dados['senha']
    # Cria um objeto hash SHA-256
    hash = sha256(senha.encode())

    # Obtém o hash resultante em formato hexadecimal
    hash_senha = hash.hexdigest()

    try:
        criar(nome=dados['nome'], email=dados['email'], senha=hash_senha, data_nascimento=dados['data_nascimento'], cpf=dados['cpf'], rg=dados['rg'])
    except:
        return jsonify({
            "message": "Erro ao cadastrar no banco de dados!"
        })
    else: 
        return jsonify({
            "message": "Dados cadastrados com sucesso!"
        })
   



if __name__ == '__main__':
    app.run(debug=True)