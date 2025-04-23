from flask import Blueprint, request, jsonify
from models.db import mongo
from bson import ObjectId
import bcrypt

bp = Blueprint("user", __name__)

@bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    device_id = data.get("device_id")
    role = data.get("role")

    if not all([username, password, device_id]):
        return jsonify({"error": "Missing parameters"}), 400

    if mongo.db.users.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    result = mongo.db.users.insert_one({
        "username": username,
        "password": hashed,
        "device_id": device_id,
        "role" : role,
        "profile": {},
    })

    return jsonify({
        "message": "Registered successfully",
    }), 201

@bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not all([username, password]):
        return jsonify({"error": "Missing parameters"}), 400

    user = mongo.db.users.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return jsonify({
            "message": "Login successful",
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401

