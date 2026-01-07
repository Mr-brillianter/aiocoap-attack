# 当前状态和使用指南

## ✅ 已完成

1. **MITM 攻击者实现** (`attacker.py`)
   - ✅ UDP 代理功能
   - ✅ CoAP 消息解析
   - ✅ 请求转发
   - ✅ 响应缓存
   - ✅ 延迟重放

2. **服务器更新** (`server.py`)
   - ✅ 添加 `/time` 路径
   - ✅ 支持多个资源

3. **演示脚本**
   - ✅ `demo_mitm_attack.py` - 使用 aiocoap
   - ✅ `demo_mitm_simple.py` - 使用原始 socket（推荐）
   - ✅ `test_attacker_simple.py` - 简单测试

4. **文档**
   - ✅ `MITM_ATTACK_GUIDE.md` - 使用指南
   - ✅ `TROUBLESHOOTING.md` - 故障排除
   - ✅ `CURRENT_STATUS.md` - 本文件

## ⚠️ 已知问题

### 问题 1: aiocoap 客户端绕过攻击者

**症状**: 使用 `demo_mitm_attack.py` 时，客户端直接收到响应，攻击者没有成功拦截。

**原因**: aiocoap 库的内部实现可能会直接连接到服务器，绕过攻击者。

**解决方案**: 使用 `demo_mitm_simple.py`，它使用原始 socket，确保流量通过攻击者。

### 问题 2: logger.info() 错误

**症状**: `TypeError: Logger.info() missing 1 required positional argument: 'msg'`

**解决方案**: 已修复，使用 `logger.info("")` 而不是 `logger.info()`。

## 🚀 推荐使用方法

### 方法 1: 使用原始 Socket（推荐 ⭐）

这是最可靠的方法，确保流量通过攻击者。

```bash
# 终端 1: 启动服务器
cd coap_token_replay
uv run python server.py

# 终端 2: 启动攻击者
cd coap_token_replay
uv run python attacker.py

# 终端 3: 运行简单演示
cd coap_token_replay
uv run python demo_mitm_simple.py
```

**预期输出**:

**客户端**:
```
🚀 发送第一个请求...
   Token: aabbccdd
   ✅ 请求已发送

⏳ 等待响应（预期：超时，因为攻击者会缓存第一个响应）...
   ✅ 超时（预期行为）

🚀 发送第二个请求（相同 Token）...
   Token: aabbccdd
   ✅ 请求已发送

⏳ 等待响应...
   ✅ 收到响应！
   Payload: 当前时间: 2026-01-03 13:30:00 (请求#2)
```

**攻击者**:
```
======================================================================
📤 [请求 #1] 客户端 → 攻击者
   Token: aabbccdd
📨 [转发] 攻击者 → 服务器
======================================================================

======================================================================
📥 [响应 #1] 服务器 → 攻击者
   Token: aabbccdd
🎯 [攻击] 捕获第一个请求的响应，缓存不转发！
======================================================================

======================================================================
📤 [请求 #2] 客户端 → 攻击者
   Token: aabbccdd
📨 [转发] 攻击者 → 服务器
======================================================================

======================================================================
📥 [响应 #2] 服务器 → 攻击者
   Token: aabbccdd
📨 [转发] 攻击者 → 客户端
======================================================================

======================================================================
💣 [攻击] 重放旧响应！
   Token: aabbccdd
   ✅ 旧响应已重放！
======================================================================
```

### 方法 2: 简单测试

快速测试攻击者是否正常工作：

```bash
# 终端 1: 启动服务器
uv run python server.py

# 终端 2: 启动攻击者
uv run python attacker.py

# 终端 3: 运行测试
uv run python test_attacker_simple.py
```

## 📊 架构说明

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Client    │────────▶│   Attacker   │────────▶│   Server    │
│  (Socket)   │         │ 127.0.0.1    │         │ 127.0.0.1   │
│             │         │ :5684        │         │ :5683       │
└─────────────┘         └──────────────┘         └─────────────┘
      ▲                        │                        
      │                        │                        
      └────────────────────────┘                        
           (延迟重放旧响应)
```

### 关键点

1. **客户端必须发送到攻击者端口（5684）**
2. **攻击者转发到服务器端口（5683）**
3. **服务器响应到攻击者端口（5684）**
4. **攻击者控制是否转发响应**

## 🎯 攻击流程

```
T0:  Client → Attacker (5684): 请求 A (Token: T)
T1:  Attacker → Server (5683): 转发请求 A
T2:  Server → Attacker (5684): 响应 A' (Token: T)
T3:  Attacker: 🎯 缓存 A'，不转发
T4:  Client: ⏰ 超时
T5:  Client → Attacker (5684): 请求 B (Token: T, 相同!)
T6:  Attacker → Server (5683): 转发请求 B
T7:  Server → Attacker (5684): 响应 B' (Token: T)
T8:  Attacker → Client: ✅ 转发 B'
T9:  Client: 处理 B'
T10: Attacker → Client: 💣 重放 A' (Token: T)
T11: Client: 收到旧响应 A'
```

## 🔧 调试

### 启用调试日志

修改 `attacker.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 查看数据包

攻击者会记录所有收到的数据包：

```
收到数据包: 来自 127.0.0.1:xxxxx, 长度 xx
  → 判断为客户端请求（端口 xxxxx != 5683）
```

## 📚 相关文档

- `MITM_ATTACK_GUIDE.md` - 详细使用指南
- `TROUBLESHOOTING.md` - 故障排除
- `README.md` - 项目总览

## 🎉 总结

**当前状态**: ✅ 功能完整，使用原始 socket 可以正常工作

**推荐使用**: `demo_mitm_simple.py`

**适用场景**:
- ✅ 教学演示
- ✅ 理解 MITM 攻击
- ✅ 学习 CoAP 协议
- ✅ 演示 Token 重用漏洞

