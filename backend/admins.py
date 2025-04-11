from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Admin
from schemas import AdminSchema

admin_bp = Blueprint(
    'users',
    __name__
)

@admin_bp.get('/all')
@jwt_required()
def getAdmins():
    page = request.args.get('page', default = 1, type = int)
    per_page = request.args.get('per_page', default = 3, type = int)

    admins = Admin.query.paginate(
        page = page,
        per_page = per_page,

    )

    result = AdminSchema().dump(admins, many = True)
    
    return jsonify({'Admins': result}), 200