#!/usr/bin/env python3
"""
简单测试：验证客户端的 Token 重用功能
"""

import asyncio
import logging
import functools
from aiocoap import *
from aiocoap import error
from aiocoap.tokenmanager import TokenManager
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test-Client")

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
logger.info("✓ Monkey Patch 已应用")
# ============================================================

async def main():
    logger.info("="*60)
    logger.info("测试 Token 重用攻击")
    logger.info("="*60)
    
    context = await Context.create_client_context()
    fixed_token = b'ATTACK_TOKEN'
    
    # 发送第一个请求
    logger.info(f"\n【请求 #1】使用 Token: {fixed_token.hex()}")
    msg1 = Message(code=Code.GET, uri="coap://127.0.0.1:5683/status", _token=fixed_token)
    
    try:
        response1 = await asyncio.wait_for(context.request(msg1).response, timeout=10.0)
        logger.info(f"✓ 响应 #1: Token={response1.token.hex()}, 数据={response1.payload.decode()}")
    except asyncio.TimeoutError:
        logger.error("✗ 请求 #1 超时")
    except Exception as e:
        logger.error(f"✗ 请求 #1 失败: {e}")
    
    await asyncio.sleep(0.5)
    
    # 发送第二个请求（重用相同 Token）
    logger.info(f"\n【请求 #2】重用 Token: {fixed_token.hex()}")
    msg2 = Message(code=Code.GET, uri="coap://127.0.0.1:5683/status", _token=fixed_token)
    
    try:
        response2 = await asyncio.wait_for(context.request(msg2).response, timeout=10.0)
        logger.info(f"✓ 响应 #2: Token={response2.token.hex()}, 数据={response2.payload.decode()}")
    except asyncio.TimeoutError:
        logger.error("✗ 请求 #2 超时")
    except Exception as e:
        logger.error(f"✗ 请求 #2 失败: {e}")
    
    # 验证
    logger.info("\n" + "="*60)
    if response1.token == response2.token == fixed_token:
        logger.info("✓✓✓ 成功！两个请求使用了相同的 Token！")
        logger.info(f"    Token: {fixed_token.hex()}")
    else:
        logger.error("✗✗✗ 失败！Token 不匹配")
    logger.info("="*60)
    
    await context.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

