# 调试指南

## 🔍 当前问题

从服务器日志看到：

```
INFO:CoAP-Server:[13:30:23] 收到 GET /time - Token: 7876, MsgID: 64201, 请求序号: 1
INFO:CoAP-Server:[13:30:30] 收到 GET /time - Token: 7877, MsgID: 64202, 请求序号: 1
```

**问题**：
1. Token 是 `7876` 和 `7877`，而不是我们发送的 `aabbccdd`
2. 两次都是"请求序号: 1"，说明服务器认为这是不同 Token 的第一个请求

## 🤔 可能的原因

### 原因 1: aiocoap 服务器自动生成 Token

aiocoap 服务器可能会忽略客户端发送的 Token，自动生成新的 Token。

**验证方法**：
```bash
# 直接发送请求到服务器（绕过攻击者）
uv run python test_direct_server.py
```

查看服务器日志，看看它记录的 Token 是什么。

### 原因 2: 攻击者修改了 Token

攻击者在转发时可能修改了 Token。

**验证方法**：
查看攻击者日志中的"原始数据"和"转发数据"，确认它们是否相同。

### 原因 3: aiocoap 客户端发送的请求

如果使用了 `demo_mitm_attack.py`（使用 aiocoap 客户端），aiocoap 会自动生成 Token。

**解决方案**：
使用 `demo_mitm_simple.py`（使用原始 socket）。

## 🧪 调试步骤

### 步骤 1: 测试 CoAP 消息生成

```bash
uv run python test_coap_message.py
```

**预期输出**：
```
✅ Token 匹配
✅ Message ID 匹配
✅ 完全匹配！
```

✅ **已验证**：CoAP 消息生成是正确的。

### 步骤 2: 直接测试服务器

```bash
# 确保服务器正在运行
# 然后运行：
uv run python test_direct_server.py
```

**目的**：验证服务器是否能正确接收和解析我们的 Token。

**查看服务器日志**：
- 如果服务器记录的 Token 是 `aabbccdd`，说明服务器正常 ✅
- 如果服务器记录的 Token 是其他值，说明 aiocoap 服务器有问题 ❌

### 步骤 3: 测试攻击者转发

```bash
# 终端 1: 启动服务器
uv run python server.py

# 终端 2: 启动攻击者（带调试日志）
uv run python attacker.py

# 终端 3: 运行演示
uv run python demo_mitm_simple.py
```

**查看攻击者日志**：
- 检查"原始数据"和"转发数据"是否相同
- 检查 Token 是否是 `aabbccdd`

## 📊 日志分析

### 服务器日志

```
INFO:CoAP-Server:[13:30:23] 收到 GET /time - Token: 7876, MsgID: 64201, 请求序号: 1
```

**分析**：
- Token `7876` = `0x78 0x76` = ASCII `'x' 'v'`
- 这不是我们发送的 `aabbccdd` = `0xAA 0xBB 0xCC 0xDD`

**可能性**：
1. aiocoap 服务器自动生成了新的 Token
2. 攻击者修改了 Token
3. 客户端发送的不是我们期望的请求

### 攻击者日志（需要查看）

**期望看到**：
```
======================================================================
📤 [请求 #1] 客户端 → 攻击者
   Token: aabbccdd
   原始数据: 440103e9aabbccddb474696d65
📨 [转发] 攻击者 → 服务器
   转发数据: 440103e9aabbccddb474696d65
======================================================================
```

**如果看到不同的 Token**：
说明客户端发送的请求有问题。

## 🔧 修复建议

### 建议 1: 检查 aiocoap 服务器的行为

aiocoap 服务器可能会：
- 忽略客户端的 Token
- 自动生成新的 Token
- 使用自己的 Token 管理机制

**解决方案**：
查看 aiocoap 文档，了解服务器如何处理 Token。

### 建议 2: 使用原始 socket 服务器

如果 aiocoap 服务器不适合我们的需求，可以：
- 创建一个简单的 UDP 服务器
- 手动解析 CoAP 消息
- 完全控制 Token 处理

### 建议 3: 修改服务器日志

在 `server.py` 中，添加更详细的日志：

```python
async def render_get(self, request):
    # 添加原始数据日志
    logger.info(f"原始请求数据: {request.payload.hex()}")
    logger.info(f"Token (bytes): {request.token}")
    logger.info(f"Token (hex): {request.token.hex()}")
```

## 🎯 下一步

1. **运行 `test_direct_server.py`**，查看服务器日志
2. **查看攻击者日志**，确认转发的数据
3. **根据结果决定**：
   - 如果服务器正常：问题在攻击者
   - 如果服务器异常：问题在 aiocoap 服务器
   - 如果都正常：问题在客户端

## 📝 记录

### 已验证
- ✅ CoAP 消息生成正确（`test_coap_message.py`）
- ✅ Token `aabbccdd` 正确编码为 `0xAA 0xBB 0xCC 0xDD`

### 待验证
- ❓ 服务器是否正确接收 Token
- ❓ 攻击者是否正确转发 Token
- ❓ 客户端是否发送了正确的请求

### 下一步测试
1. 运行 `test_direct_server.py`
2. 查看服务器日志中的 Token
3. 查看攻击者日志中的原始数据和转发数据

