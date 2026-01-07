#!/usr/bin/env python3
"""
测试 aiocoap 的 _token 参数是否可以用于手动设置 Token
"""

import asyncio
import sys
from datetime import datetime
from aiocoap import Message, Context, Code

async def test_token_parameter():
    """测试不同的 Token 设置方法"""
    
    print("=" * 60)
    print("测试 aiocoap 的 Token 参数")
    print("=" * 60)
    print()
    
    # 测试 1: 使用 token 参数（已弃用，会警告）
    print("【测试 1】使用 token 参数（已弃用）")
    print("-" * 60)
    try:
        msg1 = Message(code=Code.GET, uri="coap://127.0.0.1/test", token=b'test123')
        print(f"✓ 创建消息成功")
        print(f"  设置的 Token: b'test123'")
        print(f"  实际的 Token: {msg1.token}")
        print(f"  Token 十六进制: {msg1.token.hex()}")
    except Exception as e:
        print(f"✗ 失败: {e}")
    print()
    
    # 测试 2: 使用 _token 参数（内部 API）
    print("【测试 2】使用 _token 参数（内部 API）")
    print("-" * 60)
    try:
        msg2 = Message(code=Code.GET, uri="coap://127.0.0.1/test", _token=b'test456')
        print(f"✓ 创建消息成功（无警告！）")
        print(f"  设置的 Token: b'test456'")
        print(f"  实际的 Token: {msg2.token}")
        print(f"  Token 十六进制: {msg2.token.hex()}")
    except Exception as e:
        print(f"✗ 失败: {e}")
    print()
    
    # 测试 3: 不设置 Token（默认行为）
    print("【测试 3】不设置 Token（默认行为）")
    print("-" * 60)
    try:
        msg3 = Message(code=Code.GET, uri="coap://127.0.0.1/test")
        print(f"✓ 创建消息成功")
        print(f"  实际的 Token: {msg3.token}")
        print(f"  Token 十六进制: {msg3.token.hex() if msg3.token else 'empty'}")
    except Exception as e:
        print(f"✗ 失败: {e}")
    print()
    
    # 测试 4: 通过 Context 发送请求（关键测试）
    print("【测试 4】通过 Context 发送请求（验证 Token 是否被保留）")
    print("-" * 60)
    print("注意: 这个测试需要服务器运行在 127.0.0.1:5683")
    print()

    context = await Context.create_client_context()

    # 使用固定 Token 发送两个请求
    fixed_token = b'FIXED_TOKEN_123'

    for i in range(1, 3):
        print(f"请求 #{i}:")
        msg = Message(
            code=Code.GET,
            uri="coap://127.0.0.1:5683/status",
            _token=fixed_token
        )
        print(f"  创建后 Token: {msg.token.hex()}")

        # 创建请求对象
        request_obj = context.request(msg)
        print(f"  request() 后 Token: {msg.token.hex()}")

        try:
            response = await asyncio.wait_for(
                request_obj.response,
                timeout=5.0
            )
            print(f"  ✓ 收到响应")
            print(f"  发送时 Token: {msg.token.hex()}")
            print(f"  响应 Token: {response.token.hex()}")
            print(f"  响应状态: {response.code}")
            print(f"  响应数据: {response.payload.decode() if response.payload else 'empty'}")

            # 检查 Token 是否被保留
            if response.token == fixed_token:
                print(f"  ✓✓✓ Token 被成功保留！")
            else:
                print(f"  ✗✗✗ Token 被 Context 覆盖了！")
                print(f"      期望: {fixed_token.hex()}")
                print(f"      实际: {response.token.hex()}")
        except asyncio.TimeoutError:
            print(f"  ✗ 超时（响应时间 > 5秒）")
            print(f"  最终 Token: {msg.token.hex()}")
        except Exception as e:
            print(f"  ✗ 错误: {e}")

        print()

        if i < 2:
            await asyncio.sleep(0.5)

    await context.shutdown()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    print(f"开始时间: {datetime.now()}")
    print()
    
    try:
        asyncio.run(test_token_parameter())
    except KeyboardInterrupt:
        print("\n测试被中断")
        sys.exit(1)
    
    print()
    print(f"结束时间: {datetime.now()}")

