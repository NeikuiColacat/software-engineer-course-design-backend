# 后端 API 文档

## 基础 URL  

http://<服务器IP>:5000

---

## 一、`user` 模块

### 1. 注册新用户  
- URL  
  `POST /user/register`  
- 请求体  
  ```json
  {
    "username": "string",    // 必填，用户名
    "password": "string",    // 必填，密码
    "device_id": "string"    // 必填，设备 ID，与用户绑定
  }

  //成功响应(201)
  {"message": "Registered successfully"}
  //错误相应(400)
  { "error": "Missing parameters" }
  { "error": "User already exists" }
  ```

### 2. 用户登录

- URL  
  `POST /user/login`  
- 请求体  
  ```json
  {
    "username": "string",    // 必填，用户名
    "password": "string",    // 必填，密码
  }

  //成功响应(201)
  { "message": "Login successful" }
  //错误相应(400 , 401)
  { "error": "Missing parameters" }
  { "error": "Invalid credentials" }
  ```


## 二、`health` 模块

### 1. 上传数据 
- URL  
  `GET /repo`  
- 请求体  
  ```json
  {
    "terminal" : (string) — 终端编号 ,
    "device" : (string) — 设备编号 ,
    "heartrate" : (string) — 心率 ,
    "spo2" (string) — 血氧 ,
    "temp" (string) — 体温
  }

  //成功响应(201)
  { "message": "Health data uploaded" }
  //错误相应(400)
  { "error": "Missing parameters" }
  ```

### 2. 查询某个用户所有健康数据 

- URL  
  `POST /query_health`  
- 请求体  
  ```json
  {
    "username": "string",    // 必填，用户名
  }

  //成功响应(201)
  {
    "data": [
        {
        "timestamp": "2025-04-22T08:15:30",
        "spo2": 98,
        "heartRate": 72,
        "temperature": 36.7
        },
        {
        "timestamp": "2025-04-22T08:16:00",
        "spo2": 99,
        "heartRate": 72,
        "temperature": 37.7
        },
        //...
    ]
  }
  //错误相应(400 , 404)
  { "error": "Missing parameters" }
  //错误相应(400 , 404)
  { "error": "User not found" }
  ```


## 二、`manage` 模块

### 1. 更新profile 
- URL  
  `PUT /manage/get_profile`  
  
- 请求体  
  ```json
  {
    "username": "string",   // 必填
  }

  //成功响应(201)
  [
    {
        "username": "alice",
        "device_id": "5117",
        "profile": 
        {
            "height": 170,
            "age": 30,
            "weight": 60
        }
    }
  ]
  //错误相应(400)
  { "error": "Missing username" }
  { "error": "User not found" }
  ```

### 2. 查询所有用户Profile 

- URL  
  `GET /manage/get_all_profile`  

  ```json
  //成功响应(200)
  [
    {
        "username": "alice",
        "device_id": "12351",
        "profile": { ... }
    },
    {
        "username": "bob",
        "device_id": "1361",
        "profile": { ... }
    }
  ]
  ```