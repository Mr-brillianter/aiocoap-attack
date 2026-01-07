#!/usr/bin/env python3
"""
直接测试服务器（绕过攻击者）
"""
import socket
import struct
import time

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

def main():
    print("="*70)
    print("直接测试服务器（绕过攻击者）")
    print("="*70)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)
    
    # 直接连接到服务器（5683），不通过攻击者
    server_addr = ("127.0.0.1", 5683)
    
    token = b'\xAA\xBB\xCC\xDD'
    msg_id = 2001
    
    print(f"\n发送请求到服务器 ({server_addr[0]}:{server_addr[1]})")
    print(f"Token: {token.hex()}")
    print(f"Message ID: {msg_id}")
    
    request = create_coap_get_request("time", token, msg_id)
    print(f"请求数据: {request.hex()}")
    
    sock.sendto(request, server_addr)
    print("✅ 请求已发送")
    
    print("\n等待响应...")
    try:
        data, addr = sock.recvfrom(4096)
        print(f"✅ 收到响应！")
        print(f"来源: {addr[0]}:{addr[1]}")
        print(f"响应数据: {data.hex()}")
        print(f"长度: {len(data)} 字节")
        
        # 解析响应
        if len(data) >= 4:
            byte0 = data[0]
            token_length = byte0 & 0x0F
            code = data[1]
            resp_msg_id = struct.unpack('!H', data[2:4])[0]
            resp_token = data[4:4+token_length] if token_length > 0 else b''
            
            print(f"\n解析响应:")
            print(f"Token: {resp_token.hex()}")
            print(f"Code: {(code >> 5) & 0x07}.{code & 0x1F:02d}")
            print(f"Message ID: {resp_msg_id}")
            
            # 查找 payload
            i = 4 + token_length
            while i < len(data):
                if data[i] == 0xFF:
                    payload = data[i+1:]
                    print(f"Payload: {payload.decode('utf-8', errors='ignore')}")
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
            
    except socket.timeout:
        print("❌ 超时")
    
    sock.close()
    print("\n" + "="*70)
    print("检查服务器日志，看看它记录的 Token 是什么")
    print("="*70)

if __name__ == "__main__":
    main()

