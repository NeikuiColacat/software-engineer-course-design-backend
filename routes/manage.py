from flask import Blueprint, request, jsonify
from models.db import mongo
from bson import ObjectId
import bcrypt

bp = Blueprint("manage", __name__)

@bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data["username"]
    password = data["password"]
    device_id = data["device_id"]

    if mongo.db.users.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    mongo.db.users.insert_one({
        "username": username,
        "password": hashed,
        "device_id": device_id,
        "profile": {}  # 空用户信息
    })
    return jsonify({"message": "Registered successfully"})


@bp.route("/update_profile", methods=["PUT"])
def update_profile():
    try:
        # 从请求体中获取更新的数据
        data = request.json or {}
        username = data.get("username")  # 用户名
        height = data.get("height")  # 身高
        age = data.get("age")        # 年龄
        weight = data.get("weight")  # 体重

        # 验证用户是否存在
        user = mongo.db.users.find_one({"username": username})
        if not user:
            return jsonify({"error": "User not found"}), 404

        # 更新用户的 profile 信息
        update_data = {}
        update_data["profile.height"] = height
        update_data["profile.age"] = age
        update_data["profile.weight"] = weight

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        mongo.db.users.update_one({"username": username}, {"$set": update_data})

        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/get_profile", methods=["GET"])
def get_profile():
    data = request.json or {}
    username = data.get("username")
    if not username:
        return jsonify({"error": "Missing username"}), 400

    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    result = [{
        "username": user.get("username"),
        "device_id": user.get("device_id"),
        "profile": user.get("profile", {})
    }]
    return jsonify(result), 200

@bp.route("/get_all_profile", methods=["GET"])
def get_all_profile():
    cursor = mongo.db.users.find()
    result = []
    for u in cursor:
        result.append({
            "username": u.get("username"),
            "device_id": u.get("device_id"),
            "profile": u.get("profile", {})
        })
    return jsonify(result), 200
