# CoAP Token 重放攻击演示

## 文件说明

- `server.py` - CoAP 服务器 (端口 5683)
- `attacker.py` - MITM 代理 (端口 5684)
- `client.py` - 演示客户端

## 运行步骤

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

**终端 3 - 运行客户端：**
```bash
cd coap_token_replay
uv run python client.py
```

## 攻击原理

1. 客户端发送请求 #1（Token: aabb）
2. 攻击者拦截响应，缓存不转发
3. 客户端发送请求 #2（相同 Token: aabb）
4. 服务器响应 #2，攻击者正常转发
5. 5秒后，攻击者重放请求 #1 的旧响应
6. 客户端收到两个响应：一个是正确的，一个是重放的旧响应
