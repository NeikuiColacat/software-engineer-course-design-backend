from flask import Blueprint, request, jsonify
from models.db import mongo
from huggingface_hub import InferenceClient
import os

bp = Blueprint("hugging_face", __name__)
# 从环境变量读取 Hugging Face Token
hf_token = os.environ.get("HUGGINGFACE_TOKEN")
if not hf_token:
    raise RuntimeError("环境变量 HUGGINGFACE_TOKEN 未设置")

# 初始化 HF InferenceClient，硬编码示例 token 和 provider
client = InferenceClient(
    provider="sambanova",
    api_key=hf_token,
)

@bp.route("/ai_advice", methods=["POST"])
def ai_advice():
    data = request.json or {}
    username = data.get("username")
    if not username:
        return jsonify({"error": "Missing username"}), 400

    # 查找用户
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404
    device_id = user.get("device_id")

    # 拉取用户所有健康记录，按时间升序
    records = list(
        mongo.db.health_data
        .find({"device_id": device_id})
        .sort("timestamp", 1)
    )
    if not records:
        return jsonify({"error": "No health data found"}), 404

    # 构造 prompt
    prompt_lines = ["请根据以下健康数据给出简短建议："]
    for r in records:
        prompt_lines.append(
            f"时间：{r['timestamp'].isoformat()}，"
            f"心率：{r['heartRate']} bpm，"
            f"血氧：{r['spo2']}%，"
            f"体温：{r['temperature']}°C"
        )
    prompt = "\n".join(prompt_lines)
    # 调用 DeepSeek-V3-0324 聊天完成接口
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3-0324",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )
    advice = completion.choices[0].message.content

    return jsonify({"advice": advice}), 200