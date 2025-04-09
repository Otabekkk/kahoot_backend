# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from flask_socketio import SocketIO, join_room, emit, leave_room
# from models import db, Quiz, Question
# from flask_migrate import Migrate
# import datetime


# app = Flask(__name__)
# app.config.from_object('config')

# db.init_app(app)


# def write_log(message):
#     with open('logs.txt', 'a', encoding='utf-8') as f:
#         f.write(f"{datetime.datetime.now()} - {message}\n")

# def get_questions(quiz_id: str):
#     questions = Quiz.query.filter_by(quiz_id = quiz_id).first().questions
#     return questions


# with app.app_context():
#     db.create_all()

# Migrate(app, db)

# CORS(app)
# socketio = SocketIO(app, cors_allowed_origins = '*', async_mode="eventlet")

# active_games = {}
# game_states = {}

# @app.route('/quizzes', methods = ['POST'])
# def create_quiz():
#     data = request.get_json()

#     new_quiz = Quiz(title = data['title'], quiz_id = data['quiz_id'])

#     db.session.add(new_quiz)
#     db.session.commit()
#     return jsonify({'message': 'Quiz created', 'quiz_id': new_quiz.id}), 201

# @app.route('/quizzes/<int:quiz_id>/questions', methods = ['POST'])
# def add_question(quiz_id: int):
#     data = request.get_json()
#     quiz = Quiz.query.get(quiz_id)

#     if not quiz:
#         return jsonify({'error': 'Quiz not found'}), 404
    
#     new_question = Question(
#         quiz_id = quiz_id,
#         text = data['text'],
#         option_1 = data['option_1'],
#         option_2 = data['option_2'],
#         option_3 = data['option_3'],
#         option_4 = data['option_4'],

#         correct_option = data['correct_option']
#     )

#     db.session.add(new_question)
#     db.session.commit()

#     return jsonify({'message': 'Question added', 'question_id': new_question.id}), 201


# @app.route('/quizzes', methods=['GET'])
# def get_quizzes():
#     quizzes = Quiz.query.all()
#     return jsonify([{'id': q.id, 'title': q.title, 'questions': [question.text for question in q.questions]} for q in quizzes]), 200

# #----------------------------------------------------------------------------
# @socketio.on('join_game')
# def join(data):
#     username = data['username']
#     quiz_id = data['quiz_id']
    
#     join_room(quiz_id)
    
#     if quiz_id not in active_games:
#         active_games[quiz_id] = {}

#     if username not in active_games[quiz_id]:
#         active_games[quiz_id][username] = request.sid
#         write_log(f"{username} присоединился к игре {quiz_id}")
            

#     emit('players_list_update', {'players': list(active_games[quiz_id].keys())}, room = quiz_id)


# @socketio.on('disconnect')
# def disconnect():
#     for quiz_id, players in active_games.items():
#         for username, sid in list(players.items()):
#             if sid == request.sid:
#                 del players[username]
#                 leave_room(quiz_id)
#                 write_log(f"{username} покинул игру {quiz_id}")
#                 emit('players_list_update', {'players': list(players.keys())}, room = quiz_id)
                
#                 break

# @socketio.on('start_game')
# def start_game(data):
#     try:
#         quiz_id = data['quiz_id']
        
#         if quiz_id not in active_games:
#             emit('error', {'message': 'Game not active'}, room = quiz_id)
#             return
            
#         questions = get_questions(quiz_id)
#         if not questions:
#             emit('error', {'message': 'No questions found'}, room=quiz_id)
#             return
            
#         players = {username: {'score': 0, 'answers': []} 
#                   for username in active_games[quiz_id].keys()}

#         game_state = {
#             'questions': questions,
#             'current_question': 0,
#             'players': players,
#             'is_active': True
#         }

#         game_states[quiz_id] = game_state

        
#         first_question = questions[0]
#         question_data = {
#             'text': str(first_question.text),
#             'options': [
#                 first_question.option_1,
#                 first_question.option_2,
#                 first_question.option_3,
#                 first_question.option_4
#             ],
#             'correct_option': first_question.correct_option
#         }

#         emit('new_question', {'question': question_data}, room = quiz_id)
#         write_log(f'Игра {quiz_id} началась!\n')

#     except Exception as e:
#         emit('error', {'message': f'Start game error: {str(e)}'}, room=quiz_id)
#         write_log(f'Ошибка запуска игры {quiz_id}: {str(e)}\n')

# # @socketio.on('start_game')
# # def start_game(data):
# #     quiz_id = data['quiz_id']
    

# #     # if quiz_id in active_games:
# #     questions = get_questions(quiz_id)
# #     players = {username: {'score': 0, 'answers': []} for username in active_games[quiz_id].keys()}

# #     game_state = {
# #         'questions': questions,
# #         'current_question': 0,
# #         'players': players,
# #         'is_active': True
# #     }

# #     game_states[quiz_id] = game_state

# #     emit('new_question', {'question': game_state['questions'][game_state['current_question']]}, room = quiz_id)
# #     write_log(f'Игра {quiz_id} началась!\n')

# # @socketio.on('receive_answer')
# # def handle_receive_answer(data):
# #     try:
# #         quiz_id = data['quiz_id']
# #         username = data['username']
# #         player_answer = data['answer'].strip().lower()

# #         if quiz_id not in game_states:
# #             emit('error', {'message': 'Game not found'}, room=quiz_id)
# #             return

# #         game_state = game_states[quiz_id]
        
# #         if not game_state['is_active']:
# #             emit('error', {'message': 'Game is not active'}, room=quiz_id)
# #             return

# #         current_question = game_state['questions'][game_state['current_question']]

# #         correct_option = current_question.correct_option
# #         correct_answer = getattr(current_question, f'option_{correct_option[:-1]}').lower()
        
# #         if player_answer == correct_answer:
# #             game_state['players'][username]['score'] += 1


# #         game_state['players'][username]['answers'].append({
# #             'question': current_question.text,
# #             'answer': player_answer,
# #             'is_correct': player_answer == correct_answer
# #         })

# #         game_state['current_question'] += 1

# #         if game_state['current_question'] < len(game_state['questions']):
# #             next_question = game_state['questions'][game_state['current_question']]
# #             emit('next_question', {
# #                 'question': {
# #                     'text': next_question.text,
# #                     'options': [
# #                         next_question.option_1,
# #                         next_question.option_2,
# #                         next_question.option_3,
# #                         next_question.option_4
# #                     ],
# #                     'correct_option': next_question.correct_option
# #                 }
# #             }, room = quiz_id)
# #         else:
# #             game_state['is_active'] = False
# #             emit('game_over', {
# #                 'message': 'Игра окончена!',
# #                 'results': game_state['players']
# #             }, room=quiz_id)
# #             write_log(f'Игра {quiz_id} завершена. Результаты: {game_state["players"]}')

# #     except Exception as e:
# #         emit('error', {'message': f'Error processing answer: {str(e)}'}, room=quiz_id)
# #         write_log(f'Ошибка в receive_answer: {str(e)}')

# # @socketio.on('receive_answer')
# # def handle_receive_answer(data):
# #     try:
# #         quiz_id = data['quiz_id']
# #         username = data['username']
# #         player_answer = data['answer'].strip().lower()

# #         if quiz_id not in game_states:
# #             emit('error', {'message': 'Game not found'}, room=quiz_id)
# #             return

# #         game_state = game_states[quiz_id]
        
# #         if not game_state['is_active']:
# #             emit('error', {'message': 'Game is not active'}, room=quiz_id)
# #             return

# #         current_question_index = game_state['current_question']
# #         current_question = game_state['questions'][current_question_index]

# #         correct_option = current_question.correct_option
# #         correct_answer = getattr(current_question, f'option_{correct_option[0]}').lower()
# #         is_correct = player_answer == correct_answer
        
# #         if is_correct:
# #             game_state['players'][username]['score'] += 1

# #         game_state['players'][username]['answers'].append({
# #             'question': current_question.text,
# #             'answer': player_answer,
# #             'is_correct': is_correct
# #         })

        
# #         all_answered = all(len(player['answers']) > current_question_index 
# #                           for player in game_state['players'].values())
        
# #         if all_answered:
            
# #             game_state['current_question'] += 1

# #             if game_state['current_question'] < len(game_state['questions']):
# #                 next_question = game_state['questions'][game_state['current_question']]
# #                 emit('next_question', {
# #                     'question': {
# #                         'text': next_question.text,
# #                         'options': [
# #                             next_question.option_1,
# #                             next_question.option_2,
# #                             next_question.option_3,
# #                             next_question.option_4
# #                         ],
# #                         'correct_option': next_question.correct_option
# #                     },
# #                     'question_number': game_state['current_question'] + 1,
# #                     'total_questions': len(game_state['questions'])
# #                 }, room=quiz_id)
# #             else:
# #                 game_state['is_active'] = False
# #                 emit('game_over', {
# #                     'message': 'Игра окончена!',
# #                     'results': game_state['players']
# #                 }, room=quiz_id)
# #                 write_log(f'Игра {quiz_id} завершена. Результаты: {game_state["players"]}')

# #     except Exception as e:
# #         emit('error', {'message': f'Error processing answer: {str(e)}'}, room = quiz_id)
# #         write_log(f'Ошибка в receive_answer: {str(e)}')

# @socketio.on('receive_answer')
# def handle_receive_answer(data):
#     try:
#         # 1. Валидация входных данных
#         if not isinstance(data, dict):
#             emit('error', {'message': 'Invalid data format'}, room=request.sid)
#             return

#         quiz_id = data.get('quiz_id')
#         username = data.get('username')
#         player_answer = str(data.get('answer', '')).strip().lower()

#         if not all([quiz_id, username, player_answer]):
#             emit('error', {'message': 'Missing required fields'}, room=request.sid)
#             return

#         # 2. Проверка состояния игры
#         if quiz_id not in game_states:
#             emit('error', {'message': 'Game not found'}, room=quiz_id)
#             return

#         game_state = game_states[quiz_id]
        
#         if not game_state.get('is_active', False):
#             emit('error', {'message': 'Game is not active'}, room=quiz_id)
#             return

#         if username not in game_state['players']:
#             emit('error', {'message': 'Player not registered'}, room=quiz_id)
#             return

#         # 3. Получение текущего вопроса
#         current_question_index = game_state['current_question']
#         questions = game_state['questions']
        
#         if current_question_index >= len(questions):
#             emit('error', {'message': 'No more questions'}, room=quiz_id)
#             return

#         current_question = questions[current_question_index]
        
#         # 4. Проверка правильного ответа
#         correct_option = str(getattr(current_question, 'correct_option', ''))
        
#         # Если correct_option уже содержит только цифру (например "1")
#         if correct_option.isdigit():
#             correct_answer_attr = f'option_{correct_option}'
#         else:
#             # Если в формате "option_1"
#             correct_answer_attr = correct_option
        
#         correct_answer = str(getattr(current_question, correct_answer_attr, '')).lower()
#         is_correct = player_answer == correct_answer

#         # 5. Обновление счета игрока
#         if is_correct:
#             game_state['players'][username]['score'] += 1

#         # 6. Сохранение ответа
#         game_state['players'][username]['answers'].append({
#             'question': str(getattr(current_question, 'text', '')),
#             'answer': player_answer,
#             'is_correct': is_correct
#         })

#         # 7. Проверка, все ли ответили
#         all_answered = all(
#             len(player['answers']) > current_question_index 
#             for player in game_state['players'].values()
#         )
        
#         if all_answered:
#             game_state['current_question'] += 1
            
#             # 8. Отправка следующего вопроса или завершение игры
#             if game_state['current_question'] < len(questions):
#                 next_question = questions[game_state['current_question']]
#                 emit('next_question', {
#                     'question': {
#                         'text': str(getattr(next_question, 'text', '')),
#                         'options': [
#                             str(getattr(next_question, 'option_1', '')),
#                             str(getattr(next_question, 'option_2', '')),
#                             str(getattr(next_question, 'option_3', '')),
#                             str(getattr(next_question, 'option_4', ''))
#                         ],
#                         'correct_option': str(getattr(next_question, 'correct_option', ''))
#                     },
#                     'question_number': game_state['current_question'] + 1,
#                     'total_questions': len(questions)
#                 }, room=quiz_id)
#             else:
#                 game_state['is_active'] = False
#                 emit('game_over', {
#                     'message': 'Игра окончена!',
#                     'results': game_state['players']
#                 }, room=quiz_id)
#                 write_log(f'Игра {quiz_id} завершена. Результаты: {game_state["players"]}')
                
#                 quiz_id = data['quiz_id']

#                 if quiz_id in game_states:
#                     del game_states[quiz_id]

#                     write_log(f"Состояние игры {quiz_id} удалено.")

#     except Exception as e:
#         emit('error', {'message': f'Error processing answer: {str(e)}'}, room=quiz_id)
#         write_log(f'Ошибка в receive_answer: {str(e)}\nДанные: {data}')

# # @socketio.on('recieve_answer')
# # def receive_answer(data):
# #     quiz_id = data['quiz_id']
# #     username = data['username']
# #     player_answer = data['answer']
# #     questions = get_questions(quiz_id)

# #     game_state = game_states[quiz_id]

# #     if game_state and game_state['is_active']:
# #         correct_answer = game_state['questions'][game_state['current_question']].text.lower()

# #         if player_answer.lower() == correct_answer:
# #             game_state['players'][username]['score'] += 1
        

# #         game_state['players'][username]['answers'].append(player_answer)

# #         game_state['current_question'] += 1

# #         if game_state['current_question'] < len(game_state['questions']):
# #             next_question = questions[game_state['current_question']]

# #             next_question_data = {
# #                 'text': next_question.text,
# #                 'options': [
# #                     next_question.option_1,
# #                     next_question.option_2,
# #                     next_question.option_3,
# #                     next_question.option_4
# #                 ],
# #                 'correct_option': next_question.correct_option
# #         }
            
# #             emit('next_question', {'question': next_question_data}, room = quiz_id)
        
# #         else:
# #             game_state['is_active'] = False
# #             emit('game_over', {'message': 'Игра окончена!'}, room = quiz_id)
# #             write_log(f'Игра: {quiz_id} завершена!\n')


# # @socketio.on('game_over')
# # def game_over(data):
# #     quiz_id = data['quiz_id']

# #     game_state = game_states.get(quiz_id)

# #     if game_state:
# #         emit('final_results', {'scores': game_state['players']}, room = quiz_id)
# #         write_log(f"Игра {quiz_id} завершена! Результаты отправлены.")
        

# # @socketio.on('clear_game')
# # def clear_game(data):
# #     quiz_id = data['quiz_id']

# #     if quiz_id in game_states:
# #         del game_states[quiz_id]

# #         write_log(f"Состояние игры {quiz_id} удалено.")


# if __name__ == '__main__':
#     socketio.run(app, debug = True, host = '0.0.0.0', port = 5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, emit, leave_room
from models import db, Quiz, Question
from flask_migrate import Migrate
import datetime
from flasgger import Swagger

app = Flask(__name__)
app.config.from_object('config')

# Swagger configuration
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

def write_log(message):
    with open('logs.txt', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")

def get_questions(quiz_id: str):
    questions = Quiz.query.filter_by(quiz_id=quiz_id).first().questions
    return questions

with app.app_context():
    db.create_all()

Migrate(app, db)

CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode="eventlet")

active_games = {}
game_states = {}

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

# SocketIO events documentation (not part of Swagger but included for completeness)
"""
SocketIO Events Documentation:

1. join_game
- Event: 'join_game'
- Description: Join a game room
- Data:
  - username: string - Player's username
  - quiz_id: string - ID of the quiz/game to join
- Emits:
  - 'players_list_update' to room - Updated list of players

2. disconnect
- Event: 'disconnect'
- Description: Handle player disconnection
- Automatically emitted on socket disconnect
- Emits:
  - 'players_list_update' to room - Updated list of players

3. start_game
- Event: 'start_game'
- Description: Start the game
- Data:
  - quiz_id: string - ID of the quiz/game to start
- Emits:
  - 'new_question' to room - First question of the quiz
  - 'error' if game cannot be started

4. receive_answer
- Event: 'receive_answer'
- Description: Handle player's answer
- Data:
  - quiz_id: string - ID of the quiz/game
  - username: string - Player's username
  - answer: string - Player's answer
- Emits:
  - 'next_question' to room - Next question if available
  - 'game_over' to room - Final results when game ends
  - 'error' if any issues occur
"""

# ... (rest of your SocketIO event handlers remain unchanged)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)