from flask import Flask, request, redirect, render_template, url_for, session
from bd import criar, buscar, buscar_senha, update_senha, localiza_cpf
from hashlib import sha256
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = 'chave_secreta'

# função para checar se usuário está logado
def is_logged_in():
    return 'user_id' in session

@app.route('/', methods = ['GET', 'POST'])
def home():
    return render_template("index.html")


# rota de cadastro
@app.route('/register', methods=['GET', 'POST'])
def criar_cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        data_nascimento = request.form['data_nascimento']
        cpf = request.form['cpf']
        rg = request.form['rg']
        

        # verifica se já existe usuário com os dados informados no banco de dados
        verificacao = localiza_cpf(cpf=cpf)

        if verificacao is None:
            
            # função para verificar se existem caracteres especiais na senha passada
            def possui_numeros_ou_especiais(string):
                padrao = r'[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]'
                if re.search(padrao, string):
                    return True
                else:
                    return False


            resposta = possui_numeros_ou_especiais(string=senha)

            if resposta == True:
            # verifica se a senha informado contem 8 ou mais caracteres
                if len(senha) >= 8:
                    # Cria um objeto hash SHA-256
                    hash = sha256(senha.encode())

                    # Obtém o hash resultante em formato hexadecimal
                    hash_senha = hash.hexdigest()

                    try:
                        criar(nome=nome, email=email, senha=hash_senha, data_nascimento=data_nascimento, cpf=cpf, rg=rg)
                        return redirect(url_for('login'))
                    except:
                        error = "Falha ao cadastrar usuário"
                        return render_template("register.html", error=error)
                
                # caso a função não retorne uma resposta True, avisa ao usuário que a senha deve conter 8 ou mais caracteres
                else:
                    error = "A senha deve ter no mínimo 8 caracteres"
                    return render_template('register.html', error=error)
            # caso a função não retorne uma resposta True, avisa ao usuário que a senha deve conter caracteres especiais
            else:
                error = "A senha deve conter caracteres especiais"
                return render_template('register.html', error=error)
        else:
            error = "Usuário já cadastrado!"
            return render_template('register.html', error=error) 
    else:
        return render_template('register.html')
    
# rota para validar login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']

        # Cria um objeto hash SHA-256
        hash = sha256(senha.encode())

        # Obtém o hash resultante em formato hexadecimal
        hash_senha = hash.hexdigest()
        
        # realiza consulta na tabela cadastro do banco de dados 
        try:
            resultado = buscar(tabela="cadastro", condicao=email)
        # mensagem apresentada caso aconteça um erro na consulta ao banco de dados
        except:
            error = "Erro ao realizar busca no banco de dados."
            return render_template('login.html', error=error)
        # checa email e senha
        else:
            if len(resultado) != 0:
                email = resultado[2]
                senha = resultado[3]
                id = resultado[0]
                
                def autentic():
                    # libera o login se as informações coincidirem
                    if email == email and senha == hash_senha:
                        return id
                    # informa que os dados passados estão incorretos
                    else:
                        error = "Email e/ou senha incorretos."
                        return render_template('login.html', error=error)
                
                # Após autenticar o usuário, adicione o ID do usuário à sessão
                user_id = autentic()

                if user_id:
                    # Autenticação bem-sucedida, adiciona o ID do usuário à sessão
                    session['user_id'] = user_id
                    return redirect(url_for('sucesso'))
                else:
                    # Tratamento para falha na autenticação
                    return redirect(url_for('login'))
                
                
    else:
        return render_template('login.html')
    
@app.route('/sucesso')
def sucesso():
    # redireciona para a página de login caso o usuário não esteja na sessão
    if not is_logged_in():
        return redirect(url_for('login'))
    else:
        return render_template('pagina.html')


@app.route('/esqueceu-a-senha', methods=['GET','POST'])
def realizar_reset_senha():

    if request.method == 'POST':
        nova_senha = request.form['senha']
        confirmacao = request.form['senha_ok']
        email = request.form['email']
        cpf = request.form['cpf']

        if nova_senha == confirmacao:

            # função para verificar se existem caracteres especiais na nova senha passada
            def possui_numeros_ou_especiais(string):
                padrao = r'[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]'
                if re.search(padrao, string):
                    return True
                else:
                    return False


            resposta = possui_numeros_ou_especiais(string=nova_senha)
            
            # verifica se a senha informado contem 8 ou mais caracteres
            if len(nova_senha) >= 8:
                # caso a senha tenha 8 ou mais números, verifica se a resposta da função acima é True
                if resposta == True:
                    # Cria um objeto hash SHA-256
                    hash = sha256(nova_senha.encode())

                    # Obtém o hash resultante em formato hexadecimal
                    hash_senha = hash.hexdigest()

                    resultado = buscar_senha(email=email, cpf=cpf, tabela="cadastro")

                    # verifica se existe um resultado na consulta do banco de dados
                    if len(resultado) != 0:  
                        # tenta atualizar a senha  
                        try:
                            update_senha(senha=hash_senha, email=email, cpf=cpf)
                        # retorno caso aconteça algum erro
                        except:
                            error = "Erro ao atualizar a senha!"   
                            return render_template('reset.html', error=error)
                        # retorno caso ocorra tudo certo
                        else:
                            message = "Senha alterada com sucesso!"
                            return render_template('reset.html')
                        
                        
                    else:
                        error = "Não foi encontrado usuário com esses dados cadastrados."
                        return render_template('reset.html', error=error)
                    
                # caso a função não retorne uma resposta True, avisa ao usuário que a senha deve conter caracteres especiais
                else:
                    error = "A senha deve conter caracteres especiais"
                    return render_template('reset.html', error=error)
            
            # caso a função não retorne uma resposta True, avisa ao usuário que a senha deve conter 8 ou mais caracteres
            else:
                error = "A senha deve ter no mínimo 8 caracteres"
                return render_template('reset.html', error=error)
        else:
            error = "As senhas devem coincidir!"
            return render_template('reset.html', error=error)
    else:
        return render_template('reset.html')
    
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    # Remover o usuário caso ele aperte no botão de sair no formulário
    session.pop('user_id', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)