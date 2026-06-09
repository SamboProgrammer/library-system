from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models.models import User

auth_bp = Blueprint("auth", __name__)

# Register a new user account
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    # Defensive input verification
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password are required fields"}), 400

    # Ensure uniqueness constraints
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username is already taken"}), 409

    user = User(
        username=data["username"]
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User account created successfully"}), 201

# Login and retrieve JWT Access Token
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    # Input verification
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(
        username=data["username"]
    ).first()

    if not user:
        return jsonify({"error": "User account not found"}), 401

    if not user.verify_password(data["password"]):
        return jsonify({"error": "Invalid password credentials"}), 401

    # Generate the access token using the username as identity
    token = create_access_token(
        identity=user.username
    )

    return jsonify({"token": token}), 200
