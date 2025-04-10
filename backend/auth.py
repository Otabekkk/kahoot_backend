from flask import Blueprint, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.post('/register')
def register():
    return jsonify({'message': 'User created!'})