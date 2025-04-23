import pytest
import json
from datetime import datetime, timedelta
from app import app, mongo

@pytest.fixture(autouse=True)
def clear_db():
    # 在每个测试前清空相关集合
    mongo.db.users.delete_many({})
    mongo.db.health_data.delete_many({})
    yield

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_user_register_and_login(client):
    # 注册新用户
    rv = client.post("/user/register", json={
        "username": "alice",
        "password": "secret",
        "device_id": "dev1"
    })
    assert rv.status_code == 201
    data = rv.get_json()
    assert data["message"] == "Registered successfully"

    # 重复注册失败
    rv = client.post("/user/register", json={
        "username": "alice",
        "password": "secret",
        "device_id": "dev1"
    })
    assert rv.status_code == 400

    # 登录成功
    rv = client.post("/user/login", json={
        "username": "alice",
        "password": "secret"
    })
    assert rv.status_code == 200
    assert rv.get_json()["message"] == "Login successful"

    # 登录失败：密码错误
    rv = client.post("/user/login", json={
        "username": "alice",
        "password": "wrong"
    })
    assert rv.status_code == 401

def test_upload_and_query_health(client):
    # 先注册并绑定 device_id
    client.post("/user/register", json={
        "username": "bob", "password": "pw", "device_id": "D2"
    })

    # 上传两条健康数据
    now = datetime.utcnow()
    for i in range(2):
        rv = client.get("/repo", query_string={
            "terminal": "T", "device": "2",
            "heartrate": str(60+i),
            "spo2": str(95+i),
            "temp": str(36.5+i*0.1)
        })
        assert rv.status_code == 201

    # 查询健康数据
    rv = client.post("/query_health", json={"username": "bob"})
    assert rv.status_code == 200
    arr = rv.get_json()["data"]
    assert isinstance(arr, list) and len(arr) == 2
    assert all("timestamp" in e for e in arr)

def test_manage_update_and_get_profile(client):
    # 用 manage 注册一个用户
    rv = client.post("/manage/register", json={
        "username": "carol",
        "password": "pw2",
        "device_id": "DEV3"
    })
    assert rv.status_code == 200

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