from flask import Blueprint, request, jsonify
from models.db import mongo
from bson import ObjectId
from datetime import datetime

bp = Blueprint("health", __name__)

@bp.route("/repo", methods=["GET"])
def upload_health_from_url():
    try:
        # 从 URL 参数中获取数据
        terminal = request.args.get("terminal")
        device = request.args.get("device")
        heartrate = request.args.get("heartrate")
        spo2 = request.args.get("spo2")
        temp = request.args.get("temp")

        # 验证参数是否完整
        if not all([terminal, device, heartrate, spo2, temp]):
            return jsonify({"error": "Missing required parameters"}), 400

        # 合并温度整数和小数部分

        # 构建记录
        record = {
            "device_id": terminal + device,
            "timestamp": datetime.utcnow(),  # 使用当前时间作为时间戳
            "spo2": int(spo2),
            "heartRate": int(heartrate),
            "temperature": float(temp)
        }

        # 插入到 MongoDB
        mongo.db.health_data.insert_one(record)

        return jsonify({"message": "Health data uploaded"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/query_health", methods=["POST"])
def query_health():
    data = request.json or {}
    username = data.get("username")
    if not all([username]):
        return jsonify({"error": "Missing parameters"}), 400

    # 查找用户
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 查询 health_data 并按时间升序排列
    cursor = mongo.db.health_data.find(
        {
            "device_id":user.get("device_id")
        }
    ).sort("timestamp", 1)

    # 构建返回结果
    result = []
    for doc in cursor:
        result.append({
            "timestamp": doc["timestamp"].isoformat(),
            "spo2": doc.get("spo2"),
            "heartRate": doc.get("heartRate"),
            "temperature": doc.get("temperature")
        })

    return jsonify({"data": result}), 200