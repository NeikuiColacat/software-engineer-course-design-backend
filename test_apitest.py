import pytest
import os
from datetime import datetime , timedelta
from app import app
from models.db import mongo   # 从 db.py 直接 import mongo


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_user_login_success(client):
    # 先注册一个用户
    rv = client.post("/user/register", json={
        "username": "testuser",
        "password": "mypassword",
        "role":     "user",
        "device_id":"DEV100"
    })
    assert rv.status_code == 201

    # 登录这个用户
    rv = client.post("/user/login", json={
        "username": "testuser",
        "password": "mypassword"
    })
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["message"] == "Login successful"

@pytest.mark.parametrize("payload,code,err", [
    ({},                         400, "Missing parameters"),      # 空参数
    ({"username":"noexist"},     400, "Missing parameters"),      # 缺少 password
    ({"username":"noexist","password":"pw"}, 401, "Invalid credentials"),  # 用户不存在
    ({"username":"testuser","password":"wrong"}, 401, "Invalid credentials") # 密码错误
])
def test_user_login_failure(client, payload, code, err):
    # payload 中的字段组合应该返回对应 code 和 error message
    rv = client.post("/user/login", json=payload)
    assert rv.status_code == code
    data = rv.get_json()
    assert data.get("error") == err

def test_manage_update_and_get_profile(client):
    # 用 manage 注册一个用户
    rv = client.post("/user/register", json={
        "username": "carol",
        "password": "pw2",
        "device_id": "DEV3",
        "role" : "user"
    })
    assert rv.status_code == 201 

    # 更新 profile
    rv = client.put("/manage/update_profile", json={
        "username": "carol",
        "height": 165, "age": 28, "weight": 55
    })
    assert rv.status_code == 200
    assert rv.get_json()["message"] == "Profile updated successfully"

    # 查询单用户 profile
    rv = client.get("/manage/get_profile", json={"username": "carol"})
    assert rv.status_code == 200
    arr = rv.get_json()
    assert isinstance(arr, list) and arr[0]["profile"]["age"] == 28

    # 查询所有用户 profiles
    rv = client.get("/manage/get_all_profile")
    assert rv.status_code == 200
    all_profiles = rv.get_json()
    assert any(u["username"] == "carol" for u in all_profiles)

def test_insert_health_data_for_user():
    """
    为指定用户名的设备插入 count 条健康数据，timestamp 间隔 1 分钟。
    """
    username = "12"
    cnt = 10

    user = mongo.db.users.find_one({"username": username})
    if not user:
        raise ValueError(f"User '{username}' not found in database")
    device_id = user["device_id"]
    base_time = datetime.utcnow()
    print(device_id)

    docs = [
        {
            "device_id": '12',
            "timestamp": base_time + timedelta(minutes=i),
            "spo2": 95 + (i % 5),
            "heartRate": 60 + i * 2,
            "temperature": 36.0 + i * 0.1
        }
        for i in range(cnt)
    ]
    mongo.db.health_data.insert_many(docs)
    assert(True)

def test_user_bind_device():
    """
    为指定用户名的设备插入 count 条健康数据，timestamp 间隔 1 分钟。
    """
    username = "12"
    cnt = 10

    user = mongo.db.users.find_one({"username": username})
    if not user:
        raise ValueError(f"User '{username}' not found in database")

    device_id = user["device_id"]
    print(device_id)
    assert(device_id == '12')

def test_get_health_data(client):

    rv = client.post("/query_health", json={"username": "12"})
    data = rv.get_json()
    print(data)


# 确保 Hugging Face Token 已设置，否则跳过测试
@pytest.mark.skipif(not os.environ.get("HUGGINGFACE_TOKEN"),
                    reason="HUGGINGFACE_TOKEN not set")
def test_ai_advice(client):

    # 调用 /ai_advice 接口
    rv = client.post("/ai_advice", json={"username": "12"})
    data = rv.get_json()
    assert(data != None)
    print(data)