from flask import Flask, request, jsonify
from bd import criar, buscar, buscar_senha, update_senha
from hashlib import sha256

app = Flask(__name__)

# rota de cadastro
@app.route('/cadastro', methods=['POST'])
def criar_cadastro():
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
    
# rota para validar login
@app.route('/validar_login', methods=['POST'])
def validar_login():
    dados_login  = request.get_json()

    senha = dados_login['senha']
    # Cria um objeto hash SHA-256
    hash = sha256(senha.encode())

    # Obtém o hash resultante em formato hexadecimal
    hash_senha = hash.hexdigest()
    
    resultado = buscar(tabela="cadastro", condicao=dados_login['email'])

    try:
        if len(resultado) != 0:
            email = resultado[2]
            senha = resultado[3]

            if email == dados_login['email'] and senha == hash_senha:
                return jsonify({"message": "login efetuado com sucesso!"})
            else:
                return jsonify({"message": "Email e/ou senha incorreto."})
    except:
        return jsonify({"message": "Erro ao realizar buscar no banco de dados."})

@app.route('/esqueceu-a-senha', methods=['POST'])
def realizar_reset_senha():

    dados_nova_senha = request.get_json()

    nova_senha = dados_nova_senha['senha']
    # Cria um objeto hash SHA-256
    hash = sha256(nova_senha.encode())

    # Obtém o hash resultante em formato hexadecimal
    hash_senha = hash.hexdigest()

    resultado = buscar_senha(email=dados_nova_senha['email'], cpf=dados_nova_senha['cpf'], tabela="cadastro")

    if len(resultado) != 0:    
        try:
            update_senha(senha=hash_senha, email=dados_nova_senha['email'], cpf=dados_nova_senha['cpf'])
        except:
            return jsonify({"message": "ERRO"})
        else:
            return jsonify({"message": "OK"})
        
        
    else:
        return jsonify({
            "message": "Não foi encontrado usuário com esses dados cadastrados."
        })



if __name__ == '__main__':
    app.run(debug=True)