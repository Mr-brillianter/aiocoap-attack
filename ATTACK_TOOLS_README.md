# CoAP 攻击工具集 / CoAP Attack Tools

基于 aiocoap 库开发的 CoAP 安全测试工具集，用于教育和授权的安全测试。

## ⚠️ 重要声明

**这些工具仅用于教育、学习和授权的安全测试目的。未经授权对他人系统进行攻击是违法行为。使用者需对自己的行为负全部法律责任。**

## 📦 工具列表

### 1. 重放攻击脚本 (`coap_replay_attack.py`)
捕获并重放 CoAP 请求，测试服务器对重复请求的处理能力。

### 2. 泛洪攻击脚本 (`coap_flood_attack.py`)
发送大量 CoAP 请求，测试服务器的负载能力和抗 DoS 能力。

### 3. 测试服务器 (`test_server.py`)
提供一个简单的 CoAP 服务器用于测试攻击脚本。

### 4. 演示脚本 (`demo_attacks.py`)
自动演示重放攻击和泛洪攻击的效果。

## 🚀 快速开始

### 安装依赖

```bash
# 使用 uv（推荐）
uv pip install aiocoap

# 或使用 pip
pip install aiocoap
```

### 三步开始测试

```bash
# 步骤 1: 启动测试服务器（终端 1）
python test_server.py

# 步骤 2: 运行重放攻击（终端 2）
python coap_replay_attack.py coap://localhost/sensor -d 10 -r 5

# 步骤 3: 运行泛洪攻击（终端 2）
python coap_flood_attack.py coap://localhost/sensor -d 10 -r 20
```

### 自动演示

```bash
# 启动测试服务器（终端 1）
python test_server.py

# 运行自动演示（终端 2）
python demo_attacks.py
```

## 📖 文档

- **[QUICKSTART.md](QUICKSTART.md)** - 快速开始指南，包含详细的分步教程
- **[ATTACK_SCRIPTS_README.md](ATTACK_SCRIPTS_README.md)** - 完整的使用文档和参数说明
- **[ATTACK_TOOLS_SUMMARY.md](ATTACK_TOOLS_SUMMARY.md)** - 工具功能总结和测试场景

## 🎯 主要特性

### 重放攻击
- ✅ 自动捕获原始请求
- ✅ 保持相同的 token 进行重放
- ✅ 可配置速率和持续时间
- ✅ 实时统计成功/失败率
- ✅ 安全限制（最大 300 秒，100 请求/秒）

### 泛洪攻击
- ✅ 高速率请求发送
- ✅ 可配置并发连接数
- ✅ 支持随机负载生成
- ✅ 多种 HTTP 方法支持
- ✅ 实时性能监控
- ✅ 安全限制（最大 300 秒，200 请求/秒，50 并发）

### 测试服务器
- ✅ 多个测试资源 (/sensor, /data, /stats)
- ✅ 实时请求统计
- ✅ 支持 GET/POST/PUT/DELETE 方法
- ✅ 自动日志记录

## 📊 使用示例

### 基础重放攻击
```bash
python coap_replay_attack.py coap://localhost/sensor --duration 10 --rate 5
```

### 高强度泛洪攻击
```bash
python coap_flood_attack.py coap://localhost/sensor -d 30 -r 100 -c 30
```

### POST 方法攻击
```bash
python coap_flood_attack.py coap://localhost/data -m POST --random-payload --payload-size 500
```

### 查看服务器统计
```bash
python -m aiocoap.cli.client coap://localhost/stats
```

## 🛡️ 安全限制

为防止意外造成系统崩溃，所有脚本都内置了安全限制：

| 参数 | 最大值 | 说明 |
|------|--------|------|
| 持续时间 | 300 秒 | 防止长时间攻击 |
| 重放速率 | 100 请求/秒 | 重放攻击速率限制 |
| 泛洪速率 | 200 请求/秒 | 泛洪攻击速率限制 |
| 并发数 | 50 | 最大并发连接数 |
| 负载大小 | 1024 字节 | 单个请求最大负载 |

## 🔬 测试场景

### 场景 1: 基础功能测试
```bash
python coap_replay_attack.py coap://localhost/sensor -d 5 -r 2
python coap_flood_attack.py coap://localhost/sensor -d 5 -r 5
```

### 场景 2: 中等强度测试
```bash
python coap_replay_attack.py coap://localhost/sensor -d 30 -r 20
python coap_flood_attack.py coap://localhost/sensor -d 30 -r 50 -c 20
```

### 场景 3: 高强度压力测试
```bash
python coap_replay_attack.py coap://localhost/sensor -d 60 -r 50
python coap_flood_attack.py coap://localhost/sensor -d 60 -r 100 -c 30
```

## 🛠️ 技术栈

- **Python 3.11+**: 推荐版本
- **aiocoap**: CoAP 协议实现
- **asyncio**: 异步 I/O 支持

## 📚 相关资源

- [aiocoap 官方文档](https://aiocoap.readthedocs.io/)
- [CoAP RFC 7252](https://tools.ietf.org/html/rfc7252)
- [OSCORE RFC 8613](https://tools.ietf.org/html/rfc8613)

## 🤝 贡献

欢迎提交问题和改进建议。

## 📄 许可证

这些工具遵循 MIT 许可证，与 aiocoap 库保持一致。

## ⚖️ 法律责任

**再次强调：**

✅ **允许用于：**
- 教育和学习目的
- 授权的安全测试
- 自己系统的性能测试

❌ **禁止用于：**
- 未经授权的系统攻击
- 恶意破坏
- 任何非法活动

使用者需对自己的行为负全部法律责任。作者不对任何滥用行为负责。

---

**版本**: 1.0  
**创建日期**: 2024-12-23  
**基于**: aiocoap 0.4.17

