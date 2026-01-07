#!/usr/bin/env python3
"""
CoAP Token 重用攻击 - 简单 MITM 演示
使用原始 socket，确保流量通过攻击者

运行步骤:
1. 启动服务器: python server.py
2. 启动攻击者: python attacker.py
3. 运行此演示: python demo_mitm_simple.py
"""
import socket
import struct
import time

def create_coap_get_request(path="time", token=b'\xAA\xBB\xCC\xDD', msg_id=1):
    """创建 CoAP GET 请求"""
    # CoAP 头部: Ver=1, Type=0(CON), TKL=len(token), Code=1(GET), MsgID
    token_length = len(token)
    header = bytes([
        0b01000000 | token_length,  # Ver=1, Type=0(CON), TKL
        0x01,                        # Code=0.01 (GET)
    ]) + struct.pack('!H', msg_id)  # Message ID
    
    # Token
    data = header + token
    
    # Uri-Path 选项
    path_bytes = path.encode('utf-8')
    path_len = len(path_bytes)
    
    # Option 11 (Uri-Path), Delta=11, Length=path_len
    if path_len < 13:
        option_header = bytes([(11 << 4) | path_len])
    else:
        option_header = bytes([0xBD, path_len - 13])
    
    data += option_header + path_bytes
    
    return data

def parse_coap_response(data):
    """解析 CoAP 响应"""
    if len(data) < 4:
        return None
    
    byte0 = data[0]
    version = (byte0 >> 6) & 0x03
    msg_type = (byte0 >> 4) & 0x03
    token_length = byte0 & 0x0F
    
    code = data[1]
    msg_id = struct.unpack('!H', data[2:4])[0]
    
    token = data[4:4+token_length] if token_length > 0 else b''
    
    # 查找 payload
    payload_start = 4 + token_length
    payload = b''
    
    # 跳过选项，查找 payload marker (0xFF)
    i = payload_start
    while i < len(data):
        if data[i] == 0xFF:
            payload = data[i+1:]
            break
        # 跳过选项
        option_delta = (data[i] >> 4) & 0x0F
        option_length = data[i] & 0x0F
        i += 1
        if option_delta == 13:
            i += 1
        elif option_delta == 14:
            i += 2
        if option_length == 13:
            i += 1
        elif option_length == 14:
            i += 2
        i += option_length
    
    return {
        'version': version,
        'type': msg_type,
        'token': token,
        'code': code,
        'msg_id': msg_id,
        'payload': payload
    }

def main():
    print("\n" + "="*70)
    print("CoAP Token 重用攻击 - 简单 MITM 演示")
    print("="*70)
    print()
    print("📋 攻击流程:")
    print("  1. 客户端发送请求 A → 攻击者 → 服务器")
    print("  2. 服务器响应 A' → 攻击者（缓存，不转发）")
    print("  3. 客户端超时，发送请求 B（相同 Token）→ 攻击者 → 服务器")
    print("  4. 服务器响应 B' → 攻击者 → 客户端")
    print("  5. 攻击者延迟后重放 A' → 客户端")
    print("="*70)
    print()
    
    # 创建 socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(12.0)  # 12 秒超时
    
    # 攻击者地址（不是服务器！）
    attacker_addr = ("127.0.0.1", 5684)
    
    # 使用相同的 Token
    token = b'\xAA\xBB\xCC\xDD'
    
    print("🚀 发送第一个请求...")
    request1 = create_coap_get_request("time", token, msg_id=1001)
    print(f"   Token: {token.hex()}")
    print(f"   目标: {attacker_addr[0]}:{attacker_addr[1]} (攻击者)")
    sock.sendto(request1, attacker_addr)
    print("   ✅ 请求已发送")
    
    print("\n⏳ 等待响应（预期：超时，因为攻击者会缓存第一个响应）...")
    try:
        data, addr = sock.recvfrom(4096)
        print(f"   ⚠️  收到响应（不应该！）")
        print(f"   来源: {addr[0]}:{addr[1]}")
        resp = parse_coap_response(data)
        if resp:
            print(f"   Payload: {resp['payload'].decode('utf-8', errors='ignore')}")
    except socket.timeout:
        print("   ✅ 超时（预期行为）")
    
    print("\n⏳ 等待 2 秒...")
    time.sleep(2)
    
    print("\n🚀 发送第二个请求（相同 Token）...")
    request2 = create_coap_get_request("time", token, msg_id=1002)
    print(f"   Token: {token.hex()}")
    print(f"   目标: {attacker_addr[0]}:{attacker_addr[1]} (攻击者)")
    sock.sendto(request2, attacker_addr)
    print("   ✅ 请求已发送")
    
    print("\n⏳ 等待响应...")
    try:
        data, addr = sock.recvfrom(4096)
        print(f"   ✅ 收到响应！")
        print(f"   来源: {addr[0]}:{addr[1]}")
        resp = parse_coap_response(data)
        if resp:
            print(f"   Token: {resp['token'].hex()}")
            print(f"   Code: {(resp['code'] >> 5) & 0x07}.{resp['code'] & 0x1F:02d}")
            print(f"   Payload: {resp['payload'].decode('utf-8', errors='ignore')}")
    except socket.timeout:
        print("   ❌ 超时")
    
    print("\n⏳ 等待攻击者重放旧响应（5 秒）...")
    time.sleep(6)
    
    print("\n" + "="*70)
    print("✅ 演示完成！")
    print("="*70)
    print()
    print("📊 观察攻击者的日志，查看:")
    print("  - 第一个请求的响应被缓存")
    print("  - 第二个请求的响应被转发")
    print("  - 延迟后重放第一个响应")
    print("="*70)
    
    sock.close()

if __name__ == "__main__":
    main()

