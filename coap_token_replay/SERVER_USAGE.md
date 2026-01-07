# CoAP Server - 使用说明

## ✅ 已修复的问题

重写后的 `server.py` 修复了以下问题：

1. ✅ **导入错误** - 正确导入 `aiocoap.resource`
2. ✅ **Resource 使用错误** - 创建了正确的 Resource 子类
3. ✅ **代码结构** - 使用面向对象的资源处理方式
4. ✅ **错误处理** - 添加了 KeyboardInterrupt 处理

## 📁 文件结构

```
coap_token_replay/
├── server.py              ← 重写的服务器（已修复）
├── client.py              ← 客户端（模拟易受攻击的客户端）
├── attacker.py            ← 攻击脚本
├── test_server.py         ← 服务器测试脚本（新增）
└── SERVER_USAGE.md        ← 本文件
```

## 🚀 快速开始

### 1. 启动服务器

```bash
# Windows
.\.venv\Scripts\python.exe coap_token_replay\server.py

# Linux/Mac
python coap_token_replay/server.py
```

你应该看到：

```
============================================================
CoAP Token Replay Attack - Demo Server
============================================================
服务器地址: coap://127.0.0.1:5683
可用资源:
  - coap://127.0.0.1:5683/          (欢迎信息)
  - coap://127.0.0.1:5683/toggle    (状态切换)
  - coap://127.0.0.1:5683/status    (服务器状态)
  - coap://127.0.0.1:5683/.well-known/core
============================================================
服务器已启动，按 Ctrl+C 停止
============================================================
```

### 2. 测试服务器

在另一个终端运行：

```bash
.\.venv\Scripts\python.exe coap_token_replay\test_server.py
```

这会测试所有端点并显示结果。

### 3. 运行客户端

```bash
.\.venv\Scripts\python.exe coap_token_replay\client.py
```

### 4. 运行攻击脚本（可选）

需要管理员权限：

```bash
# Windows (管理员 PowerShell)
.\.venv\Scripts\python.exe coap_token_replay\attacker.py

# Linux/Mac
sudo python coap_token_replay/attacker.py
```

## 📊 服务器资源说明

### 1. `/` - 欢迎页面

**方法**: GET

**示例**:
```bash
coap-client -m get coap://127.0.0.1:5683/
```

**响应**:
```
CoAP Token Replay Attack Demo Server
Available resources:
  - /toggle
  - /status
  - /.well-known/core
```

---

### 2. `/toggle` - 状态切换

**方法**: GET, POST

**功能**: 切换服务器状态（ON/OFF）

**特性**:
- 第一个请求会延迟 2 秒（模拟网络延迟，便于攻击者捕获）
- 每个请求都会切换状态
- 使用请求计数器跟踪每个 Token 的请求次数

**示例**:
```bash
# GET 请求
coap-client -m get coap://127.0.0.1:5683/toggle

# POST 请求
coap-client -m post coap://127.0.0.1:5683/toggle
```

**响应示例**:
```
Toggle状态: ON (请求#1)
Toggle状态: OFF (请求#2)
```

---

### 3. `/status` - 服务器状态

**方法**: GET

**功能**: 返回服务器当前状态和时间

**特性**:
- 第一个请求会延迟 2 秒
- 显示请求序号和当前时间

**示例**:
```bash
coap-client -m get coap://127.0.0.1:5683/status
```

**响应示例**:
```
服务器状态: 运行中 (请求#1, 时间: 14:30:25)
```

---

### 4. `/.well-known/core` - 资源发现

**方法**: GET

**功能**: 返回服务器上所有可用资源的列表

**示例**:
```bash
coap-client -m get coap://127.0.0.1:5683/.well-known/core
```

## 🔧 代码结构

### 资源类

服务器使用以下资源类：

1. **`RequestCounter`** - 跟踪每个 Token 的请求次数
2. **`ToggleResource`** - 处理 `/toggle` 路径
3. **`StatusResource`** - 处理 `/status` 路径
4. **`WelcomeResource`** - 处理根路径 `/`

### 关键特性

```python
class ToggleResource(resource.Resource):
    def __init__(self, counter):
        super().__init__()
        self.counter = counter
        self.state = False
    
    async def render_get(self, request):
        # 处理 GET 请求
        count = self.counter.increment(request.token)
        
        # 第一个请求延迟 2 秒
        if count == 1:
            await asyncio.sleep(2)
        
        # 切换状态并返回响应
        self.state = not self.state
        return Message(code=Code.CONTENT, payload=...)
```

## 📝 日志输出

服务器会记录详细的请求和响应信息：

```
[14:30:23] 收到 GET /toggle - Token: 666978656431323, MsgID: 12345, 请求序号: 1
   → 第一个请求，延迟 2 秒响应...
[14:30:25] 发送响应 - Token: 666978656431323, 数据: Toggle状态: ON (请求#1)
```

## ⚠️ 注意事项

1. **端口绑定**: 服务器绑定到 `127.0.0.1:5683`，只能本地访问
2. **延迟设置**: 第一个请求延迟 2 秒，用于演示攻击场景
3. **Token 跟踪**: 使用 `RequestCounter` 跟踪每个 Token 的请求次数

## 🎯 演示 Token 重用攻击

完整的攻击演示流程：

1. **终端 1**: 启动服务器
   ```bash
   python coap_token_replay/server.py
   ```

2. **终端 2**: 启动攻击者（管理员权限）
   ```bash
   python coap_token_replay/attacker.py
   # 选择 Loopback 接口
   # 选择模式 1（自动嗅探）
   ```

3. **终端 3**: 运行客户端
   ```bash
   python coap_token_replay/client.py
   ```

4. **观察**: 在攻击者终端查看捕获和重放的数据包

## 🐛 故障排除

### 问题: "Address already in use"

**原因**: 端口 5683 已被占用

**解决**:
```bash
# Windows
netstat -ano | findstr :5683
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5683
kill -9 <PID>
```

### 问题: "No module named 'aiocoap'"

**解决**:
```bash
pip install aiocoap
```

### 问题: 客户端连接超时

**检查**:
1. 服务器是否正在运行
2. 防火墙是否阻止了连接
3. 使用正确的地址 `127.0.0.1:5683`

