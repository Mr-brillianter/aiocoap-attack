#!/usr/bin/env python3
"""
CoAP客户端程序，模拟易受攻击的客户端
使用 Monkey Patch 绕过 aiocoap 的 Token 自动管理
"""
import asyncio
import logging
import hashlib
import functools
from aiocoap import *
from aiocoap import error
from aiocoap.tokenmanager import TokenManager
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CoAP-Client")

# ============================================================
# Monkey Patch: 允许手动设置 Token
# ============================================================
# 保存原始的 request 方法
_original_request = TokenManager.request

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
        logger.debug(f"自动分配 Token: {msg.token.hex()}")
    else:
        logger.debug(f"保留手动设置的 Token: {msg.token.hex()}")

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
logger.info("✓ 已应用 Monkey Patch：允许手动设置 Token")
# ============================================================

class VulnerableCoAPClient:
    def __init__(self, server_url="coap://127.0.0.1:5684"):
        self.server_url = server_url
        self.context = None
        self.current_token = b'fixed123'  # 使用固定Token - 这是漏洞！
        
    async def init(self):
        """初始化客户端"""
        self.context = await Context.create_client_context()
        
    def generate_token(self, request_num):
        """生成Token（有漏洞的实现）"""
        # 漏洞1：使用固定Token
        # return b'fixed123'
        
        # 漏洞2：使用可预测的Token
        return hashlib.md5(str(request_num % 3).encode()).digest()[:4]
        
        # 安全做法：使用随机Token
        # return os.urandom(4)
    
    async def send_request(self, path, request_num=1):
        """发送CoAP请求"""
        try:
            # 使用固定或可预测的Token（这是漏洞！）
            token = self.current_token
            logger.info(f"[{datetime.now()}] 发送请求#{request_num} - "
                       f"路径: {path}, 期望 Token: {token.hex()}")

            # 构建请求，使用 _token 参数手动设置 Token
            request = Message(
                code=Code.GET,
                uri=f"{self.server_url}/{path}",
                _token=token  # 使用内部参数设置 Token
            )

            logger.info(f"  → 消息创建后 Token: {request.token.hex()}")

            # 发送请求
            response = await self.context.request(request).response

            logger.info(f"[{datetime.now()}] 收到响应#{request_num} - "
                       f"Token: {response.token.hex() if response.token else 'none'}, "
                       f"状态: {response.code}, 数据: {response.payload.decode()}")

            # 验证 Token 是否被保留
            if response.token == token:
                logger.info(f"  ✓ Token 成功保留！")
            else:
                logger.warning(f"  ✗ Token 被修改: {token.hex()} → {response.token.hex()}")

            return response

        except Exception as e:
            logger.error(f"请求失败: {e}")
            return None
    
    async def simulate_attack_scenario(self):
        """模拟攻击场景"""
        logger.info("="*50)
        logger.info("开始模拟令牌重用攻击场景")
        logger.info("="*50)
        
        # 第一次请求
        logger.info("\n1. 第一次请求（响应将被攻击者延迟）")
        task1 = asyncio.create_task(self.send_request("toggle", 1))
        
        # 等待一段时间后发送第二次请求
        await asyncio.sleep(1)
        
        logger.info("\n2. 第二次请求（使用相同的Token）")
        task2 = asyncio.create_task(self.send_request("toggle", 2))
        
        # 等待两个请求完成
        await asyncio.gather(task1, task2)

async def main():
    client = VulnerableCoAPClient()
    await client.init()
    await client.simulate_attack_scenario()

if __name__ == "__main__":
    asyncio.run(main())