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
    "device_id": "string",    // 必填，设备 ID，与用户绑定
    "role": "string" - "manager" or "user"    // 必填，设备 ID，与用户绑定
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
        "role" : "manager or user",
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

### 3. 更新用户的Profile
- URL  
  `PUT /manage/update_profile`  

  ```json
  //请求json body
  {
    "username": "carol",     // 必填，目标用户名
    "height": 165,           // 选填，身高（厘米）
    "age": 28,               // 选填，年龄（岁）
    "weight": 55             // 选填，体重（公斤）
  }
  //成功响应(200)
  {
    "message": "Profile updated successfully"
  }
  // 错误 (400 404 500)
  { "error": "Missing parameters" }
  { "error": "No valid fields to update" }
  { "error": "User not found" }
  { "error": "详细错误信息" }

  ```

## LLM 接口

URL : `POST /hugging_face/ai_advice`
```json
//Body
{
  "username": "12"  // 必填，要获取建议的用户名
}


//成功返回(200)
{
    "advice": "一个markdown语法的字符串",
}

//例子如下
"根据您的健康数据，以下为简要分析及建议：\n\n### **数据趋势分析**\n1. **心率**：从60 bpm逐渐上升至78 bpm（正常范围60-100 bpm），呈现波动上升趋势，可能与轻度活动（如步行）相关。\n2. **血氧**：95%-99%（正常≥95%），波动但总体良好，无缺氧风险。\n3. **体温**：36.0°C升至36.9°C（正常约36.1-37.2°C），轻微升高但仍属正常，可能与活动或环境温度有关。\n\n### **建议**\n1. **心率波动**：  \n   - 若伴随活动（如运动），属正常反应；若无明显诱因，建议观察是否与压力、咖啡因摄入或脱水有关。  \n   - 静息时心率持续＞80 bpm或出现心悸，需咨询医生。\n\n2. **体温管理**：  \n   - 36.9°C接近正常上限，确保适当补水，避免过热环境。若持续升高或出现不适（如乏力、头晕），需排查感染或炎症。\n\n3. **日常注意**：  \n   - 保持规律作息，避免突然剧烈运动。  \n   - 监测数据变化，若异常持续或伴随症状（如胸痛、呼吸困难），及时就医。\n\n**总结**：当前数据基本正常，注意观察潜在诱因，保持健康生活习惯即可。"

// 错误(404 400)
{
  "error": "User not found"
}
{
  "error": "No health data found"
}
{
  "error": "Missing username"
}
```