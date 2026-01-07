# CoAP 攻击工具集总结

## 📁 项目文件

本项目包含以下文件：

### 核心攻击脚本
1. **`coap_replay_attack.py`** - CoAP 重放攻击脚本
2. **`coap_flood_attack.py`** - CoAP 泛洪攻击脚本
3. **`test_server.py`** - 测试用 CoAP 服务器

### 文档
4. **`ATTACK_SCRIPTS_README.md`** - 详细使用文档
5. **`QUICKSTART.md`** - 快速开始指南
6. **`ATTACK_TOOLS_SUMMARY.md`** - 本文件

## 🎯 功能概览

### 1. 重放攻击 (Replay Attack)

**原理：** 捕获合法的 CoAP 请求并重复发送，测试服务器是否能正确处理重复请求。

**关键特性：**
- ✅ 自动捕获原始请求
- ✅ 保持相同的 token 进行重放
- ✅ 可配置速率和持续时间
- ✅ 实时统计成功/失败率
- ✅ 安全限制（最大 300 秒，100 请求/秒）

**典型用法：**
```bash
python coap_replay_attack.py coap://localhost/sensor --duration 10 --rate 5
```

### 2. 泛洪攻击 (Flood Attack)

**原理：** 向目标服务器发送大量请求，测试其负载能力和抗 DoS 能力。

**关键特性：**
- ✅ 高速率请求发送
- ✅ 可配置并发连接数
- ✅ 支持随机负载生成
- ✅ 多种 HTTP 方法支持
- ✅ 实时性能监控
- ✅ 安全限制（最大 300 秒，200 请求/秒，50 并发）

**典型用法：**
```bash
python coap_flood_attack.py coap://localhost/sensor --duration 10 --rate 20 --concurrent 10
```

### 3. 测试服务器

**功能：** 提供一个简单的 CoAP 服务器用于测试攻击脚本。

**特性：**
- ✅ 多个测试资源 (/sensor, /data, /stats)
- ✅ 实时请求统计
- ✅ 支持 GET/POST/PUT/DELETE 方法
- ✅ 自动日志记录

**启动方式：**
```bash
python test_server.py
```

## 🚀 快速开始

### 三步开始测试

```bash
# 步骤 1: 安装依赖
uv pip install aiocoap

# 步骤 2: 启动测试服务器（终端 1）
python test_server.py

# 步骤 3: 运行攻击脚本（终端 2）
python coap_replay_attack.py coap://localhost/sensor -d 10 -r 5
```

详细步骤请参考 [QUICKSTART.md](QUICKSTART.md)

## 📊 参数对照表

### 重放攻击参数

| 参数 | 简写 | 默认值 | 最大值 | 说明 |
|------|------|--------|--------|------|
| target | - | 必需 | - | 目标 URI |
| --method | -m | GET | - | CoAP 方法 |
| --payload | -p | None | - | 请求负载 |
| --duration | -d | 30 | 300 | 持续时间（秒） |
| --rate | -r | 10 | 100 | 请求速率（请求/秒） |

### 泛洪攻击参数

| 参数 | 简写 | 默认值 | 最大值 | 说明 |
|------|------|--------|--------|------|
| target | - | 必需 | - | 目标 URI |
| --method | -m | GET | - | CoAP 方法 |
| --duration | -d | 30 | 300 | 持续时间（秒） |
| --rate | -r | 20 | 200 | 请求速率（请求/秒） |
| --concurrent | -c | 10 | 50 | 最大并发数 |
| --random-payload | - | False | - | 使用随机负载 |
| --payload-size | - | 100 | 1024 | 负载大小（字节） |

## 🔬 测试场景示例

### 场景 1: 基础功能测试
```bash
# 低强度测试，验证脚本功能
python coap_replay_attack.py coap://localhost/sensor -d 5 -r 2
python coap_flood_attack.py coap://localhost/sensor -d 5 -r 5
```

### 场景 2: 中等强度测试
```bash
# 测试服务器在中等负载下的表现
python coap_replay_attack.py coap://localhost/sensor -d 30 -r 20
python coap_flood_attack.py coap://localhost/sensor -d 30 -r 50 -c 20
```

### 场景 3: 高强度压力测试
```bash
# 测试服务器极限性能
python coap_replay_attack.py coap://localhost/sensor -d 60 -r 50
python coap_flood_attack.py coap://localhost/sensor -d 60 -r 100 -c 30
```

### 场景 4: POST 方法测试
```bash
# 测试 POST 请求处理
python coap_flood_attack.py coap://localhost/data -m POST -d 20 -r 30 --random-payload --payload-size 500
```

### 场景 5: 混合攻击
```bash
# 同时运行多个攻击（不同终端）
# 终端 2:
python coap_replay_attack.py coap://localhost/sensor -d 60 -r 20

# 终端 3:
python coap_flood_attack.py coap://localhost/data -m POST -d 60 -r 30
```

## 📈 预期结果

### 正常情况
- **成功率**: > 95%
- **服务器响应**: 正常返回 2.05 Content 或相应状态码
- **系统资源**: CPU < 50%, 内存稳定

### 异常情况（可能表明问题）
- **成功率**: < 50%
- **服务器响应**: 超时或错误增多
- **系统资源**: CPU > 90%, 内存持续增长

## 🛡️ 安全特性

### 内置保护机制
1. **时间限制**: 最大运行 5 分钟
2. **速率限制**: 防止过高的请求速率
3. **并发限制**: 防止资源耗尽
4. **超时控制**: 避免无限等待
5. **异常处理**: 优雅处理错误

### 使用建议
- ⚠️ 仅在授权环境中使用
- ⚠️ 从低强度开始逐步增加
- ⚠️ 监控系统资源使用
- ⚠️ 保存测试日志用于分析

## 🔧 技术细节

### 依赖库
- **aiocoap**: CoAP 协议实现
- **asyncio**: 异步 I/O 支持
- **Python 3.11+**: 推荐版本

### 架构设计
```
┌─────────────────┐
│  攻击脚本       │
│  (Client)       │
└────────┬────────┘
         │ CoAP Requests
         │ (UDP/5683)
         ▼
┌─────────────────┐
│  测试服务器     │
│  (Server)       │
└─────────────────┘
```

### 工作流程

**重放攻击：**
1. 发送原始请求并捕获
2. 提取 token 和 payload
3. 重复发送相同的请求
4. 统计成功/失败率

**泛洪攻击：**
1. 创建大量并发任务
2. 批量发送请求
3. 速率控制和并发限制
4. 实时统计和报告

## 📚 相关文档

- [详细使用文档](ATTACK_SCRIPTS_README.md) - 完整的参数说明和示例
- [快速开始指南](QUICKSTART.md) - 分步教程
- [aiocoap 官方文档](https://aiocoap.readthedocs.io/) - 库文档

## ⚖️ 法律声明

**重要提示：**

这些工具仅用于：
- ✅ 教育和学习目的
- ✅ 授权的安全测试
- ✅ 自己系统的性能测试

**禁止用于：**
- ❌ 未经授权的系统攻击
- ❌ 恶意破坏
- ❌ 任何非法活动

使用者需对自己的行为负全部法律责任。

## 📞 支持

如有问题或建议，请参考：
- aiocoap 项目: https://github.com/chrysn/aiocoap
- CoAP 规范: RFC 7252

---

**版本**: 1.0  
**最后更新**: 2024-12-23  
**许可证**: MIT

