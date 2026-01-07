# 快速开始指南 (Quick Start Guide)

本指南将帮助你快速设置和运行 CoAP 攻击测试脚本。

## 📦 步骤 1: 安装依赖

```bash
# 使用 uv 安装 aiocoap（推荐，适用于 Windows）
uv pip install aiocoap

# 或使用 pip
pip install aiocoap
```

## 🚀 步骤 2: 启动测试服务器

在第一个终端窗口中启动测试服务器：

```bash
python test_server.py
```

你应该看到类似以下的输出：

```
============================================================
CoAP 测试服务器启动
============================================================
监听地址: localhost:5683
可用资源:
  - coap://localhost:5683/sensor  (GET, POST)
  - coap://localhost:5683/data    (GET, POST, PUT, DELETE)
  - coap://localhost:5683/stats   (GET - 查看统计)
============================================================
按 Ctrl+C 停止服务器
```

## 🎯 步骤 3: 测试服务器连接

在第二个终端窗口中，使用 aiocoap 客户端测试连接：

```bash
# 测试 sensor 资源
python -m aiocoap.cli.client coap://localhost/sensor

# 查看统计信息
python -m aiocoap.cli.client coap://localhost/stats
```

## ⚔️ 步骤 4: 运行攻击脚本

### 4.1 重放攻击测试

在第二个终端窗口中运行：

```bash
# 基础重放攻击（10秒，5请求/秒）
python coap_replay_attack.py coap://localhost/sensor --duration 10 --rate 5
```

**预期输出：**
```
============================================================
CoAP 重放攻击开始
============================================================
目标: coap://localhost/sensor
方法: GET
持续时间: 10 秒
速率: 5 请求/秒
============================================================
正在捕获原始请求: coap://localhost/sensor
✓ 成功捕获请求 - 响应码: 2.05 Content
  Token: 1a2b3c4d
  Payload: {"temperature": 22.5, "humidity": 60, "timestamp...

开始重放攻击，持续 10 秒...
已发送 10 个重放请求 (成功: 10, 失败: 0)
已发送 20 个重放请求 (成功: 20, 失败: 0)
...
```

同时观察服务器终端，你会看到请求统计：

```
📊 统计: 25 请求/5秒, 总计: 51
```

### 4.2 泛洪攻击测试

```bash
# 基础泛洪攻击（10秒，20请求/秒）
python coap_flood_attack.py coap://localhost/sensor --duration 10 --rate 20
```

**预期输出：**
```
============================================================
CoAP 泛洪攻击开始
============================================================
目标: coap://localhost/sensor
方法: GET
持续时间: 10 秒
速率: 20 请求/秒
最大并发: 10
随机负载: 否
============================================================

开始泛洪攻击，持续 10 秒...
进度: 50 请求 (成功: 50, 失败: 0)
进度: 100 请求 (成功: 100, 失败: 0)
进度: 150 请求 (成功: 150, 失败: 0)
进度: 200 请求 (成功: 200, 失败: 0)
...
```

### 4.3 高级测试场景

**场景 1: 高速率重放攻击**
```bash
python coap_replay_attack.py coap://localhost/sensor -d 30 -r 50
```

**场景 2: POST 方法泛洪攻击**
```bash
python coap_flood_attack.py coap://localhost/data -m POST -d 20 -r 30 --random-payload --payload-size 200
```

**场景 3: 高并发泛洪攻击**
```bash
python coap_flood_attack.py coap://localhost/sensor -d 60 -r 100 -c 30
```

## 📊 步骤 5: 查看服务器统计

攻击完成后，查看服务器统计信息：

```bash
python -m aiocoap.cli.client coap://localhost/stats
```

**示例输出：**
```json
{
  "total_requests": 1523,
  "uptime_seconds": 125.45,
  "requests_per_second": 12.14,
  "methods": {
    "GET": 1200,
    "POST": 323
  },
  "paths": {
    "/sensor": 1200,
    "/data": 323
  }
}
```

## 🛑 步骤 6: 停止测试

1. 在攻击脚本终端按 `Ctrl+C` 停止攻击
2. 在服务器终端按 `Ctrl+C` 停止服务器

服务器会显示最终统计：

```
============================================================
最终统计
============================================================
总请求数: 1523
运行时间: 125.45 秒
平均速率: 12.14 请求/秒
方法分布: {'GET': 1200, 'POST': 323}
路径分布: {'/sensor': 1200, '/data': 323}
============================================================
```

## 🔬 实验建议

### 实验 1: 测试服务器负载能力

逐步增加攻击强度，观察服务器性能：

```bash
# 低强度
python coap_flood_attack.py coap://localhost/sensor -d 30 -r 10

# 中强度
python coap_flood_attack.py coap://localhost/sensor -d 30 -r 50

# 高强度
python coap_flood_attack.py coap://localhost/sensor -d 30 -r 100
```

### 实验 2: 测试重放攻击检测

观察服务器是否能检测到重复的 token：

```bash
# 运行重放攻击
python coap_replay_attack.py coap://localhost/sensor -d 20 -r 10

# 检查服务器日志，看是否有重复请求
```

### 实验 3: 混合攻击测试

同时运行多个攻击脚本（在不同终端）：

```bash
# 终端 2
python coap_replay_attack.py coap://localhost/sensor -d 60 -r 20

# 终端 3
python coap_flood_attack.py coap://localhost/data -m POST -d 60 -r 30
```

## 📈 性能监控

在测试期间，可以使用以下工具监控系统性能：

**Windows:**
```powershell
# 任务管理器
taskmgr

# 或使用 PowerShell
Get-Process python | Select-Object CPU, WorkingSet
```

**Linux/Mac:**
```bash
# 监控 CPU 和内存
top -p $(pgrep -f python)

# 或使用 htop
htop
```

```bash
 python coap_flood_attack.py --help
usage: coap_flood_attack.py [-h] [-m {GET,POST,PUT,DELETE}] [-d DURATION] [-r RATE] [-c CONCURRENT] [--random-payload] [--payload-size PAYLOAD_SIZE] target

CoAP泛洪攻击工具 - 向目标发送大量CoAP请求

positional arguments:
  target                目标CoAP URI (例如: coap://localhost/sensor)

options:
  -h, --help            show this help message and exit
  -m {GET,POST,PUT,DELETE}, --method {GET,POST,PUT,DELETE}
                        CoAP方法 (默认: GET)
  -d DURATION, --duration DURATION
                        攻击持续时间(秒) (默认: 30, 最大: 300)
  -r RATE, --rate RATE  每秒请求数 (默认: 20, 最大: 200)
  -c CONCURRENT, --concurrent CONCURRENT
                        最大并发请求数 (默认: 10, 最大: 50)
  --random-payload      使用随机生成的负载
  --payload-size PAYLOAD_SIZE
                        负载大小(字节) (默认: 100, 最大: 1024)

示例:
  # 基本泛洪攻击
  python coap_flood_attack.py coap://localhost/sensor

  # 高速率攻击，持续60秒
  python coap_flood_attack.py coap://localhost/sensor -d 60 -r 50

  # 使用随机负载的POST攻击
  python coap_flood_attack.py coap://localhost/data -m POST --random-payload --payload-size 500
```

## ⚠️ 常见问题

**Q: 攻击脚本报错 "Connection refused"**
- A: 确保测试服务器正在运行
- A: 检查端口 5683 是否被占用

**Q: 成功率很低（<50%）**
- A: 降低请求速率 (`-r` 参数)
- A: 减少并发数 (`-c` 参数)
- A: 检查系统资源是否充足

**Q: 服务器无响应**
- A: 攻击强度可能过高，重启服务器
- A: 降低攻击参数重新测试

**Q: Windows 防火墙阻止连接**
- A: 允许 Python 通过防火墙
- A: 或临时禁用防火墙进行测试

## 📚 下一步

- 阅读 [ATTACK_SCRIPTS_README.md](ATTACK_SCRIPTS_README.md) 了解详细参数
- 修改脚本以适应你的测试需求
- 实现防御机制并测试其有效性

## 🔒 安全提醒

**再次强调：这些工具仅用于授权的安全测试。未经授权的攻击是违法的！**

