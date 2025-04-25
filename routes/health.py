from flask import Blueprint, request, jsonify
from models.db import mongo
from bson import ObjectId
from datetime import datetime , timezone , timedelta
import pytz

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
            "timestamp": datetime.now(),  # 使用当前时间作为时间戳
            "spo2": int(spo2),
            "heartRate": int(heartrate),
            "temperature": float(temp)
        }

        # 插入到 MongoDB
        mongo.db.health_data.insert_one(record)

        return jsonify({"message": "Health data uploaded"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def convert_to_east_eight(utc_time_str):
    """
    将 UTC 时间字符串转换为东八区时间字符串。

    :param utc_time_str: ISO 8601 格式的 UTC 时间字符串 (如 "2025-04-24T08:47:22+00:00")
    :return: ISO 8601 格式的东八区时间字符串 (如 "2025-04-24T16:47:22+08:00")
    """
    # 将 ISO 8601 格式的时间字符串解析为 datetime 对象
    utc_time = datetime.fromisoformat(utc_time_str)

    # 定义东八区的时间偏移
    east_eight_offset = timedelta(hours=8)

    # 将 UTC 时间加上东八区的时间偏移
    east_eight_time = utc_time + east_eight_offset

    # 返回东八区时间的 ISO 8601 字符串，并附加 "+08:00" 时区信息
    return east_eight_time.isoformat() 

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
        cur_time = (doc["timestamp"].isoformat())
        result.append({
            "timestamp": cur_time, 
            "spo2": doc.get("spo2"),
            "heartRate": doc.get("heartRate"),
            "temperature": doc.get("temperature")
        })

    return jsonify({"data": result}), 200