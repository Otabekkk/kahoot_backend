from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from models import db, Quiz, Question
# from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)


# with app.app_context():
#     db.create_all()

# Migrate(app, db)

CORS(app)
socketio = SocketIO(app, cors_allowed_origins = '*')

@app.route('/quizzes', methods = ['POST'])
def create_quiz():
    data = request.get_json()

    new_quiz = Quiz(title = data['title'])

    db.session.add(new_quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz created', 'quiz_id': new_quiz.id}), 201

@app.route('/quizzes/<int:quiz_id>/quiestions', methods = ['POST'])
def add_question(quiz_id: int):
    data = request.get_json()
    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    new_question = Question(
        quiz_id = quiz_id,
        text = data['text'],
        option_1 = data['option_1'],
        option_2 = data['option_2'],
        option_3 = data['option_3'],
        option_4 = data['option_4'],

        correct_option = data['correct_option']
    )

    db.session.add(new_question)
    db.session.commit()

    return jsonify({'message': 'Question added', 'question_id': new_question.id}), 201


@app.route('/quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.all()
    return jsonify([{'id': q.id, 'title': q.title, 'questions': [question.text for question in q.questions]} for q in quizzes]), 200


if __name__ == '__main__':
    socketio.run(app, debug = True)
