# CoAP Token 重用攻击演示项目 - MITM 实现

这是一个演示 CoAP Token 重用攻击的完整项目，使用**中间人代理（MITM）**架构实现。

## 🎯 核心特性

- 🚀 **开箱即用**：无需管理员权限，无需 Scapy
- 🔧 **纯 Python 实现**：仅使用标准库
- 🌍 **跨平台**：支持 Windows/Linux/macOS
- 📚 **教育友好**：详细的文档和注释
- 🎯 **完全控制**：精确控制每个数据包

## 🏗️ MITM 架构

```
Client (127.0.0.1:random) → Attacker (127.0.0.1:5684) → Server (127.0.0.1:5683)
Client ← Attacker (延迟重放) ← Server
```

攻击者作为中间人代理，拦截并控制所有通信。

## 📁 项目结构

```
coap_token_replay/
├── server.py                      # CoAP 服务器
├── client.py                      # 易受攻击的客户端（包含 Monkey Patch）
├── attacker.py                    # 攻击者程序
├── demo_token_reuse_attack.py     # Token 重用攻击演示
├── demo_interface_usage.py        # 接口使用演示
├── quick_test.py                  # 快速测试脚本
├── test_server.py                 # 服务器测试
├── docs/                          # 📚 文档目录
│   ├── QUICK_START_TOKEN_REUSE.md # 快速开始指南
│   ├── TOKEN_REUSE_FIX_SUMMARY.md # Token 重用修复总结
│   ├── FINAL_SOLUTION.md          # 最终解决方案
│   ├── QUICK_START.md             # 通用快速开始
│   ├── USAGE.md                   # 使用说明
│   └── README_FIXED.md            # 修复说明
├── tests/                         # 🧪 测试目录
│   ├── test_monkey_patch.py       # Monkey Patch 测试
│   ├── test_token_parameter.py    # Token 参数测试
│   ├── test_client_simple.py      # 简单客户端测试
│   ├── test_attack.py             # 攻击测试
│   ├── test_attacker_import.py    # 攻击者导入测试
│   └── test_interface_selection.py # 接口选择测试
├── logs/                          # 📝 日志目录
└── resources/                     # 📦 资源目录
```

## 🚀 快速开始

### 方法 1: MITM 攻击演示（推荐 ⭐）

使用中间人代理实现完整的 Token 重用攻击。

**终端 1 - 启动服务器：**
```bash
cd coap_token_replay
uv run python server.py
```

**终端 2 - 启动攻击者（MITM 代理）：**
```bash
cd coap_token_replay
uv run python attacker.py
```

**终端 3 - 运行演示：**
```bash
cd coap_token_replay
uv run python demo_mitm_attack.py
```

**预期效果**：
- 第一个请求的响应被攻击者缓存
- 第二个请求正常收到响应
- 攻击者延迟后重放第一个请求的旧响应
- 客户端可能会将旧响应误认为新请求的响应

📚 **详细文档**: [MITM_ATTACK_GUIDE.md](MITM_ATTACK_GUIDE.md)

### 方法 2: Token 重用攻击演示（传统方式）

**终端 1 - 启动服务器：**
```bash
cd coap_token_replay
uv run python server.py
```

**终端 2 - 运行攻击演示：**
```bash
cd coap_token_replay
uv run python demo_token_reuse_attack.py
```

### 方法 2: 传统攻击演示

**终端 1 - 启动服务器：**
```bash
cd coap_token_replay
uv run python server.py
```

**终端 2 - 运行客户端：**
```bash
cd coap_token_replay
uv run python client.py
```

**终端 3 - 运行攻击者：**
```bash
cd coap_token_replay
uv run python attacker.py
```

## 📚 文档

### 快速导航

- **[📖 文档索引](docs/INDEX.md)** - 完整的文档导航
- **[📊 项目总结](PROJECT_SUMMARY.md)** - 项目概览和成果

### 主要文档

- **[快速开始 - Token 重用攻击](docs/QUICK_START_TOKEN_REUSE.md)** - 最简单的开始方式
- **[Token 重用修复总结](docs/TOKEN_REUSE_FIX_SUMMARY.md)** - 技术细节和实现
- **[最终解决方案](docs/FINAL_SOLUTION.md)** - 完整的解决方案文档
- **[服务器使用说明](SERVER_USAGE.md)** - 服务器配置和使用
- **[如何运行](HOW_TO_RUN.md)** - 详细的运行指南
- **[测试说明](tests/README.md)** - 测试套件文档

## 🔍 攻击原理

### Token 重用攻击

Token 重用攻击利用了客户端使用固定或可预测的 Token 的漏洞：

1. **漏洞**：客户端使用固定的 Token（如 `b'FIXED_TOKEN'`）
2. **拦截**：攻击者拦截客户端的请求和响应
3. **重放**：攻击者可以重放响应，导致客户端接收错误的数据
4. **混淆**：服务器无法区分合法请求和重放请求

### 演示效果

```
【请求 #1】Token: 56554c4e5f544f4b454e ⚠️ Token 被重用！
【请求 #2】Token: 56554c4e5f544f4b454e ⚠️ Token 被重用！
【请求 #3】Token: 56554c4e5f544f4b454e ⚠️ Token 被重用！
```

## 🛡️ 防御措施

- ✅ **使用随机生成的 Token**：每个请求使用唯一的随机 Token
- ✅ **Token 足够长**：至少 4 字节，推荐 8 字节
- ✅ **使用加密安全的随机数生成器**：如 `os.urandom()`
- ✅ **实现 Token 过期机制**：限制 Token 的有效时间
- ✅ **使用 DTLS/TLS**：加密传输层，防止中间人攻击

## 🔧 技术细节

### Monkey Patch 解决方案

由于 aiocoap 库不允许手动设置 Token，我们使用 Monkey Patch 来绕过限制：

```python
from aiocoap.tokenmanager import TokenManager

def _patched_request(self, request):
    # 只在 Token 为空时才分配新 Token
    if not msg.token:
        msg.token = self.next_token()
    # ... 其他代码

TokenManager.request = _patched_request
```

详见：[Token 重用修复总结](docs/TOKEN_REUSE_FIX_SUMMARY.md)

## 🧪 测试

运行所有测试：

```bash
cd coap_token_replay

# 测试 Monkey Patch
uv run python tests/test_monkey_patch.py

# 测试 Token 参数
uv run python tests/test_token_parameter.py

# 测试简单客户端
uv run python tests/test_client_simple.py
```

## 📚 文档索引

### MITM 攻击相关（新增 ⭐）
- [MITM 攻击指南](MITM_ATTACK_GUIDE.md) - 完整的 MITM 攻击使用指南
- [MITM 实现总结](MITM_IMPLEMENTATION_SUMMARY.md) - 技术实现细节
- [MITM 完成总结](FINAL_MITM_SUMMARY.md) - 项目完成总结

### 传统攻击相关
- [快速开始指南](docs/QUICK_START_TOKEN_REUSE.md) - 最快上手的方式
- [Token 重用修复总结](docs/TOKEN_REUSE_FIX_SUMMARY.md) - 技术细节和修复方案
- [最终解决方案](docs/FINAL_SOLUTION.md) - 完整的解决方案文档
- [使用说明](docs/USAGE.md) - 详细的使用说明
- [测试说明](tests/README.md) - 测试套件说明

## 📝 主要文件说明

### MITM 实现（新增）
- `attacker.py` - MITM 攻击者（中间人代理）
- `demo_mitm_attack.py` - MITM 攻击演示
- `test_mitm.py` - MITM 单元测试

### 核心文件
- `server.py` - CoAP 服务器
- `client.py` - CoAP 客户端（带 Monkey Patch）
- `demo_token_reuse_attack.py` - Token 重用攻击演示

## ⚠️ 重要说明

1. **这是演示代码**：仅用于教学和安全研究
2. **不要在生产环境使用**：Token 重用是一个严重的安全漏洞
3. **aiocoap 的默认行为是安全的**：它会自动为每个请求生成唯一的 Token
4. **Monkey Patch 仅用于演示**：不应在实际应用中使用

## 📖 相关资源

- [aiocoap 文档](https://aiocoap.readthedocs.io/)
- [RFC 7252 - CoAP 协议](https://tools.ietf.org/html/rfc7252)
- [CoAP Token 安全](https://tools.ietf.org/html/rfc7252#section-5.3.1)

## 📄 许可证

MIT License - 仅供教育和研究目的使用

