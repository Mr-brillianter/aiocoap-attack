# CoAP Token 重用攻击 - 修复总结

## 问题描述

aiocoap 库从某个版本开始，**不再允许手动设置 Token**，这使得它无法直接用于演示 Token 重用攻击。

### 核心问题

1. **`token` 参数已弃用**
   ```python
   msg = Message(code=Code.GET, uri="...", token=b'fixed')
   # DeprecationWarning: Initializing messages with a token is deprecated.
   ```

2. **`_token` 参数会被覆盖**
   ```python
   msg = Message(code=Code.GET, uri="...", _token=b'fixed')
   # Token 在 Context.request() 时被 TokenManager 覆盖
   ```

3. **TokenManager 强制分配新 Token**
   - 位置: `aiocoap/tokenmanager.py:231`
   - 代码: `msg.token = self.next_token()`
   - 结果: 无论如何设置，Token 都会被覆盖

## 解决方案

使用 **Monkey Patch** 修改 `TokenManager.request()` 方法，使其在 Token 已存在时不覆盖。

### 实现代码

```python
import functools
from aiocoap import error
from aiocoap.tokenmanager import TokenManager

def _patched_request(self, request):
    """修改后的 request 方法，允许保留手动设置的 Token"""
    if self.outgoing_requests is None:
        request.add_exception(error.LibraryShutdown())
        return

    msg = request.request
    assert msg.code.is_request(), "Message code is not valid for request"
    assert msg.remote is not None, "Remote not pre-populated"

    # ★ 关键修改：只在 Token 为空时才分配新 Token
    if not msg.token:
        msg.token = self.next_token()
    
    self.log.debug("Sending request - Token: %s, Remote: %s", msg.token.hex(), msg.remote)

    if msg.remote.is_multicast:
        key = (msg.token, None)
    else:
        key = (msg.token, msg.remote)

    self.outgoing_requests[key] = request
    request.on_interest_end(functools.partial(self.outgoing_requests.pop, key, None))

    try:
        send_canceller = self.token_interface.send_message(
            msg, lambda: request.add_exception(error.MessageError)
        )
    except Exception as e:
        request.add_exception(e)
        return

    # ★ 重要：检查 send_canceller 是否为 None
    if send_canceller is not None:
        request.on_interest_end(send_canceller)

# 应用 Monkey Patch
TokenManager.request = _patched_request
```

### 使用方法

```python
# 1. 应用 Monkey Patch（在导入 aiocoap 后）
TokenManager.request = _patched_request

# 2. 创建消息时使用 _token 参数
msg = Message(
    code=Code.GET,
    uri="coap://127.0.0.1:5683/toggle",
    _token=b'FIXED_TOKEN'  # 使用内部参数
)

# 3. 发送请求
response = await context.request(msg).response

# 4. 验证 Token 是否被保留
assert response.token == b'FIXED_TOKEN'  # ✓ 成功！
```

## 测试结果

### 修复前
```
创建后 Token: 46495845445f544f4b454e5f313233
发送时 Token: 3b79  ← 被 TokenManager 覆盖！
响应 Token: 3b79
```

### 修复后
```
创建后 Token: 46495845445f544f4b454e5f313233
发送时 Token: 46495845445f544f4b454e5f313233  ← 成功保留！
响应 Token: 46495845445f544f4b454e5f313233
```

## 文件清单

| 文件 | 说明 |
|------|------|
| `client.py` | 修改后的客户端，包含 Monkey Patch |
| `test_monkey_patch.py` | 测试 Monkey Patch 是否有效 |
| `demo_token_reuse_attack.py` | 完整的 Token 重用攻击演示 |
| `test_token_parameter.py` | 测试不同 Token 参数的行为 |

## 运行演示

```bash
# 1. 启动服务器
uv run python server.py

# 2. 在另一个终端运行演示
uv run python demo_token_reuse_attack.py
```

## 重要说明

1. **这是演示代码**：Monkey Patch 仅用于演示安全漏洞，不应在生产环境使用
2. **aiocoap 的设计是正确的**：禁止手动设置 Token 是一个安全特性
3. **演示目的**：展示为什么 Token 重用是危险的，以及为什么 aiocoap 要防止它

## 为什么 aiocoap 禁止手动设置 Token？

**这是一个安全特性！**

- Token 重用是一个已知的安全漏洞
- 应用层不应该管理 Token
- 库应该自动确保 Token 的唯一性
- 这正是安全的 CoAP 实现应该做的！

## 参考

- aiocoap 源代码: `aiocoap/tokenmanager.py`
- aiocoap 文档: https://aiocoap.readthedocs.io/
- RFC 7252 (CoAP): https://tools.ietf.org/html/rfc7252

