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
teststr = "根据您的健康数据，以下为简要分析及建议：\n\n### **数据趋势分析**\n1. **心率**：从60 bpm逐渐上升至78 bpm（正常范围60-100 bpm），呈现波动上升趋势，可能与轻度活动（如步行）相关。\n2. **血氧**：95%-99%（正常≥95%），波动但总体良好，无缺氧风险。\n3. **体温**：36.0°C升至36.9°C（正常约36.1-37.2°C），轻微升高但仍属正常，可能与活动或环境温度有关。\n\n### **建议**\n1. **心率波动**：  \n   - 若伴随活动（如运动），属正常反应；若无明显诱因，建议观察是否与压力、咖啡因摄入或脱水有关。  \n   - 静息时心率持续＞80 bpm或出现心悸，需咨询医生。\n\n2. **体温管理**：  \n   - 36.9°C接近正常上限，确保适当补水，避免过热环境。若持续升高或出现不适（如乏力、头晕），需排查感染或炎症。\n\n3. **日常注意**：  \n   - 保持规律作息，避免突然剧烈运动。  \n   - 监测数据变化，若异常持续或伴随症状（如胸痛、呼吸困难），及时就医。\n\n**总结**：当前数据基本正常，注意观察潜在诱因，保持健康生活习惯即可。"

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
    # completion = client.chat.completions.create(
    #     model="deepseek-ai/DeepSeek-V3-0324",
    #     messages=[{"role": "user", "content": prompt}],
    #     max_tokens=512,
    # )
    # advice = completion.choices[0].message.content

    return jsonify({"advice": teststr}), 200
