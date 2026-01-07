# 快速开始指南 - CoAP Token Replay Attack

## 🚀 三步开始

### 步骤 1: 测试安装

```bash
# Windows (PowerShell 管理员模式)
.\.venv\Scripts\python.exe coap_token_replay\test_attacker_import.py

# Linux/Mac
source .venv/bin/activate
python coap_token_replay/test_attacker_import.py
```

看到 `All tests passed! ✓` 就可以继续了。

---

### 步骤 2: 查看可用网络接口

```bash
# Windows
.\.venv\Scripts\python.exe coap_token_replay\test_interface_selection.py

# Linux/Mac
python coap_token_replay/test_interface_selection.py
```

**记住 Loopback 接口的编号**（用于本地测试）

---

### 步骤 3: 运行攻击脚本

```bash
# Windows (PowerShell 管理员模式)
.\.venv\Scripts\python.exe coap_token_replay\attacker.py

# Linux/Mac
sudo python coap_token_replay/attacker.py
```

---

## 📋 完整测试流程

### 终端 1: 启动 CoAP 服务器

```bash
# 确保 server.py 已修复（bind 到 127.0.0.1）
.\.venv\Scripts\python.exe server.py
```

应该看到:
```
CoAP server is running on 127.0.0.1:5683
Press Ctrl+C to stop
```

---

### 终端 2: 启动攻击者（管理员权限）

```bash
# Windows - 以管理员身份运行 PowerShell
.\.venv\Scripts\python.exe coap_token_replay\attacker.py
```

**选择步骤:**
1. 当提示选择网络接口时，输入 **Loopback 接口的编号**（例如 `9`）
2. 当提示选择攻击模式时，输入 `1`（自动嗅探和攻击）

应该看到:
```
✓ 已选择接口: \Device\NPF_Loopback
当前使用接口: \Device\NPF_Loopback
开始嗅探接口 \Device\NPF_Loopback 上的CoAP流量...
嗅探线程已启动，按 Ctrl+C 停止...
```

---

### 终端 3: 运行 CoAP 客户端

```bash
.\.venv\Scripts\python.exe coap_token_replay\client.py
```

---

## 🎯 你应该看到什么

### 在攻击者终端（终端 2）:

```
[2026-01-03 ...] 捕获数据包 - Token: 1a2b3c, 类型: 0, 代码: 1
   → 捕获Token为 1a2b3c 的响应，将延迟发送
等待5秒后重放Token为 1a2b3c 的响应...
重放旧响应！Token: 1a2b3c, 目标: 127.0.0.1:xxxxx
```

这表示:
1. ✅ 捕获了 CoAP 请求
2. ✅ 捕获了 CoAP 响应
3. ✅ 5秒后重放了旧响应

---

## ⚠️ 常见问题

### 问题 1: "Permission denied" 或 "需要管理员权限"

**解决方案:**
- **Windows**: 右键点击 PowerShell → "以管理员身份运行"
- **Linux/Mac**: 使用 `sudo python ...`

---

### 问题 2: 没有捕获到任何数据包

**可能原因:**
1. ❌ 选择了错误的网络接口
   - **解决**: 确保选择了 Loopback 接口（用于本地测试）

2. ❌ 服务器和客户端没有运行
   - **解决**: 确保三个终端都在运行

3. ❌ 防火墙阻止了流量
   - **解决**: 临时关闭防火墙或添加例外

---

### 问题 3: "No module named 'scapy'"

**解决方案:**
```bash
# 确保使用虚拟环境中的 Python
# Windows
.\.venv\Scripts\python.exe -m pip install scapy

# Linux/Mac
source .venv/bin/activate
pip install scapy
```

---

## 📊 接口选择指南

### 本地测试（推荐）
- **选择**: Loopback 接口
- **Windows**: `\Device\NPF_Loopback`
- **Linux**: `lo`
- **Mac**: `lo0`

### 网络测试
- **选择**: 连接到网络的接口
- **Windows**: 通常是 `\Device\NPF_{GUID}` 格式
- **Linux**: `eth0`, `wlan0`, `enp0s3` 等
- **Mac**: `en0`, `en1` 等

### 如何判断?
运行 `test_interface_selection.py` 查看所有接口，标记为 "Loopback" 的就是本地回环接口。

---

## 🎓 学习模式

如果你只是想了解攻击原理，不需要实际运行:

```bash
.\.venv\Scripts\python.exe coap_token_replay\attacker.py
# 选择接口: 直接回车（使用默认）
# 选择模式: 输入 2（查看攻击步骤说明）
```

这会显示攻击的详细步骤说明，无需管理员权限。

---

## 📚 更多信息

- 详细使用说明: `coap_token_replay/USAGE.md`
- 调试总结: `ATTACKER_DEBUG_SUMMARY.md`
- 测试脚本: `coap_token_replay/test_attacker_import.py`

