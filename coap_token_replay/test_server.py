#!/usr/bin/env python3
"""
测试 CoAP 服务器是否正常工作
"""
import asyncio
import sys

try:
    import aiocoap
    from aiocoap import Message, Context
    from aiocoap.numbers.codes import Code
except ImportError as e:
    print(f"错误: 无法导入 aiocoap - {e}")
    print("请确保已安装 aiocoap: pip install aiocoap")
    sys.exit(1)


async def test_server():
    """测试服务器的各个端点"""
    
    print("="*60)
    print("CoAP 服务器测试")
    print("="*60)
    
    # 创建客户端上下文
    print("\n[1] 创建 CoAP 客户端...")
    try:
        context = await Context.create_client_context()
        print("✓ 客户端创建成功")
    except Exception as e:
        print(f"✗ 客户端创建失败: {e}")
        return
    
    server_url = "coap://127.0.0.1:5683"
    
    # 测试根路径
    print(f"\n[2] 测试 GET {server_url}/")
    try:
        request = Message(code=Code.GET, uri=f"{server_url}/")
        response = await context.request(request).response
        print(f"✓ 响应代码: {response.code}")
        print(f"  内容: {response.payload.decode('utf-8')}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    # 测试 /status
    print(f"\n[3] 测试 GET {server_url}/status")
    try:
        request = Message(code=Code.GET, uri=f"{server_url}/status")
        response = await context.request(request).response
        print(f"✓ 响应代码: {response.code}")
        print(f"  内容: {response.payload.decode('utf-8')}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    # 测试 /toggle (GET)
    print(f"\n[4] 测试 GET {server_url}/toggle")
    try:
        request = Message(code=Code.GET, uri=f"{server_url}/toggle")
        response = await context.request(request).response
        print(f"✓ 响应代码: {response.code}")
        print(f"  内容: {response.payload.decode('utf-8')}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    # 测试 /toggle (POST)
    print(f"\n[5] 测试 POST {server_url}/toggle")
    try:
        request = Message(code=Code.POST, uri=f"{server_url}/toggle", payload=b"toggle")
        response = await context.request(request).response
        print(f"✓ 响应代码: {response.code}")
        print(f"  内容: {response.payload.decode('utf-8')}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    # 测试 /.well-known/core
    print(f"\n[6] 测试 GET {server_url}/.well-known/core")
    try:
        request = Message(code=Code.GET, uri=f"{server_url}/.well-known/core")
        response = await context.request(request).response
        print(f"✓ 响应代码: {response.code}")
        print(f"  内容: {response.payload.decode('utf-8')}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    # 关闭客户端
    await context.shutdown()
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


async def main():
    print("\n确保 CoAP 服务器正在运行:")
    print("  python coap_token_replay/server.py")
    print("\n按 Enter 继续测试，或 Ctrl+C 取消...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n测试已取消")
        return
    
    await test_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试已中断")

