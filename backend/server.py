from flask import Flask, request, jsonify
from flask_cors import CORS

# Inicialização da aplicação Flask
app = Flask(__name__)
CORS(app)

# Dicionário para armazenar os usuários temporariamente (em memória)
usuarios = {}

# Dicionário para armazenar os resíduos temporariamente (em memória)
residuos = []

# Rota de login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Verifica se o email existe e se a senha bate
    if email in usuarios and usuarios[email]['senha'] == password:
        return jsonify({"message": "Login bem-sucedido!", "authenticated": True}), 200
    else:
        return jsonify({"message": "Credenciais inválidas!", "authenticated": False}), 401

# Rota de cadastro de usuário
@app.route('/api/usuarios/cadastro', methods=['POST'])
def cadastro():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')  # Agora usamos o email para cadastro
    senha = data.get('senha')
    grupo = data.get('grupo')

    # Lógica para salvar o usuário no banco de dados (aqui usamos o dicionário)
    if email in usuarios:  # Verifica se o email já foi cadastrado
        return jsonify({"message": "Usuário já existe!"}), 400  # Usuário já cadastrado

    # Armazenando o usuário no dicionário com email como chave para a busca
    usuarios[email] = {'nome': nome, 'senha': senha, 'grupo': grupo}
    return jsonify({"message": f"Usuário {nome} cadastrado com sucesso!"}), 200

# Rota para redefinir a senha
@app.route('/api/usuarios/redefinir-senha', methods=['POST'])
def redefinir_senha():
    data = request.get_json()
    email = data.get('email')
    nova_senha = data.get('novaSenha')

    # Verificando se o usuário existe pelo e-mail
    if email not in usuarios:
        return jsonify({"error": "E-mail não encontrado!"}), 400
    
    # Atualiza a senha do usuário
    usuarios[email]['senha'] = nova_senha
    return jsonify({"message": "Senha redefinida com sucesso!"}), 200

# Rota para cadastrar um resíduo
@app.route('/api/residuos/cadastrar', methods=['POST'])
def cadastrar_residuo():
    data = request.get_json()

    # Coletando os dados do resíduo
    nome = data.get('nome')
    tipo = data.get('tipo')
    peso = data.get('peso')
    unidade = data.get('unidade')
    local_descart = data.get('local_descart')

    # Salvando o resíduo no dicionário
    residuos.append({
        'nome': nome,
        'tipo': tipo,
        'peso': peso,
        'unidade': unidade,
        'local_descart': local_descart
    })

    return jsonify({"message": "Resíduo cadastrado com sucesso!"}), 200

# Rota para listar todos os resíduos cadastrados
@app.route('/api/residuos/listar', methods=['GET'])
def listar_residuos():
    return jsonify({"residuos": residuos}), 200

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
