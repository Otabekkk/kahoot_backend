from flask import Blueprint, jsonify, request
from models import Admin
from flask_jwt_extended import create_access_token, create_refresh_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.post('/register')
def register():
    data = request.get_json()

    user = Admin.getAdminByUsername(data.get('username'))

    if user is not None:
        return jsonify({'Error': 'User already exists!'}), 403
    
    newAdmin = Admin(username = data.get('username'))
    newAdmin.securePassword(data.get('password'))
    
    newAdmin.save()

    return jsonify({'Success': 'User created!'}), 201

@auth_bp.post('/login')
def login():
    data = request.get_json()

    user = Admin.getAdminByUsername(username = data.get('username'))

    if user and (user.checkPassword(password = data.get('password'))):
        access_token = create_access_token(identity = user.username)
        refresh_token = create_refresh_token(identity = user.username)

        return jsonify({
            'Message': 'Logged in',
            'Tokens': {
                'access': access_token,
                'refresh': refresh_token
            }
        })
    
    return jsonify({'Error': 'Invalid username or password!'}), 400
