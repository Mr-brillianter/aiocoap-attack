#!/usr/bin/env python3
"""
快速测试 CoAP 服务器（无需用户输入）
"""
import asyncio
import sys

try:
    import aiocoap
    from aiocoap import Message, Context
    from aiocoap.numbers.codes import Code
except ImportError as e:
    print(f"错误: 无法导入 aiocoap - {e}")
    sys.exit(1)


async def quick_test():
    """快速测试服务器"""
    
    print("="*60)
    print("CoAP 服务器快速测试")
    print("="*60)
    
    try:
        # 创建客户端
        print("\n创建客户端...")
        context = await Context.create_client_context()
        print("✓ 客户端创建成功")
        
        # 测试 /status
        print("\n测试 GET /status...")
        request = Message(code=Code.GET, uri="coap://127.0.0.1:5683/status")
        response = await asyncio.wait_for(context.request(request).response, timeout=5.0)
        print(f"✓ 响应: {response.payload.decode('utf-8')}")
        
        # 关闭客户端
        await context.shutdown()
        
        print("\n" + "="*60)
        print("✓ 测试成功！服务器正常工作")
        print("="*60)
        
    except asyncio.TimeoutError:
        print("\n✗ 连接超时 - 请确保服务器正在运行:")
        print("  python coap_token_replay/server.py")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(quick_test())

