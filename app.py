from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import secrets
# from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.secret_key = secrets.token_hex(16)



from models import Admin, Test, db
db.init_app(app)
with app.app_context():
    db.create_all()
# migrate = Migrate(app, db)

@app.route('/admins/<int:user_id>', methods = ['GET'])
def get_admin(user_id: int):
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


# @app.route('add/<str:username>')


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)