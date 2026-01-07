# CoAP Token Replay Attack - 修复版本

## ✅ 已修复的问题

本版本修复了原始 `attacker.py` 中的所有问题：

1. ✅ **导入错误** - 修复了 `scapy.layers.coap` → `scapy.contrib.coap`
2. ✅ **异步集成** - 修复了 asyncio 与 scapy 的集成问题
3. ✅ **跨平台支持** - 添加了 Windows/Linux/Mac 自动检测
4. ✅ **数据包构造** - 修复了 CoAP 数据包的正确语法
5. ✅ **接口选择** - 添加了网络接口选择功能

## 🚀 快速开始

### 1. 测试安装

```bash
# Windows (管理员 PowerShell)
.\.venv\Scripts\python.exe test_attacker_import.py

# Linux/Mac
sudo python test_attacker_import.py
```

### 2. 查看网络接口

```bash
.\.venv\Scripts\python.exe test_interface_selection.py
```

记住 **Loopback 接口的编号**（用于本地测试）

### 3. 运行攻击脚本

```bash
# Windows (管理员 PowerShell)
.\.venv\Scripts\python.exe attacker.py

# Linux/Mac
sudo python attacker.py
```

**选择步骤:**
1. 输入 Loopback 接口编号（例如 `9`）
2. 选择攻击模式 `1`（自动嗅探）

## 📁 文件说明

### 核心文件
- **`attacker.py`** - 主攻击脚本（已修复）
- **`client.py`** - CoAP 客户端
- **`server.py`** - CoAP 服务器

### 测试文件
- **`test_attacker_import.py`** - 测试所有导入和基本功能
- **`test_interface_selection.py`** - 显示所有网络接口
- **`demo_interface_usage.py`** - 演示接口使用方法

### 文档
- **`QUICK_START.md`** - 快速开始指南（中文）
- **`USAGE.md`** - 详细使用说明（英文）
- **`README_FIXED.md`** - 本文件

## 🎯 完整测试流程

### 终端 1: CoAP 服务器
```bash
.\.venv\Scripts\python.exe ..\server.py
```

### 终端 2: 攻击者（管理员）
```bash
.\.venv\Scripts\python.exe attacker.py
# 选择 Loopback 接口（例如 9）
# 选择模式 1
```

### 终端 3: CoAP 客户端
```bash
.\.venv\Scripts\python.exe client.py
```

## 📊 预期结果

在攻击者终端应该看到：

```
[2026-01-03 ...] 捕获数据包 - Token: abc123, 类型: 0, 代码: 1
   → 捕获Token为 abc123 的响应，将延迟发送
等待5秒后重放Token为 abc123 的响应...
重放旧响应！Token: abc123, 目标: 127.0.0.1:xxxxx
```

## ⚠️ 重要提示

### Windows 用户
1. 必须安装 **Npcap**: https://npcap.com/
2. 必须以**管理员身份**运行 PowerShell
3. 选择 `\Device\NPF_Loopback` 接口进行本地测试

### Linux/Mac 用户
1. 必须使用 `sudo` 运行脚本
2. 选择 `lo` 或 `lo0` 接口进行本地测试

### 接口选择
- **本地测试**: 选择 Loopback 接口
- **网络测试**: 选择对应的网络适配器
- **不确定**: 直接回车使用默认接口

## 🔧 技术细节

### 主要改进

1. **导入修复**
   ```python
   # 之前 ❌
   from scapy.layers.coap import *
   
   # 现在 ✅
   from scapy.contrib.coap import *
   ```

2. **异步集成**
   ```python
   # 在单独线程中运行 sniff
   self.sniff_thread = Thread(target=self._sniff_thread, daemon=True)
   
   # 使用线程安全的方式调度协程
   asyncio.run_coroutine_threadsafe(self.replay_response(...), self.loop)
   ```

3. **接口自动检测**
   ```python
   if platform.system() == "Windows":
       self.interface = conf.iface
   else:
       self.interface = "lo"
   ```

4. **正确的数据包构造**
   ```python
   # CoAP 数据包 + Raw payload
   packet = (IP(...) / UDP(...) / 
             CoAP(type="ACK", code=69, token=b'test') / 
             Raw(load=b"payload"))
   ```

## 📚 更多资源

- **调试总结**: `../ATTACKER_DEBUG_SUMMARY.md`
- **快速开始**: `QUICK_START.md`
- **详细使用**: `USAGE.md`

## 🎓 学习模式

如果只想了解攻击原理，无需管理员权限：

```bash
.\.venv\Scripts\python.exe attacker.py
# 接口: 直接回车
# 模式: 选择 2（查看攻击步骤说明）
```

## ⚖️ 免责声明

此工具仅用于**教育和研究目的**。仅在您拥有或有明确授权的网络上使用。未经授权的网络嗅探和数据包注入可能违法。

