#!/usr/bin/env python3
"""
快速测试 MITM 攻击实现
"""
import asyncio
import sys

# 测试导入
try:
    from attacker import MITMAttacker, CoAPMessage
    print("✅ 成功导入 MITMAttacker")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 测试 CoAP 消息解析
def test_coap_parser():
    print("\n" + "="*70)
    print("测试 CoAP 消息解析器")
    print("="*70)
    
    # 构造一个简单的 CoAP 消息
    # Ver=1, Type=0(CON), TKL=4, Code=1(GET), MsgID=12345, Token=0x1a2b3c4d
    data = bytes([
        0b01000100,  # Ver=1, Type=0, TKL=4
        0x01,        # Code=0.01 (GET)
        0x30, 0x39,  # Message ID = 12345
        0x1a, 0x2b, 0x3c, 0x4d  # Token
    ])
    
    msg = CoAPMessage.parse(data)
    
    if msg:
        print(f"✅ 解析成功:")
        print(f"   版本: {msg['version']}")
        print(f"   类型: {msg['type']}")
        print(f"   Token 长度: {msg['token_length']}")
        print(f"   代码: {CoAPMessage.format_code(msg['code'])}")
        print(f"   消息ID: {msg['msg_id']}")
        print(f"   Token: {msg['token'].hex()}")
        print(f"   是请求: {msg['is_request']}")
        print(f"   是响应: {msg['is_response']}")
        
        # 验证
        assert msg['version'] == 1, "版本错误"
        assert msg['type'] == 0, "类型错误"
        assert msg['token_length'] == 4, "Token 长度错误"
        assert msg['code'] == 1, "代码错误"
        assert msg['msg_id'] == 12345, "消息ID错误"
        assert msg['token'] == b'\x1a\x2b\x3c\x4d', "Token错误"
        assert msg['is_request'] == True, "应该是请求"
        assert msg['is_response'] == False, "不应该是响应"
        
        print("\n✅ 所有断言通过！")
    else:
        print("❌ 解析失败")
        return False
    
    return True

# 测试响应消息解析
def test_response_parser():
    print("\n" + "="*70)
    print("测试响应消息解析")
    print("="*70)
    
    # 构造一个 CoAP 响应消息
    # Ver=1, Type=2(ACK), TKL=4, Code=69(2.05 Content), MsgID=12345, Token=0x1a2b3c4d
    data = bytes([
        0b01100100,  # Ver=1, Type=2(ACK), TKL=4
        0x45,        # Code=2.05 (Content) = 69
        0x30, 0x39,  # Message ID = 12345
        0x1a, 0x2b, 0x3c, 0x4d  # Token
    ])
    
    msg = CoAPMessage.parse(data)
    
    if msg:
        print(f"✅ 解析成功:")
        print(f"   版本: {msg['version']}")
        print(f"   类型: {msg['type']}")
        print(f"   代码: {CoAPMessage.format_code(msg['code'])}")
        print(f"   消息ID: {msg['msg_id']}")
        print(f"   Token: {msg['token'].hex()}")
        print(f"   是请求: {msg['is_request']}")
        print(f"   是响应: {msg['is_response']}")
        
        # 验证
        assert msg['version'] == 1, "版本错误"
        assert msg['type'] == 2, "类型错误（应该是ACK）"
        assert msg['code'] == 69, "代码错误"
        assert CoAPMessage.format_code(msg['code']) == "2.05", "代码格式化错误"
        assert msg['is_request'] == False, "不应该是请求"
        assert msg['is_response'] == True, "应该是响应"
        
        print("\n✅ 所有断言通过！")
    else:
        print("❌ 解析失败")
        return False
    
    return True

# 测试 MITMAttacker 初始化
def test_attacker_init():
    print("\n" + "="*70)
    print("测试 MITMAttacker 初始化")
    print("="*70)
    
    try:
        attacker = MITMAttacker(
            listen_host="127.0.0.1",
            listen_port=5684,
            server_host="127.0.0.1",
            server_port=5683,
            attack_delay=5
        )
        
        print("✅ MITMAttacker 初始化成功")
        print(f"   监听地址: {attacker.listen_host}:{attacker.listen_port}")
        print(f"   服务器地址: {attacker.server_host}:{attacker.server_port}")
        print(f"   攻击延迟: {attacker.attack_delay} 秒")
        
        # 验证
        assert attacker.listen_host == "127.0.0.1"
        assert attacker.listen_port == 5684
        assert attacker.server_host == "127.0.0.1"
        assert attacker.server_port == 5683
        assert attacker.attack_delay == 5
        
        print("\n✅ 所有断言通过！")
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

# 主函数
def main():
    print("\n" + "="*70)
    print("CoAP MITM 攻击 - 单元测试")
    print("="*70)
    
    results = []
    
    # 运行测试
    results.append(("CoAP 请求解析", test_coap_parser()))
    results.append(("CoAP 响应解析", test_response_parser()))
    results.append(("MITMAttacker 初始化", test_attacker_init()))
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("="*70)
    if all_passed:
        print("🎉 所有测试通过！")
        print("\n下一步:")
        print("  1. 启动服务器: uv run python server.py")
        print("  2. 启动攻击者: uv run python attacker.py")
        print("  3. 运行演示: uv run python demo_mitm_attack.py")
    else:
        print("❌ 部分测试失败，请检查代码")
    print("="*70)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

