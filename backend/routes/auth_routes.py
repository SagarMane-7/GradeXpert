from flask import Blueprint, request, jsonify
from models import db, User, Branch
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        # Create JWT Token
        # FIX: 'sub' (identity) MUST be a string. Put other data in additional_claims.
        access_token = create_access_token(
            identity=str(user.id), 
            additional_claims={
                'username': user.username,
                'role': user.role,
                'branch_id': user.branch_id
            }
        )
        return jsonify(access_token=access_token, role=user.role), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Get Branch name if present
    branch_name = "All Branches"
    if user.branch_id:
        b = db.session.get(Branch, user.branch_id)
        if b: branch_name = b.name
        
    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role.title(),
        "branch": branch_name,
        "created_at": user.created_at.strftime('%Y-%m-%d %H:%M')
    }), 200
