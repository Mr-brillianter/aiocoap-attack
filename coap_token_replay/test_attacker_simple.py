#!/usr/bin/env python3
"""
简单测试攻击者是否正常工作
"""
import socket
import struct
import time

def create_coap_request(token=b'\x1a\x2b\x3c\x4d'):
    """创建一个简单的 CoAP GET 请求"""
    # CoAP 头部: Ver=1, Type=0(CON), TKL=4, Code=1(GET), MsgID=12345
    header = bytes([
        0b01000100,  # Ver=1, Type=0, TKL=4
        0x01,        # Code=0.01 (GET)
        0x30, 0x39,  # Message ID = 12345
    ])
    
    # Token
    data = header + token
    
    # 添加 Uri-Path 选项 (Option 11, value="time")
    # Option Delta=11, Length=4
    option_header = bytes([0xB4])  # Delta=11, Length=4
    option_value = b'time'
    data += option_header + option_value
    
    # Payload marker (0xFF) 和空 payload
    # data += b'\xFF'
    
    return data

def main():
    print("="*70)
    print("测试攻击者是否正常工作")
    print("="*70)
    
    # 创建 UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)
    
    # 攻击者地址
    attacker_addr = ("127.0.0.1", 5684)
    
    # 创建 CoAP 请求
    request = create_coap_request()
    
    print(f"\n1. 发送请求到攻击者 ({attacker_addr[0]}:{attacker_addr[1]})")
    print(f"   请求数据: {request.hex()}")
    
    # 发送请求
    sock.sendto(request, attacker_addr)
    print("   ✅ 请求已发送")
    
    # 等待响应
    print("\n2. 等待响应...")
    try:
        data, addr = sock.recvfrom(4096)
        print(f"   ✅ 收到响应！")
        print(f"   来源: {addr[0]}:{addr[1]}")
        print(f"   数据: {data.hex()}")
        print(f"   长度: {len(data)} 字节")
        
        # 解析响应
        if len(data) >= 4:
            byte0 = data[0]
            code = data[1]
            msg_id = struct.unpack('!H', data[2:4])[0]
            
            print(f"\n3. 解析响应:")
            print(f"   版本: {(byte0 >> 6) & 0x03}")
            print(f"   类型: {(byte0 >> 4) & 0x03}")
            print(f"   Token 长度: {byte0 & 0x0F}")
            print(f"   代码: {(code >> 5) & 0x07}.{code & 0x1F:02d}")
            print(f"   消息ID: {msg_id}")
            
    except socket.timeout:
        print("   ❌ 超时！没有收到响应")
        print("\n可能的原因:")
        print("  1. 攻击者没有启动")
        print("  2. 服务器没有启动")
        print("  3. 端口配置错误")
    
    sock.close()
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

