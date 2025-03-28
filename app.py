from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import secrets
from flasgger import Swagger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# from flask_migrate import Migrate


app = Flask(__name__)
Swagger(app)
CORS(app)
jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.secret_key = secrets.token_hex(16)


from models import Admin, Test, db
db.init_app(app)
with app.app_context():
    db.create_all()
# migrate = Migrate(app, db)


@app.route('/register', methods = ['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if Admin.query.filter_by(username = username).first():
        return jsonify({'Error': 'Username already exists'})
    
    admin = Admin(username = username, password = password)
    db.session.add(admin)
    db.session.commit()

    return jsonify({'Success': 'Admin created'})


@app.route('/login', methods = ['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    admin = Admin.query.filter_by(username = username, password = password).first()

    if not admin:
        return jsonify({'Error': 'Invalid data'})
    
    access_token = create_access_token(identity = admin.id)

    return jsonify(access_token = access_token)


@app.route('/tests', methods = ['POST'])
@jwt_required()
def create_test():
    user_id = get_jwt_identity()

    test = Test(user_id = user_id)

    db.session.add(test)
    db.session.commit()

    return jsonify({'Success': 'Test created!', 'Test id': test.id})
    


@app.route('/admins/<int:user_id>', methods = ['GET'])
def get_admin(user_id: int):
    """
    Получить информацию об администраторе
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID администратора
    responses:
      200:
        description: Успешный ответ
        schema:
          id: Admin
          properties:
            id:
              type: integer
              description: ID администратора
            username:
              type: string
              description: Имя пользователя
      404:
        description: Администратор не найден
    """

    admin = Admin.query.get(user_id)
    if not admin:
        return jsonify({'Error': 'User not found'}), 404
    
    return jsonify({'id': admin.id, 'username': admin.username})


@app.route('/admins/<int:user_id>/tests', methods = ['GET'])
def get_admin_tests(user_id):
    admin = Admin.query.get(user_id)
    if not admin:
        return jsonify({'Error': 'User not found'}), 404
    
    tests = [{'id': test.id} for test in admin.tests]

    return jsonify({"user_id": admin.id, "tests": tests})


@app.route('/api/admins', methods = ['POST'])
def create_admin():
    """
    Создание администратора
    ---
    tags:
      - Администраторы
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: Имя пользователя
              example: "admin123"
            password:
              type: string
              description: Пароль
              example: "secret"
    responses:
      201:
        description: Администратор создан
        schema:
          type: object
          properties:
            id:
              type: integer
              description: ID администратора
            username:
              type: string
              description: Имя пользователя
      400:
        description: Ошибка валидации
      500:
        description: Внутренняя ошибка сервера
    """

    data = request.get_json()
    try:
        admin = Admin(
            username = data['username'],
            password = data['password']
        )

        db.session.add(admin)
        db.session.commit()

        return jsonify({'id': admin.id, 'username': admin.username}), 201
    
    except Exception as ex:
        db.session.rollback()
        return jsonify({'Error': str(ex)})


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)