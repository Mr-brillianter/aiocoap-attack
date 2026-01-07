#!/usr/bin/env python3
"""
测试 Monkey Patch 是否能够保留手动设置的 Token
"""

import asyncio
import sys
import functools
from datetime import datetime
from aiocoap import Message, Context, Code, error
from aiocoap.tokenmanager import TokenManager

# ============================================================
# Monkey Patch: 允许手动设置 Token
# ============================================================
def _patched_request(self, request):
    """
    修改后的 request 方法，允许保留手动设置的 Token
    如果消息已经有 Token，就不覆盖它
    """
    if self.outgoing_requests is None:
        request.add_exception(error.LibraryShutdown())
        return

    msg = request.request

    assert msg.code.is_request(), "Message code is not valid for request"
    assert msg.remote is not None, "Remote not pre-populated"

    # ★ 关键修改：只在 Token 为空时才分配新 Token
    if not msg.token:
        msg.token = self.next_token()
        print(f"  [Patch] 自动分配 Token: {msg.token.hex()}")
    else:
        print(f"  [Patch] 保留手动设置的 Token: {msg.token.hex()}")

    self.log.debug(
        "Sending request - Token: %s, Remote: %s", msg.token.hex(), msg.remote
    )

    if msg.remote.is_multicast:
        self.log.warning("Sending request to multicast via unicast request method")
        key = (msg.token, None)
    else:
        key = (msg.token, msg.remote)

    self.outgoing_requests[key] = request
    request.on_interest_end(
        functools.partial(self.outgoing_requests.pop, key, None)
    )

    try:
        send_canceller = self.token_interface.send_message(
            msg, lambda: request.add_exception(error.MessageError)
        )
    except Exception as e:
        request.add_exception(e)
        return

    if send_canceller is not None:
        request.on_interest_end(send_canceller)

# 应用 Monkey Patch
TokenManager.request = _patched_request
print("✓ 已应用 Monkey Patch")
print()
# ============================================================

async def test_fixed_token():
    """测试固定 Token 是否能够被保留"""
    
    print("=" * 60)
    print("测试 Monkey Patch 后的 Token 行为")
    print("=" * 60)
    print()
    
    context = await Context.create_client_context()
    
    # 使用固定 Token 发送两个请求
    fixed_token = b'FIXED123'
    
    for i in range(1, 3):
        print(f"【请求 #{i}】")
        msg = Message(
            code=Code.GET, 
            uri="coap://127.0.0.1:5683/status",
            _token=fixed_token
        )
        print(f"  创建后 Token: {msg.token.hex()}")
        
        try:
            response = await asyncio.wait_for(
                context.request(msg).response, 
                timeout=5.0
            )
            print(f"  ✓ 收到响应")
            print(f"  发送的 Token: {msg.token.hex()}")
            print(f"  响应的 Token: {response.token.hex()}")
            print(f"  响应状态: {response.code}")
            print(f"  响应数据: {response.payload.decode() if response.payload else 'empty'}")
            
            # 检查 Token 是否被保留
            if response.token == fixed_token:
                print(f"  ✓✓✓ Token 成功保留！")
            else:
                print(f"  ✗✗✗ Token 被修改了！")
                print(f"      期望: {fixed_token.hex()}")
                print(f"      实际: {response.token.hex()}")
        except asyncio.TimeoutError:
            print(f"  ✗ 超时（服务器可能未运行）")
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
        asyncio.run(test_fixed_token())
    except KeyboardInterrupt:
        print("\n测试被中断")
        sys.exit(1)
    
    print()
    print(f"结束时间: {datetime.now()}")

