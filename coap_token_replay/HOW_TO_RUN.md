# 如何运行 CoAP Token Replay Attack 演示

## 📁 项目结构

```
coap_token_replay/
├── server.py                      # CoAP 服务器
├── client.py                      # 客户端（包含 Monkey Patch）
├── attacker.py                    # 攻击者程序
├── demo_token_reuse_attack.py     # Token 重用攻击演示
├── docs/                          # 📚 文档目录
│   ├── QUICK_START_TOKEN_REUSE.md
│   ├── TOKEN_REUSE_FIX_SUMMARY.md
│   └── FINAL_SOLUTION.md
└── tests/                         # 🧪 测试目录
    ├── test_monkey_patch.py
    ├── test_token_parameter.py
    └── test_client_simple.py
```

## 🎯 三步快速开始

### 步骤 1: 启动服务器

打开**终端 1**:

```bash
cd coap_token_replay
uv run python server.py
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
============================================================
服务器已启动，按 Ctrl+C 停止
============================================================
```

✅ 如果看到这个输出，服务器已成功启动！

---

### 步骤 2: 运行 Token 重用攻击演示

打开**终端 2**:

```bash
cd coap_token_replay
uv run python demo_token_reuse_attack.py
```

**预期输出**:
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

✅ 如果看到这个输出，服务器工作正常！

---

### 步骤 3: 运行完整演示

#### 选项 A: 仅运行客户端（无攻击）

在**终端 2**:

```bash
.\.venv\Scripts\python.exe coap_token_replay\client.py
```

这会发送两个使用相同 Token 的请求。

---

#### 选项 B: 运行完整攻击演示

**终端 1**: 服务器（已运行）

**终端 2**: 攻击者（需要管理员权限）

```bash
# Windows (管理员 PowerShell)
.\.venv\Scripts\python.exe coap_token_replay\attacker.py

# Linux/Mac
sudo python coap_token_replay/attacker.py
```

**选择步骤**:
1. 选择 Loopback 接口（例如输入 `9`）
2. 选择模式 `1`（自动嗅探和攻击）

**终端 3**: 客户端

```bash
.\.venv\Scripts\python.exe coap_token_replay\client.py
```

---

## 📊 预期结果

### 服务器终端（终端 1）

```
[14:30:23] 收到 GET /toggle - Token: 666978656431323, MsgID: 12345, 请求序号: 1
   → 第一个请求，延迟 2 秒响应...
[14:30:25] 发送响应 - Token: 666978656431323, 数据: Toggle状态: ON (请求#1)
[14:30:26] 收到 GET /toggle - Token: 666978656431323, MsgID: 12346, 请求序号: 2
[14:30:26] 发送响应 - Token: 666978656431323, 数据: Toggle状态: OFF (请求#2)
```

### 客户端终端（终端 3）

```
[2026-01-03 14:30:23] 发送请求#1 - 路径: toggle, Token: 666978656431323
[2026-01-03 14:30:24] 发送请求#2 - 路径: toggle, Token: 666978656431323
[2026-01-03 14:30:25] 收到响应#1 - Token: 666978656431323, 数据: Toggle状态: ON (请求#1)
[2026-01-03 14:30:26] 收到响应#2 - Token: 666978656431323, 数据: Toggle状态: OFF (请求#2)
```

### 攻击者终端（终端 2，如果运行）

```
[2026-01-03 14:30:25] 捕获数据包 - Token: 666978656431323, 类型: ACK, 代码: CONTENT
   → 捕获Token为 666978656431323 的响应，将延迟发送
等待5秒后重放Token为 666978656431323 的响应...
[2026-01-03 14:30:30] 重放旧响应！Token: 666978656431323
```

---

## 🐛 故障排除

### 问题 1: "Address already in use"

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

---

### 问题 2: "No module named 'aiocoap'"

**解决**:
```bash
pip install aiocoap
```

---

### 问题 3: 客户端连接超时

**检查清单**:
- [ ] 服务器是否正在运行？
- [ ] 使用正确的地址 `127.0.0.1:5683`？
- [ ] 防火墙是否阻止了连接？

**测试连接**:
```bash
.\.venv\Scripts\python.exe coap_token_replay\quick_test.py
```

---

### 问题 4: 攻击者无法捕获数据包（Windows）

**检查清单**:
- [ ] 是否以**管理员身份**运行 PowerShell？
- [ ] 是否安装了 **Npcap**？ (https://npcap.com/)
- [ ] 是否选择了正确的 **Loopback 接口**？

**验证 Npcap**:
```bash
.\.venv\Scripts\python.exe coap_token_replay\test_interface_selection.py
```

---

### 问题 5: 攻击者无法捕获数据包（Linux/Mac）

**检查清单**:
- [ ] 是否使用 `sudo` 运行？
- [ ] 是否选择了 `lo` 或 `lo0` 接口？

---

## 📁 文件说明

| 文件 | 用途 | 需要管理员权限 |
|------|------|----------------|
| `server.py` | CoAP 服务器 | ❌ 否 |
| `client.py` | CoAP 客户端 | ❌ 否 |
| `attacker.py` | 攻击脚本 | ✅ 是 |
| `quick_test.py` | 快速测试 | ❌ 否 |
| `test_server.py` | 完整测试 | ❌ 否 |
| `test_interface_selection.py` | 接口测试 | ❌ 否 |

---

## 🎓 学习模式（无需管理员权限）

如果只想了解攻击原理，无需运行攻击脚本：

```bash
# 1. 启动服务器
.\.venv\Scripts\python.exe coap_token_replay\server.py

# 2. 在另一个终端运行客户端
.\.venv\Scripts\python.exe coap_token_replay\client.py

# 3. 查看攻击步骤说明
.\.venv\Scripts\python.exe coap_token_replay\attacker.py
# 接口: 直接回车
# 模式: 选择 2（查看攻击步骤说明）
```

---

## 📚 更多资源

- **服务器使用说明**: `SERVER_USAGE.md`
- **服务器重写总结**: `../SERVER_REWRITE_SUMMARY.md`
- **攻击脚本调试**: `../ATTACKER_DEBUG_SUMMARY.md`
- **快速开始**: `QUICK_START.md`

---

## ⚖️ 免责声明

此工具仅用于**教育和研究目的**。仅在您拥有或有明确授权的网络上使用。

