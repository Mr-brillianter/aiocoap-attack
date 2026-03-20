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
成功了会观察到client第一次超时，第二次正常，等待时受到第一次的延迟响应

## 攻击原理

1. 客户端发送请求 #1（Token: aabb）
2. 攻击者拦截响应，缓存不转发
3. 客户端发送请求 #2（相同 Token: aabb）
4. 服务器响应 #2，攻击者正常转发
5. 5秒后，攻击者重放请求 #1 的旧响应
6. 客户端收到两个响应：一个是正确的，一个是重放的旧响应

## 异常处理
### 无法绑定端口
可能程序变僵尸了：
```bash
ps aux | grep attacker
ps aux | grep server
ps aux | grep client
kill -9 <PID>
```
## 抓包方法

需要过滤 **5683** 和 **5684** 两个端口：

| 端口 | 通信路径 | 说明 |
|------|----------|------|
| **5684** | 客户端 → 攻击者 | 客户端请求发往攻击者的 MITM 代理端口 |
| **5683** | 攻击者 → 服务器 | 攻击者将请求转发给真实的 CoAP 服务器 |

### tcpdump 抓包命令
```bash
sudo tcpdump -i lo port 5683 or port 5684 -w coap_attack_capture.pcap
```

### tshark 抓包命令
```bash
tshark -i lo -f "port 5683 or port 5684" -w coap_attack_capture.pcap
```

## 持续模拟攻击的方法

python run_attack.py

启动 python attacker.py（挂起）
等待 0.5 秒
运行 python client.py
client 完成后自动关闭 attacker

## 完整抓包实验步骤（4个终端）

| 终端 | 命令 |
|------|------|
| 1 | `sudo tcpdump -i lo port 5683 or port 5684 -w capture.pcap` |
| 2 | `cd coap_token_replay && uv run python server.py` |
| 3 | `while true; do python run_attack.py; sleep 1; done` |

## 关键分析点

在 Wireshark 中查看 pcap 文件时，关注：
1. **Token** - 是否为固定值 `aabb`
2. **Message ID** - 两次请求的 MID 是否重复
3. **时间戳 payload** - 重放的旧响应时间戳与新响应不同
4. **重放延迟** - [`attacker.py:95`](coap_token_replay/attacker.py:95) 中设置为 5 秒延迟后重放