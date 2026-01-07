#!/usr/bin/env python3
"""
完整的 MITM 攻击演示 - 自动启动所有组件

这个脚本会:
1. 启动服务器
2. 启动攻击者
3. 运行客户端演示
4. 清理所有进程
"""
import asyncio
import subprocess
import sys
import time
import socket
import struct

async def start_server():
    """启动服务器"""
    print("🚀 启动服务器...")
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "server.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await asyncio.sleep(2)  # 等待服务器启动
    print("   ✅ 服务器已启动")
    return proc

async def start_attacker():
    """启动攻击者"""
    print("🚀 启动攻击者...")
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "attacker.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await asyncio.sleep(2)  # 等待攻击者启动
    print("   ✅ 攻击者已启动")
    return proc

def create_coap_get_request(path="time", token=b'\xAA\xBB\xCC\xDD', msg_id=1):
    """创建 CoAP GET 请求"""
    token_length = len(token)
    header = bytes([
        0b01000000 | token_length,
        0x01,
    ]) + struct.pack('!H', msg_id)
    
    data = header + token
    
    path_bytes = path.encode('utf-8')
    path_len = len(path_bytes)
    
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
    token_length = byte0 & 0x0F
    code = data[1]
    msg_id = struct.unpack('!H', data[2:4])[0]
    token = data[4:4+token_length] if token_length > 0 else b''
    
    payload_start = 4 + token_length
    payload = b''
    
    i = payload_start
    while i < len(data):
        if data[i] == 0xFF:
            payload = data[i+1:]
            break
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
        'token': token,
        'code': code,
        'msg_id': msg_id,
        'payload': payload
    }

async def run_client_demo():
    """运行客户端演示"""
    print("\n" + "="*70)
    print("📱 客户端演示")
    print("="*70)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(12.0)
    
    attacker_addr = ("127.0.0.1", 5684)
    token = b'\xAA\xBB\xCC\xDD'
    
    print("\n🚀 发送第一个请求...")
    request1 = create_coap_get_request("time", token, msg_id=1001)
    print(f"   Token: {token.hex()}")
    sock.sendto(request1, attacker_addr)
    print("   ✅ 请求已发送")
    
    print("\n⏳ 等待响应（预期：超时）...")
    try:
        data, addr = sock.recvfrom(4096)
        print(f"   ⚠️  收到响应（不应该！）")
    except socket.timeout:
        print("   ✅ 超时（预期行为）")
    
    await asyncio.sleep(2)
    
    print("\n🚀 发送第二个请求（相同 Token）...")
    request2 = create_coap_get_request("time", token, msg_id=1002)
    print(f"   Token: {token.hex()}")
    sock.sendto(request2, attacker_addr)
    print("   ✅ 请求已发送")
    
    print("\n⏳ 等待响应...")
    try:
        data, addr = sock.recvfrom(4096)
        print(f"   ✅ 收到响应！")
        resp = parse_coap_response(data)
        if resp:
            print(f"   Token: {resp['token'].hex()}")
            print(f"   Payload: {resp['payload'].decode('utf-8', errors='ignore')}")
    except socket.timeout:
        print("   ❌ 超时")
    
    print("\n⏳ 等待攻击者重放旧响应（6 秒）...")
    await asyncio.sleep(6)
    
    sock.close()
    print("\n" + "="*70)
    print("✅ 演示完成！")
    print("="*70)

async def main():
    """主函数"""
    print("\n" + "="*70)
    print("CoAP Token 重用攻击 - 完整演示")
    print("="*70)
    
    server_proc = None
    attacker_proc = None
    
    try:
        # 启动服务器和攻击者
        server_proc = await start_server()
        attacker_proc = await start_attacker()
        
        # 运行客户端演示
        await run_client_demo()
        
    finally:
        # 清理
        print("\n🧹 清理进程...")
        if attacker_proc:
            attacker_proc.terminate()
            await attacker_proc.wait()
            print("   ✅ 攻击者已停止")
        if server_proc:
            server_proc.terminate()
            await server_proc.wait()
            print("   ✅ 服务器已停止")

if __name__ == "__main__":
    asyncio.run(main())

