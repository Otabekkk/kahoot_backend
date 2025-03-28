from flask import Flask, jsonify, request
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


from models import Admin, Test, db, Player, Answer
db.init_app(app)
with app.app_context():
    db.create_all()
# migrate = Migrate(app, db)


@app.route('/register', methods = ['POST'])
def register():
    """
    Регистрация нового администратора
    ---
    tags:
      - Аутентификация
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "admin123"
            password:
              type: string
              example: "securepassword"
    responses:
      200:
        description: Успешная регистрация
        schema:
          type: object
          properties:
            Success:
              type: string
      400:
        description: Ошибка валидации
    """
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'Error': 'Username and password are required'}), 400

        # Нормализация данных
        username = data['username'].strip()
        password = data['password']

        # Проверка существования (с учетом регистра)
        if Admin.query.filter_by(username = username).first():
            return jsonify({'Error': 'Username already exists'}), 400

        # Создание и сохранение
        admin = Admin(username=username, password=password)
        db.session.add(admin)
        db.session.commit()

        return jsonify({'Success': 'Admin created', 'id': admin.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'Error': 'Database error', 'details': str(e)}), 500


@app.route('/login', methods = ['POST'])
def login():
    """
    Аутентификация администратора
    ---
    tags:
      - Аутентификация
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "admin123"
            password:
              type: string
              example: "securepassword"
    responses:
      200:
        description: Успешная аутентификация
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Неверные учетные данные
    """
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
    """
    Создание нового теста
    ---
    tags:
      - Тесты
    security:
      - JWT: []
    responses:
      200:
        description: Тест успешно создан
        schema:
          type: object
          properties:
            Success:
              type: string
            Test id:
              type: integer
      401:
        description: Не авторизован
    """
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
    tags:
      - Администраторы
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
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
      404:
        description: Администратор не найден
    """

    admin = Admin.query.get(user_id)
    if not admin:
        return jsonify({'Error': 'User not found'}), 404
    
    return jsonify({'id': admin.id, 'username': admin.username})


@app.route('/admins/<int:user_id>/tests', methods = ['GET'])
def get_admin_tests(user_id):
    """
    Получить все тесты администратора
    ---
    tags:
      - Администраторы
      - Тесты
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID администратора
    responses:
      200:
        description: Список тестов
        schema:
          type: object
          properties:
            user_id:
              type: integer
            tests:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
      404:
        description: Администратор не найден
    """
    admin = Admin.query.get(user_id)
    if not admin:
        return jsonify({'Error': 'User not found'}), 404
    
    tests = [{'id': test.id} for test in admin.tests]

    return jsonify({"user_id": admin.id, "tests": tests})


# @app.route('/api/admins', methods = ['POST'])
# def create_admin():
#     """
#     Создание администратора
#     ---
#     tags:
#       - Администраторы
#     parameters:
#       - in: body
#         name: body
#         required: true
#         schema:
#           type: object
#           properties:
#             username:
#               type: string
#               description: Имя пользователя
#               example: "admin123"
#             password:
#               type: string
#               description: Пароль
#               example: "secret"
#     responses:
#       201:
#         description: Администратор создан
#         schema:
#           type: object
#           properties:
#             id:
#               type: integer
#             username:
#               type: string
#       400:
#         description: Ошибка валидации
#       500:
#         description: Внутренняя ошибка сервера
#     """

#     data = request.get_json()
#     try:
#         admin = Admin(
#             username = data['username'],
#             password = data['password']
#         )

#         db.session.add(admin)
#         db.session.commit()

#         return jsonify({'id': admin.id, 'username': admin.username}), 201
    
#     except Exception as ex:
#         db.session.rollback()
#         return jsonify({'Error': str(ex)})


@app.route('/games/join', methods=['POST'])
def join_game():
    """
    Присоединение игрока к игре
    ---
    tags:
      - Игры
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: Имя игрока
              example: "player1"
    responses:
      201:
        description: Игрок создан
        schema:
          type: object
          properties:
            player_id:
              type: integer
    """
    data = request.get_json()
    player = Player(username=data['username'], score=0)
    db.session.add(player)
    db.session.commit()
    return jsonify({"player_id": player.id}), 201



@app.route('/games/answer', methods=['POST'])
def submit_answer():
    """
    Отправка ответа на вопрос
    ---
    tags:
      - Игры
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            answer_id:
              type: integer
              description: ID ответа
              example: 1
            player_id:
              type: integer
              description: ID игрока
              example: 1
    responses:
      200:
        description: Результат ответа
        schema:
          type: object
          properties:
            correct:
              type: boolean
            score:
              type: integer
    """
    data = request.get_json()
    answer = Answer.query.get(data['answer_id'])
    player = Player.query.get(data['player_id'])
    
    if answer.is_correct:
        player.score += answer.question.points
        db.session.commit()
    
    return jsonify({"correct": answer.is_correct, "score": player.score}), 200


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)