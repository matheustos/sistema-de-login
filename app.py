from flask import Flask, request, jsonify
from bd import criar, buscar, buscar_senha, update_senha, localiza_usuarios, localiza_cpf, deleta_usuario
from hashlib import sha256
import re

app = Flask(__name__)

# rota de cadastro
@app.route('/cadastro', methods=['POST'])
def criar_cadastro():
    dados = request.get_json()

    # verifica se já existe usuário com os dados informados no banco de dados
    verificacao = localiza_cpf(cpf=dados['cpf'])

    if verificacao is None:
        
        # função para verificar se existem caracteres especiais na senha passada
        def possui_numeros_ou_especiais(string):
            padrao = r'[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]'
            if re.search(padrao, string):
                return True
            else:
                return False


        resposta = possui_numeros_ou_especiais(string=dados['senha'])

        if resposta == True:
        # verifica se a senha informado contem 8 ou mais caracteres
            if len(dados['senha']) >= 8:
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
            
            # caso a função não retorne uma resposta True, avisa ao usuário que a senha deve conter 8 ou mais caracteres
            else:
                return jsonify({
                    "message": "A senha deve ter no mínimo 8 caracteres"
                })
        # caso a função não retorne uma resposta True, avisa ao usuário que a senha deve conter caracteres especiais
        else:
            return jsonify({
                "message": "A senha deve conter caracteres especiais"
            })
    else:
        return jsonify({
            "message": "Usuário já cadastrado!"
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
    
    # realiza consulta na tabela cadastro do banco de dados 
    try:
        resultado = buscar(tabela="cadastro", condicao=dados_login['email'])
    # mensagem apresentada caso aconteça um erro na consulta ao banco de dados
    except:
        return jsonify({"message": "Erro ao realizar busca no banco de dados."})
    # checa email e senha
    else:
        if len(resultado) != 0:
            email = resultado[2]
            senha = resultado[3]
            
            # libera o login se as informações coincidirem
            if email == dados_login['email'] and senha == hash_senha:
                return jsonify({"message": "login efetuado com sucesso!"})
            # informa que os dados passados estão incorretos
            else:
                return jsonify({"message": "Email e/ou senha incorretos."})
    

@app.route('/esqueceu-a-senha', methods=['POST'])
def realizar_reset_senha():

    dados_nova_senha = request.get_json()

    nova_senha = dados_nova_senha['senha']

    # função para verificar se existem caracteres especiais na nova senha passada
    def possui_numeros_ou_especiais(string):
        padrao = r'[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]'
        if re.search(padrao, string):
            return True
        else:
            return False


    resposta = possui_numeros_ou_especiais(string=dados_nova_senha['senha'])
    
    # verifica se a senha informado contem 8 ou mais caracteres
    if len(dados_nova_senha['senha']) >= 8:
        # caso a senha tenha 8 ou mais números, verifica se a resposta da função acima é True
        if resposta == True:
            # Cria um objeto hash SHA-256
            hash = sha256(nova_senha.encode())

            # Obtém o hash resultante em formato hexadecimal
            hash_senha = hash.hexdigest()

            resultado = buscar_senha(email=dados_nova_senha['email'], cpf=dados_nova_senha['cpf'], tabela="cadastro")

            # verifica se existe um resultado na consulta do banco de dados
            if len(resultado) != 0:  
                # tenta atualizar a senha  
                try:
                    update_senha(senha=hash_senha, email=dados_nova_senha['email'], cpf=dados_nova_senha['cpf'])
                # retorno caso aconteça algum erro
                except:
                    return jsonify({"message": "Erro ao atualizar a senha!"})
                # retorno caso ocorra tudo certo
                else:
                    return jsonify({"message": "Senha alterada com sucesso!"})
                
                
            else:
                return jsonify({
                    "message": "Não foi encontrado usuário com esses dados cadastrados."
                })
            
         # caso a função não retorne uma resposta True, avisa ao usuário que a senha deve conter caracteres especiais
        else:
            return jsonify({
                "message": "A senha deve conter caracteres especiais"
            })
       
    # caso a função não retorne uma resposta True, avisa ao usuário que a senha deve conter 8 ou mais caracteres
    else:
        return jsonify({
            "message": "A senha deve ter no mínimo 8 caracteres"
        })
    
@app.route('/usuarios', methods = ['GET'])
def busca_usuarios():
    # tenta localizar usuários
    try:
        resposta = localiza_usuarios()
    # informação caso apresente algum erro na consulta
    except:
        return jsonify({
            "message": "Erro ao consultar banco de dados"
        })
    # retorna os dados da consulta 
    else:
        return jsonify(resposta)

@app.route('/usuarios/cpf', methods = ['POST'])
def busca_cpf():
    cpf = request.get_json()
    
    retorno = localiza_cpf(cpf=cpf['cpf'])
    # retorna os dados do usuário, com excessão da senha, caso o resultado da consulta não seja nulo
    if retorno is not None:
        return jsonify({
            "id": retorno[0],
            "nome": retorno[1],
            "email": retorno[2],
            "data_nascimento": retorno[4],
            "cpf": retorno[5],
            "rg": retorno[6]
        })
    # retorna uma mensagem informando que não foram encontrados usuários no banco de dados
    else:
        return jsonify({
            "message": "Não foi encontrado nenhum usuário com esse cpf!"
        })

@app.route('/deleta-usuario', methods = ['DELETE'])
def delete():
    dados_delete = request.get_json()
    # tenta realizar delete de usuário
    try:
        deleta_usuario(cpf=dados_delete['cpf'])
    # mensagem caso aconteça algum erro
    except:
        return jsonify({
            "message": "Erro ao deletar usuário!"
        })
    # mensagem caso o delete aconteça sem falhas
    else:
        return jsonify({
            "message": "Usuário deletado com sucesso!"
        })
    

if __name__ == '__main__':
    app.run(debug=True)