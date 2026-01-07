# CoAP Token 重用攻击 - 最终解决方案

## 📌 问题总结

**问题**：aiocoap 库不允许手动设置 Token，导致无法演示 Token 重用攻击。

**原因**：aiocoap 的 `TokenManager` 会在发送请求时强制覆盖 Token（`tokenmanager.py:231`）。

**解决方案**：使用 Monkey Patch 修改 `TokenManager.request()` 方法。

## ✅ 解决方案

### 核心代码

在 `client.py` 中添加以下 Monkey Patch：

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

    # ★ 关键：只在 Token 为空时才分配新 Token
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

    if send_canceller is not None:  # ← 重要：防止 TypeError
        request.on_interest_end(send_canceller)

# 应用 Monkey Patch
TokenManager.request = _patched_request
```

### 使用方法

```python
# 创建消息时使用 _token 参数
msg = Message(
    code=Code.GET,
    uri="coap://127.0.0.1:5683/toggle",
    _token=b'FIXED_TOKEN'  # 使用内部参数
)

# 发送请求
response = await context.request(msg).response

# Token 会被保留！
assert response.token == b'FIXED_TOKEN'  # ✓
```

## 🧪 测试结果

### 测试 1: Monkey Patch 验证

```bash
$ uv run python test_monkey_patch.py
```

**输出**：
```
✓ 已应用 Monkey Patch

【请求 #1】
  创建后 Token: 4649584544313233
  [Patch] 保留手动设置的 Token: 4649584544313233
  ✓ 收到响应
  发送的 Token: 4649584544313233
  响应的 Token: 4649584544313233
  ✓✓✓ Token 成功保留！

【请求 #2】
  创建后 Token: 4649584544313233
  [Patch] 保留手动设置的 Token: 4649584544313233
  ✓ 收到响应
  发送的 Token: 4649584544313233
  响应的 Token: 4649584544313233
  ✓✓✓ Token 成功保留！
```

### 测试 2: 完整攻击演示

```bash
$ uv run python demo_token_reuse_attack.py
```

**输出**：
```
【漏洞】使用固定 Token: 56554c4e5f544f4b454e

--- 请求 #1 ---
✓ 收到响应
  Token: 56554c4e5f544f4b454e
  数据: Toggle状态: ON (请求#1)
  ⚠️  Token 被重用！

--- 请求 #2 ---
✓ 收到响应
  Token: 56554c4e5f544f4b454e
  数据: Toggle状态: OFF (请求#2)
  ⚠️  Token 被重用！

--- 请求 #3 ---
✓ 收到响应
  Token: 56554c4e5f544f4b454e
  数据: Toggle状态: ON (请求#3)
  ⚠️  Token 被重用！
```

**服务器日志**：
```
INFO:CoAP-Server:[10:53:58] 收到 GET /toggle - Token: 56554c4e5f544f4b454e, 请求序号: 1
INFO:CoAP-Server:[10:54:00] 收到 GET /toggle - Token: 56554c4e5f544f4b454e, 请求序号: 2
INFO:CoAP-Server:[10:54:01] 收到 GET /toggle - Token: 56554c4e5f544f4b454e, 请求序号: 3
```

## 📁 修改的文件

| 文件 | 修改内容 |
|------|----------|
| `client.py` | 添加 Monkey Patch，修复 `send_request()` 方法 |
| `test_monkey_patch.py` | 创建测试脚本 |
| `demo_token_reuse_attack.py` | 创建完整演示 |
| `TOKEN_REUSE_FIX_SUMMARY.md` | 技术文档 |
| `QUICK_START_TOKEN_REUSE.md` | 快速开始指南 |

## 🎯 关键要点

1. **`_token` 参数可以设置 Token**，但会被 `TokenManager` 覆盖
2. **Monkey Patch 是必需的**，用于绕过 `TokenManager` 的强制覆盖
3. **`if send_canceller is not None:` 很重要**，防止 `TypeError`
4. **这是演示代码**，不应在生产环境使用

## 🛡️ 为什么 aiocoap 要禁止手动设置 Token？

**这是一个安全特性！**

- Token 重用是一个已知的安全漏洞
- 应用层不应该管理 Token
- 库应该自动确保 Token 的唯一性
- 每个请求都应该有唯一的 Token

## 📚 参考资料

- aiocoap 源代码: `aiocoap/tokenmanager.py`
- RFC 7252 (CoAP): https://tools.ietf.org/html/rfc7252
- CoAP Token 安全: https://tools.ietf.org/html/rfc7252#section-5.3.1

## ✨ 成功标准

- ✅ 可以手动设置 Token
- ✅ Token 在发送时被保留
- ✅ 多个请求可以使用相同的 Token
- ✅ 没有 TypeError 异常
- ✅ 服务器正确接收重复的 Token

