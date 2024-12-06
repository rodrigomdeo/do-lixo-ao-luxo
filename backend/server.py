from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Inicialização da aplicação Flask
app = Flask(__name__)
CORS(app)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///residuos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    grupo = db.Column(db.String(50), nullable=False)

# Modelo de Resíduo com 'unidade' opcional
class Residuo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    peso = db.Column(db.Float, nullable=False)
    unidade = db.Column(db.String(20), nullable=True)  # Tornando 'unidade' opcional
    local_descart = db.Column(db.String(100), nullable=False)

# Função para criar administradores fixos
def create_admins():
    admins = [
        {"nome": "Rodrigo Mendes de Oliveira", "email": "rodrigowmendes18@gmail.com", "senha": "1234", "grupo": "administrador"},
        {"nome": "Felipe da Costa Argolo Vieira", "email": "pizzagamerx@gmail.com", "senha": "1234", "grupo": "administrador"},
        {"nome": "Guilherme de Jesus Santos", "email": "guilhermejs135@gmail.com", "senha": "1234", "grupo": "administrador"}
    ]
    
    for admin in admins:
        if not Usuario.query.filter_by(email=admin["email"]).first():
            hashed_password = generate_password_hash(admin["senha"])
            new_admin = Usuario(nome=admin["nome"], email=admin["email"], senha=hashed_password, grupo=admin["grupo"])
            db.session.add(new_admin)
    
    db.session.commit()

# Função para verificar se o usuário é administrador
def is_admin_user(email):
    admin_emails = [
        "rodrigowmendes18@gmail.com",
        "pizzagamerx@gmail.com",
        "guilhermejs135@gmail.com"
    ]
    return email in admin_emails

# Rota de login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and check_password_hash(usuario.senha, password):
        if usuario.grupo == "administrador" and is_admin_user(email):
            return jsonify({"message": "Login bem-sucedido!", "authenticated": True}), 200
        else:
            return jsonify({"message": "Acesso restrito! Apenas administradores podem logar.", "authenticated": False}), 403
    else:
        return jsonify({"message": "Credenciais inválidas!", "authenticated": False}), 401

# Rota de cadastro de usuário
@app.route('/api/usuarios/cadastro', methods=['POST'])
def cadastro():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    grupo = data.get('grupo')

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"message": "Usuário já existe!"}), 400

    hashed_password = generate_password_hash(senha)
    novo_usuario = Usuario(nome=nome, email=email, senha=hashed_password, grupo=grupo)
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({"message": f"Usuário {nome} cadastrado com sucesso!"}), 200

# Rota para redefinir a senha
@app.route('/api/usuarios/redefinir-senha', methods=['POST'])
def redefinir_senha():
    data = request.get_json()
    email = data.get('email')
    nova_senha = data.get('novaSenha')

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "E-mail não encontrado!"}), 400
    
    usuario.senha = generate_password_hash(nova_senha)
    db.session.commit()
    return jsonify({"message": "Senha redefinida com sucesso!"}), 200

# Rota para cadastrar um resíduo
@app.route('/api/residuos/cadastrar', methods=['POST'])
def cadastrar_residuo():
    data = request.get_json()

    nome = data.get('nome')
    tipo = data.get('tipo')
    peso = data.get('peso')
    unidade = data.get('unidade')  # Se não passar, 'unidade' pode ser None
    local_descart = data.get('local_descart')

    # Verificação de campos obrigatórios
    if not nome or not tipo or not peso or not local_descart:
        return jsonify({"message": "Campos obrigatórios estão faltando!"}), 400

    # Se 'unidade' não for fornecido, podemos definir como 'não especificado'
    if unidade is None:
        unidade = 'não especificado'

    novo_residuo = Residuo(nome=nome, tipo=tipo, peso=peso, unidade=unidade, local_descart=local_descart)
    db.session.add(novo_residuo)
    db.session.commit()

    return jsonify({"message": "Resíduo cadastrado com sucesso!", "redirect": "/pagina-de-residuos"}), 200

# Rota para listar todos os resíduos cadastrados
@app.route('/api/residuos/listar', methods=['GET'])
def listar_residuos():
    residuos = Residuo.query.all()
    residuos_list = [
        {'nome': res.nome, 'tipo': res.tipo, 'peso': res.peso, 'unidade': res.unidade, 'local_descart': res.local_descart}
        for res in residuos
    ]
    return jsonify({"residuos": residuos_list}), 200

# Rota para obter os dados do usuário
@app.route('/api/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        return jsonify({
            "nome": usuario.nome,
            "email": usuario.email,
            "senha": usuario.senha
        }), 200
    else:
        return jsonify({"message": "Usuário não encontrado!"}), 404

# Iniciar o servidor
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admins()
    app.run(debug=True, host='0.0.0.0', port=5000)
