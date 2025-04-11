from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, emit, leave_room
from models import db, Quiz, Question
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import datetime
from flasgger import Swagger
from auth import auth_bp
from admins import admin_bp

from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

jwt = JWTManager()

app = Flask(__name__)
app.config.from_object('config')
app.register_blueprint(auth_bp, url_prefix = '/auth')
app.register_blueprint(admin_bp, url_prefix = '/admins')

app.config['SWAGGER'] = {
    'title': 'Quiz Game API',
    'uiversion': 3,
    'description': 'API for creating and managing quiz games with real-time multiplayer functionality',
    'version': '1.0.0',
    'termsOfService': '',
    'tags': [
        {
            'name': 'Quizzes',
            'description': 'Operations with quizzes'
        },
        {
            'name': 'Questions',
            'description': 'Operations with questions'
        },
        {
            'name': 'Game',
            'description': 'Real-time game operations'
        }
    ]
}


swagger = Swagger(app)

db.init_app(app)

with app.app_context():
    db.create_all()

Migrate(app, db)

CORS(app)

jwt.init_app(app)

socketio = SocketIO(app, cors_allowed_origins = '*', async_mode="eventlet")

active_games = {}
game_states = {}

@jwt.expired_token_loader
def expiredTokenCallBack(jwt_header, jwt_data):
    return jsonify({
        'Message':'Token has expired',
        'Error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalidTokenCallBack(error):
    return jsonify({
        'Message': 'Signature verification failed',
        'Error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missinTokenCallBack(error):
    return jsonify({
        'Message': 'Request does not contain valid token',
        'Error': 'authorization_header'
    }), 401


def write_log(message):
    with open('logs.txt', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")


def get_questions(quiz_id: str):
    questions = Quiz.query.filter_by(quiz_id = quiz_id).first().questions
    return questions


@app.route('/quizzes', methods=['POST'])
def create_quiz():
    """
    Create a new quiz
    ---
    tags:
      - Quizzes
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - quiz_id
          properties:
            title:
              type: string
              description: Title of the quiz
            quiz_id:
              type: string
              description: Unique identifier for the quiz
    responses:
      201:
        description: Quiz created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Quiz created
            quiz_id:
              type: integer
              example: 1
      400:
        description: Missing required fields
    """
    data = request.get_json()

    new_quiz = Quiz(title=data['title'], quiz_id=data['quiz_id'])

    db.session.add(new_quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz created', 'quiz_id': new_quiz.id}), 201

@app.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
def add_question(quiz_id: int):
    """
    Add a question to a quiz
    ---
    tags:
      - Questions
    parameters:
      - in: path
        name: quiz_id
        required: true
        type: integer
        description: ID of the quiz to add question to
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - text
            - option_1
            - option_2
            - option_3
            - option_4
            - correct_option
          properties:
            text:
              type: string
              description: The question text
            option_1:
              type: string
              description: First answer option
            option_2:
              type: string
              description: Second answer option
            option_3:
              type: string
              description: Third answer option
            option_4:
              type: string
              description: Fourth answer option
            correct_option:
              type: string
              description: Correct option (e.g. "option_1")
    responses:
      201:
        description: Question added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Question added
            question_id:
              type: integer
              example: 1
      404:
        description: Quiz not found
    """
    data = request.get_json()
    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    new_question = Question(
        quiz_id=quiz_id,
        text=data['text'],
        option_1=data['option_1'],
        option_2=data['option_2'],
        option_3=data['option_3'],
        option_4=data['option_4'],
        correct_option=data['correct_option']
    )

    db.session.add(new_question)
    db.session.commit()

    return jsonify({'message': 'Question added', 'question_id': new_question.id}), 201

@app.route('/quizzes', methods=['GET'])
def get_quizzes():
    """
    Get all quizzes
    ---
    tags:
      - Quizzes
    responses:
      200:
        description: List of all quizzes
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              title:
                type: string
                example: General Knowledge Quiz
              questions:
                type: array
                items:
                  type: string
                  example: What is the capital of France?
    """
    quizzes = Quiz.query.all()
    return jsonify([{'id': q.id, 'title': q.title, 'questions': [question.text for question in q.questions]} for q in quizzes]), 200


#----------------------------------------------------------------------------

@socketio.on('join_game')
def join(data):
    """
    Join a game room
    ---
    operationId: join_game
    message:
      contentType: application/json
      payload:
        type: object
        properties:
          username:
            type: string
          quiz_id:
            type: string
    """
    username = data['username']
    quiz_id = data['quiz_id']
    
    join_room(quiz_id)
    
    if quiz_id not in active_games:
        active_games[quiz_id] = {}

    if username not in active_games[quiz_id]:
        active_games[quiz_id][username] = request.sid
        write_log(f"{username} присоединился к игре {quiz_id}")
            

    emit('players_list_update', {'players': list(active_games[quiz_id].keys())}, room = quiz_id)


@socketio.on('disconnect')
def disconnect():
    for quiz_id, players in active_games.items():
        for username, sid in list(players.items()):
            if sid == request.sid:
                del players[username]
                leave_room(quiz_id)
                write_log(f"{username} покинул игру {quiz_id}")
                emit('players_list_update', {'players': list(players.keys())}, room = quiz_id)
                
                break

@socketio.on('start_game')
def start_game(data):
    try:
        quiz_id = data['quiz_id']
        
        if quiz_id not in active_games:
            emit('error', {'message': 'Game not active'}, room = quiz_id)
            return
            
        questions = get_questions(quiz_id)
        if not questions:
            emit('error', {'message': 'No questions found'}, room=quiz_id)
            return
            
        players = {username: {'score': 0, 'answers': []} 
                  for username in active_games[quiz_id].keys()}

        game_state = {
            'questions': questions,
            'current_question': 0,
            'players': players,
            'is_active': True
        }

        game_states[quiz_id] = game_state

        
        first_question = questions[0]
        question_data = {
            'text': str(first_question.text),
            'options': [
                first_question.option_1,
                first_question.option_2,
                first_question.option_3,
                first_question.option_4
            ],
            'correct_option': first_question.correct_option
        }

        emit('new_question', {'question': question_data}, room = quiz_id)
        write_log(f'Игра {quiz_id} началась!\n')

    except Exception as e:
        emit('error', {'message': f'Start game error: {str(e)}'}, room=quiz_id)
        write_log(f'Ошибка запуска игры {quiz_id}: {str(e)}\n')


@socketio.on('receive_answer')
def handle_receive_answer(data):
    try:
        # 1. Валидация входных данных
        if not isinstance(data, dict):
            emit('error', {'message': 'Invalid data format'}, room=request.sid)
            return

        quiz_id = data.get('quiz_id')
        username = data.get('username')
        player_answer = str(data.get('answer', '')).strip().lower()

        if not all([quiz_id, username, player_answer]):
            emit('error', {'message': 'Missing required fields'}, room=request.sid)
            return

        # 2. Проверка состояния игры
        if quiz_id not in game_states:
            emit('error', {'message': 'Game not found'}, room=quiz_id)
            return

        game_state = game_states[quiz_id]
        
        if not game_state.get('is_active', False):
            emit('error', {'message': 'Game is not active'}, room=quiz_id)
            return

        if username not in game_state['players']:
            emit('error', {'message': 'Player not registered'}, room=quiz_id)
            return

        # 3. Получение текущего вопроса
        current_question_index = game_state['current_question']
        questions = game_state['questions']
        
        if current_question_index >= len(questions):
            emit('error', {'message': 'No more questions'}, room=quiz_id)
            return

        current_question = questions[current_question_index]
        
        # 4. Проверка правильного ответа
        correct_option = str(getattr(current_question, 'correct_option', ''))
        
        # Если correct_option уже содержит только цифру (например "1")
        if correct_option.isdigit():
            correct_answer_attr = f'option_{correct_option}'
        else:
            # Если в формате "option_1"
            correct_answer_attr = correct_option
        
        correct_answer = str(getattr(current_question, correct_answer_attr, '')).lower()
        is_correct = player_answer == correct_answer

        # 5. Обновление счета игрока
        if is_correct:
            game_state['players'][username]['score'] += 1

        # 6. Сохранение ответа
        game_state['players'][username]['answers'].append({
            'question': str(getattr(current_question, 'text', '')),
            'answer': player_answer,
            'is_correct': is_correct
        })

        # 7. Проверка, все ли ответили
        all_answered = all(
            len(player['answers']) > current_question_index 
            for player in game_state['players'].values()
        )
        
        if all_answered:
            game_state['current_question'] += 1
            
            # 8. Отправка следующего вопроса или завершение игры
            if game_state['current_question'] < len(questions):
                next_question = questions[game_state['current_question']]
                emit('next_question', {
                    'question': {
                        'text': str(getattr(next_question, 'text', '')),
                        'options': [
                            str(getattr(next_question, 'option_1', '')),
                            str(getattr(next_question, 'option_2', '')),
                            str(getattr(next_question, 'option_3', '')),
                            str(getattr(next_question, 'option_4', ''))
                        ],
                        'correct_option': str(getattr(next_question, 'correct_option', ''))
                    },
                    'question_number': game_state['current_question'] + 1,
                    'total_questions': len(questions)
                }, room=quiz_id)
            else:
                game_state['is_active'] = False
                emit('game_over', {
                    'message': 'Игра окончена!',
                    'results': game_state['players']
                }, room=quiz_id)
                write_log(f'Игра {quiz_id} завершена. Результаты: {game_state["players"]}')
                
                quiz_id = data['quiz_id']

                if quiz_id in game_states:
                    del game_states[quiz_id]

                    write_log(f"Состояние игры {quiz_id} удалено.")

    except Exception as e:
        emit('error', {'message': f'Error processing answer: {str(e)}'}, room=quiz_id)
        write_log(f'Ошибка в receive_answer: {str(e)}\nДанные: {data}')


if __name__ == '__main__':
    socketio.run(app, debug = True, host = '0.0.0.0', port = 5000)