from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    
    questions = db.relationship('Question', backref = 'quiz', lazy = True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
    option_4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    score = db.Column(db.Integer, default = 0)