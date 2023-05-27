import mysql.connector

try:
    conexao = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password= '',
        database='sistema-de-login'
    )
except:
    print("ERRO")

cursor = conexao.cursor()

# Tabela de cadastro de cadastro
cursor.execute("""
    CREATE TABLE IF NOT EXISTS cadastro (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(45),
        email VARCHAR(45),
        senha VARCHAR(100),
        data_nascimento VARCHAR(45),
        cpf VARCHAR(11), 
        rg VARCHAR(20)
    )
""")

def criar(nome, email, senha, data_nascimento, cpf, rg):
    comando = f"INSERT INTO cadastro(nome, email, senha, data_nascimento, cpf, rg) VALUES ('{nome}', '{email}', '{senha}', '{data_nascimento}', '{cpf}', '{rg}')"
    cursor.execute(comando)
    conexao.commit()


def buscar(tabela, condicao):

    cursor = conexao.cursor()
    comando_leitor = f"SELECT * FROM {tabela} WHERE email = '{condicao}'"
    cursor.execute(comando_leitor)
    resultado = cursor.fetchone()
    return resultado

def buscar_senha(email, cpf, tabela):
    cursor = conexao.cursor()
    comando_leitor = f"SELECT * FROM {tabela} WHERE email = '{email}' AND {cpf}"
    cursor.execute(comando_leitor)
    resultado = cursor.fetchone()
    return resultado


def update_senha(senha, email, cpf):
    comando = f"UPDATE cadastro SET senha = '{senha}' WHERE email = '{email}' AND cpf = '{cpf}'"
    cursor.execute(comando)
    conexao.commit()










cursor.close
conexao.close