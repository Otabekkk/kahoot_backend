from flask import Blueprint, jsonify, request
from models import Admin

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
