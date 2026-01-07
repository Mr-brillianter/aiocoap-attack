# CoAP Token Replay Attack - Usage Guide

## Quick Start

### 1. Test the Installation

First, verify that all dependencies are working:

```bash
cd coap_token_replay
python test_attacker_import.py
```

You should see:
```
============================================================
All tests passed! ✓
============================================================
```

### 2. Run the Attacker Script

#### On Windows (PowerShell as Administrator):

```powershell
# Make sure you're in the virtual environment
.\.venv\Scripts\activate.ps1

# Run the attacker
python coap_token_replay\attacker.py
```

#### On Linux/Mac:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run with sudo for packet capture
sudo python coap_token_replay/attacker.py
```

### 3. Select Network Interface

The script will show available network interfaces:

```
可用的网络接口:
  1. \Device\NPF_{5DA2537F-06D5-4EED-BF23-992A93D6D7EB}
  2. \Device\NPF_{E1C7B1CD-6341-41A8-ADFD-1E7C26D5A38E}
  ...
  9. \Device\NPF_Loopback ← 推荐用于本地测试

请选择网络接口 (1-9, 直接回车使用默认):
```

**For local testing (server and client on same machine):**
- Choose the **Loopback** interface (usually marked with "Loopback" or "lo")
- On Windows: `\Device\NPF_Loopback`
- On Linux/Mac: `lo`

**For network testing:**
- Choose the interface connected to your network
- Press Enter to use the default interface

### 4. Choose Attack Mode

After selecting the interface, you'll see a menu:

```
选择攻击模式:
1. 自动嗅探和攻击    - Automatically sniff and replay CoAP responses
2. 查看攻击步骤说明   - View attack methodology explanation
3. 手动构造攻击数据包 - Show example of manual packet construction
```

## Attack Modes Explained

### Mode 1: Automatic Sniffing and Attack

This mode:
- Monitors network traffic for CoAP packets
- Captures ACK responses from the server
- Delays and replays them to demonstrate token reuse vulnerability

**How it works:**
1. The script starts sniffing on the network interface
2. When a CoAP ACK response is detected, it's captured
3. After 5 seconds, the old response is replayed
4. This simulates an attacker replaying old responses with reused tokens

**To test this:**
1. Start the attacker in Mode 1
2. In another terminal, run a CoAP client that makes requests
3. Watch the logs to see captured and replayed packets

### Mode 2: View Attack Steps

This mode displays a step-by-step explanation of how the token replay attack works:

```
1. 攻击者监听客户端和服务器之间的通信
2. 客户端发送请求A（Token: T）
3. 服务器响应A'（Token: T），攻击者捕获并延迟该响应
4. 客户端以为失败，用相同Token T发送请求B
5. 服务器正常响应B'（Token: T），客户端处理
6. 攻击者重放旧的响应A'（Token: T）
7. 客户端无法区分，将旧响应A'关联到请求B
```

### Mode 3: Manual Packet Construction

This mode shows you how to manually construct a malicious CoAP packet:

```python
fake_response = (IP(src="127.0.0.1", dst="127.0.0.1") /
                UDP(sport=5683, dport=5684) /
                CoAP(type="ACK", code=69, token=b'fixed123') /
                Raw(load=b"Malicious response: old data"))
```

You can use this as a template to create custom attack packets.

## Prerequisites

### Windows
1. **Install Npcap**: Download from https://npcap.com/
   - During installation, make sure to check "Install Npcap in WinPcap API-compatible Mode"
2. **Run as Administrator**: Right-click PowerShell → "Run as Administrator"

### Linux
1. **Install dependencies**:
   ```bash
   sudo apt-get install tcpdump libpcap-dev
   ```
2. **Run with sudo**: Required for raw packet capture

### Mac
1. **Install dependencies**:
   ```bash
   brew install libpcap
   ```
2. **Run with sudo**: Required for raw packet capture

## Troubleshooting

### "No module named 'scapy.contrib.coap'"
- Make sure you've activated the virtual environment
- Reinstall scapy: `pip install --upgrade scapy`

### "Permission denied" or "Operation not permitted"
- On Windows: Run PowerShell as Administrator
- On Linux/Mac: Use `sudo python attacker.py`

### "The transport can not be bound to any-address"
- This is from the server.py, not attacker.py
- Make sure server.py has been fixed with `bind=("127.0.0.1", None)`

### No packets captured
- Check that the network interface is correct
- Verify that CoAP traffic is actually flowing on the network
- Try using a different interface from the list shown at startup

## Example Workflow

1. **Terminal 1** - Start the CoAP server:
   ```bash
   python server.py
   ```

2. **Terminal 2** - Start the attacker (as admin/sudo):
   ```bash
   sudo python coap_token_replay/attacker.py
   # Choose option 1
   ```

3. **Terminal 3** - Run a CoAP client:
   ```bash
   python coap_token_replay/client.py
   ```

4. Watch the attacker terminal to see:
   - Captured CoAP packets
   - Replayed responses
   - Token reuse demonstration

## Safety Note

This tool is for **educational and research purposes only**. Only use it on networks you own or have explicit permission to test. Unauthorized network sniffing and packet injection may be illegal in your jurisdiction.

