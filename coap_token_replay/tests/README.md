# CoAP Token 重用攻击 - 测试套件

这个目录包含所有测试脚本，用于验证 Token 重用攻击演示的功能。

## 📁 测试文件

| 文件 | 说明 | 运行命令 |
|------|------|----------|
| `test_monkey_patch.py` | 测试 Monkey Patch 是否正确工作 | `uv run python tests/test_monkey_patch.py` |
| `test_token_parameter.py` | 测试不同的 Token 参数设置方法 | `uv run python tests/test_token_parameter.py` |
| `test_client_simple.py` | 简单客户端测试 | `uv run python tests/test_client_simple.py` |
| `test_attack.py` | 完整的攻击测试 | `uv run python tests/test_attack.py` |
| `test_attacker_import.py` | 测试攻击者模块导入 | `uv run python tests/test_attacker_import.py` |
| `test_interface_selection.py` | 测试网络接口选择 | `uv run python tests/test_interface_selection.py` |

## 🚀 快速运行

### 运行所有测试

```bash
cd coap_token_replay

# 测试 Monkey Patch
uv run python tests/test_monkey_patch.py

# 测试 Token 参数
uv run python tests/test_token_parameter.py

# 测试简单客户端
uv run python tests/test_client_simple.py
```

### 运行单个测试

```bash
cd coap_token_replay

# 只运行 Monkey Patch 测试
uv run python tests/test_monkey_patch.py
```

## 📋 测试说明

### 1. test_monkey_patch.py

**目的**：验证 Monkey Patch 是否正确保留手动设置的 Token

**测试内容**：
- 应用 Monkey Patch
- 创建带有固定 Token 的请求
- 验证 Token 在发送时被保留
- 验证响应中的 Token 匹配

**预期输出**：
```
✓ 已应用 Monkey Patch

【请求 #1】
  创建后 Token: 4649584544313233
  [Patch] 保留手动设置的 Token: 4649584544313233
  ✓ 收到响应
  发送的 Token: 4649584544313233
  响应的 Token: 4649584544313233
  ✓✓✓ Token 成功保留！
```

### 2. test_token_parameter.py

**目的**：测试不同的 Token 参数设置方法

**测试内容**：
- 使用 `token` 参数（已弃用）
- 使用 `_token` 参数（内部参数）
- 不设置 Token（默认行为）

**预期输出**：
```
测试 1: 使用 token 参数（已弃用）
  DeprecationWarning: Initializing messages with a token is deprecated.
  
测试 2: 使用 _token 参数
  ✓ Token 被保留
  
测试 3: 不设置 Token
  ✓ 自动生成 Token
```

### 3. test_client_simple.py

**目的**：测试简单的客户端请求

**测试内容**：
- 创建客户端上下文
- 发送简单的 GET 请求
- 验证响应

**预期输出**：
```
✓ 客户端创建成功
✓ 发送请求
✓ 收到响应
```

### 4. test_attack.py

**目的**：测试完整的攻击流程

**测试内容**：
- 启动服务器
- 运行客户端
- 执行攻击
- 验证攻击效果

### 5. test_attacker_import.py

**目的**：测试攻击者模块是否可以正确导入

**测试内容**：
- 导入 attacker 模块
- 验证所有必需的函数和类

### 6. test_interface_selection.py

**目的**：测试网络接口选择功能

**测试内容**：
- 列出所有网络接口
- 选择正确的接口
- 验证接口配置

## ⚠️ 运行前提

### 1. 启动服务器

所有测试都需要服务器运行：

```bash
cd coap_token_replay
uv run python server.py
```

### 2. 检查端口

确保端口 5683 未被占用：

```bash
# Windows
netstat -ano | findstr :5683

# Linux/Mac
lsof -i :5683
```

## 🔍 调试

### 启用详细日志

```bash
# 设置日志级别为 DEBUG
export AIOCOAP_LOG_LEVEL=DEBUG
uv run python tests/test_monkey_patch.py
```

### 查看网络流量

```bash
# 使用 tcpdump 查看 CoAP 流量
sudo tcpdump -i lo -n port 5683 -X
```

## 📊 测试结果

### 成功标准

- ✅ 所有测试无异常退出
- ✅ Token 被正确保留
- ✅ 响应匹配请求
- ✅ 没有 TypeError 或其他错误

### 失败排查

1. **服务器未启动**
   ```
   ConnectionRefusedError: [Errno 111] Connection refused
   ```
   **解决**：启动服务器 `uv run python server.py`

2. **端口被占用**
   ```
   OSError: [Errno 98] Address already in use
   ```
   **解决**：结束占用进程或更改端口

3. **Token 未保留**
   ```
   AssertionError: Token mismatch
   ```
   **解决**：检查 Monkey Patch 是否正确应用

## 📚 相关文档

- [主文档](../README.md)
- [快速开始](../docs/QUICK_START_TOKEN_REUSE.md)
- [Token 重用修复总结](../docs/TOKEN_REUSE_FIX_SUMMARY.md)
- [最终解决方案](../docs/FINAL_SOLUTION.md)

## 📝 添加新测试

要添加新测试：

1. 在 `tests/` 目录创建新文件 `test_xxx.py`
2. 导入必要的模块
3. 编写测试函数
4. 更新此 README

示例：

```python
#!/usr/bin/env python3
"""测试 XXX 功能"""

import asyncio
from aiocoap import *

async def test_xxx():
    """测试 XXX"""
    # 测试代码
    pass

if __name__ == "__main__":
    asyncio.run(test_xxx())
```

---

**需要帮助？** 请查看主 [README.md](../README.md) 或相关文档。

