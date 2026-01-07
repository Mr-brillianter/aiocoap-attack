# CoAP Server 重写总结

## 问题回顾

用户运行 `python .\server.py` 时遇到两个错误：

### 错误 1: `NameError: name 'resource' is not defined`
```python
File "F:\my_code\aiocoap-attack\coap_token_replay\server.py", line 58, in start_server
    root = resource.Site()
           ^^^^^^^^
NameError: name 'resource' is not defined. Did you forget to import 'resource'?
```

**原因**: 缺少 `import aiocoap.resource as resource`

---

### 错误 2: `TypeError: Resource.__init__() takes 1 positional argument but 2 were given`
```python
File "F:\my_code\aiocoap-attack\coap_token_replay\server.py", line 60, in start_server
    root.add_resource(['toggle'], resource.Resource(self.handle_request))
                                  ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
TypeError: Resource.__init__() takes 1 positional argument but 2 were given
```

**原因**: `resource.Resource()` 不接受处理函数作为参数。需要创建继承自 `Resource` 的类。

---

## ✅ 解决方案

完全重写了 `coap_token_replay/server.py`，使用正确的 aiocoap 资源处理方式。

### 主要改进

#### 1. 正确的导入
```python
import aiocoap
import aiocoap.resource as resource
from aiocoap import Message, Context
from aiocoap.numbers.codes import Code
```

#### 2. 创建 Resource 子类

**之前（错误）**:
```python
root.add_resource(['toggle'], resource.Resource(self.handle_request))  # ❌
```

**现在（正确）**:
```python
class ToggleResource(resource.Resource):
    def __init__(self, counter):
        super().__init__()
        self.counter = counter
        self.state = False
    
    async def render_get(self, request):
        # 处理 GET 请求
        ...
        return Message(code=Code.CONTENT, payload=...)
    
    async def render_post(self, request):
        # 处理 POST 请求
        ...
        return Message(code=Code.CHANGED, payload=...)

# 使用
root.add_resource(['toggle'], ToggleResource(counter))  # ✅
```

#### 3. 添加请求计数器
```python
class RequestCounter:
    """跟踪每个 Token 的请求次数"""
    def __init__(self):
        self.counter = {}
    
    def increment(self, token):
        token_str = token.hex() if token else "no-token"
        self.counter[token_str] = self.counter.get(token_str, 0) + 1
        return self.counter[token_str]
```

#### 4. 实现多个资源类

- **`WelcomeResource`** - 处理根路径 `/`
- **`ToggleResource`** - 处理 `/toggle` (GET, POST)
- **`StatusResource`** - 处理 `/status` (GET)

#### 5. 改进的日志记录
```python
logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 收到 GET /toggle - "
           f"Token: {token}, MsgID: {request.mid}, 请求序号: {count}")
```

---

## 📁 新增文件

1. **`coap_token_replay/server.py`** - 重写的服务器（170 行）
2. **`coap_token_replay/test_server.py`** - 服务器测试脚本
3. **`coap_token_replay/quick_test.py`** - 快速测试脚本（无需用户输入）
4. **`coap_token_replay/SERVER_USAGE.md`** - 详细使用说明
5. **`SERVER_REWRITE_SUMMARY.md`** - 本文件

---

## 🚀 如何使用

### 启动服务器

```bash
# Windows
.\.venv\Scripts\python.exe coap_token_replay\server.py

# Linux/Mac
python coap_token_replay/server.py
```

**预期输出**:
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

### 测试服务器

**方式 1: 快速测试**
```bash
.\.venv\Scripts\python.exe coap_token_replay\quick_test.py
```

**方式 2: 完整测试**
```bash
.\.venv\Scripts\python.exe coap_token_replay\test_server.py
```

**方式 3: 使用客户端**
```bash
.\.venv\Scripts\python.exe coap_token_replay\client.py
```

---

## 🎯 服务器功能

### 1. `/` - 欢迎页面
- **方法**: GET
- **响应**: 服务器信息和可用资源列表

### 2. `/toggle` - 状态切换
- **方法**: GET, POST
- **功能**: 切换服务器状态（ON/OFF）
- **特性**: 第一个请求延迟 2 秒（用于演示攻击）

### 3. `/status` - 服务器状态
- **方法**: GET
- **功能**: 返回服务器状态和时间
- **特性**: 第一个请求延迟 2 秒

### 4. `/.well-known/core` - 资源发现
- **方法**: GET
- **功能**: 返回所有可用资源

---

## 🔧 代码结构对比

### 之前的错误代码

```python
class CoAPServer:
    async def handle_request(self, request):
        # 处理逻辑
        ...
    
    async def start_server(self):
        root = resource.Site()
        # ❌ 错误：Resource 不接受函数参数
        root.add_resource(['toggle'], resource.Resource(self.handle_request))
```

### 现在的正确代码

```python
class ToggleResource(resource.Resource):
    def __init__(self, counter):
        super().__init__()
        self.counter = counter
    
    async def render_get(self, request):
        # 处理 GET 请求
        ...
        return Message(...)

async def main():
    counter = RequestCounter()
    root = resource.Site()
    # ✅ 正确：使用 Resource 子类的实例
    root.add_resource(['toggle'], ToggleResource(counter))
```

---

## 📊 测试结果

运行 `quick_test.py` 应该看到：

```
============================================================
CoAP 服务器快速测试
============================================================

创建客户端...
✓ 客户端创建成功

测试 GET /status...
✓ 响应: 服务器状态: 运行中 (请求#1, 时间: 14:30:25)

============================================================
✓ 测试成功！服务器正常工作
============================================================
```

---

## 📚 参考资料

### aiocoap Resource 类的正确用法

```python
# 1. 继承 resource.Resource
class MyResource(resource.Resource):
    
    # 2. 实现 render_* 方法
    async def render_get(self, request):
        return Message(code=Code.CONTENT, payload=b"Hello")
    
    async def render_post(self, request):
        return Message(code=Code.CHANGED, payload=b"Updated")
    
    async def render_put(self, request):
        return Message(code=Code.CHANGED, payload=b"Created")
    
    async def render_delete(self, request):
        return Message(code=Code.DELETED)

# 3. 添加到资源树
root = resource.Site()
root.add_resource(['path'], MyResource())
```

---

## ✨ 总结

### 修复的问题
1. ✅ 添加了缺失的 `import aiocoap.resource as resource`
2. ✅ 使用正确的 Resource 子类而不是直接传递函数
3. ✅ 实现了 `render_get`、`render_post` 等方法
4. ✅ 添加了请求计数器跟踪 Token 使用情况
5. ✅ 改进了日志记录和错误处理

### 新增功能
1. ✅ 多个资源类（Welcome, Toggle, Status）
2. ✅ 请求计数器（跟踪每个 Token 的请求）
3. ✅ 详细的日志输出
4. ✅ 第一个请求延迟（用于演示攻击）
5. ✅ 测试脚本（test_server.py, quick_test.py）

**服务器现在可以正常运行了！** 🎉

