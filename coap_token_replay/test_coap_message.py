#!/usr/bin/env python3
"""
测试 CoAP 消息生成和解析
"""
import struct

def create_coap_get_request(path="time", token=b'\xAA\xBB\xCC\xDD', msg_id=1):
    """创建 CoAP GET 请求"""
    token_length = len(token)
    header = bytes([
        0b01000000 | token_length,  # Ver=1, Type=0(CON), TKL
        0x01,                        # Code=0.01 (GET)
    ]) + struct.pack('!H', msg_id)  # Message ID
    
    data = header + token
    
    path_bytes = path.encode('utf-8')
    path_len = len(path_bytes)
    
    if path_len < 13:
        option_header = bytes([(11 << 4) | path_len])
    else:
        option_header = bytes([0xBD, path_len - 13])
    
    data += option_header + path_bytes
    
    return data

def parse_coap_message(data):
    """解析 CoAP 消息"""
    if len(data) < 4:
        return None
    
    byte0 = data[0]
    version = (byte0 >> 6) & 0x03
    msg_type = (byte0 >> 4) & 0x03
    token_length = byte0 & 0x0F
    
    code = data[1]
    msg_id = struct.unpack('!H', data[2:4])[0]
    
    token = data[4:4+token_length] if token_length > 0 else b''
    
    return {
        'version': version,
        'type': msg_type,
        'token_length': token_length,
        'token': token,
        'code': code,
        'msg_id': msg_id,
        'raw': data
    }

def main():
    print("="*70)
    print("测试 CoAP 消息生成和解析")
    print("="*70)
    
    # 测试 1: 创建请求
    print("\n测试 1: 创建 CoAP GET 请求")
    token = b'\xAA\xBB\xCC\xDD'
    msg_id = 1001
    request = create_coap_get_request("time", token, msg_id)
    
    print(f"Token: {token.hex()}")
    print(f"Message ID: {msg_id}")
    print(f"生成的请求: {request.hex()}")
    print(f"长度: {len(request)} 字节")
    
    # 解析请求
    print("\n测试 2: 解析生成的请求")
    parsed = parse_coap_message(request)
    if parsed:
        print(f"版本: {parsed['version']}")
        print(f"类型: {parsed['type']} (0=CON)")
        print(f"Token 长度: {parsed['token_length']}")
        print(f"Token: {parsed['token'].hex()}")
        print(f"代码: {(parsed['code'] >> 5) & 0x07}.{parsed['code'] & 0x1F:02d}")
        print(f"消息ID: {parsed['msg_id']}")
        
        # 验证
        print("\n测试 3: 验证")
        if parsed['token'] == token:
            print("✅ Token 匹配")
        else:
            print(f"❌ Token 不匹配: 期望 {token.hex()}, 实际 {parsed['token'].hex()}")
        
        if parsed['msg_id'] == msg_id:
            print("✅ Message ID 匹配")
        else:
            print(f"❌ Message ID 不匹配: 期望 {msg_id}, 实际 {parsed['msg_id']}")
    
    # 测试 4: 手动构造预期的请求
    print("\n测试 4: 手动构造预期的请求")
    expected = bytes([
        0x44,        # Ver=1, Type=0, TKL=4
        0x01,        # Code=0.01 (GET)
        0x03, 0xE9,  # Message ID = 1001
        0xAA, 0xBB, 0xCC, 0xDD,  # Token
        0xB4,        # Option: Delta=11, Length=4
        0x74, 0x69, 0x6D, 0x65,  # "time"
    ])
    
    print(f"预期的请求: {expected.hex()}")
    print(f"生成的请求: {request.hex()}")
    
    if request == expected:
        print("✅ 完全匹配！")
    else:
        print("❌ 不匹配")
        print(f"差异:")
        for i, (e, a) in enumerate(zip(expected, request)):
            if e != a:
                print(f"  字节 {i}: 期望 {e:02x}, 实际 {a:02x}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

