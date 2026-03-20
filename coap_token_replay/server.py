#!/usr/bin/env python3
"""
CoAP 服务器 - 极简版
"""
import asyncio
import logging
from datetime import datetime
import aiocoap.resource as resource
from aiocoap import Message, Context
from aiocoap.numbers.codes import Code

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

class TimeResource(resource.Resource):
    async def render_get(self, request):
        token = request.token.hex() if request.token else "no-token"
        logger.info(f"收到 GET /time - Token: {token}")
        payload = f"时间: {datetime.now().strftime('%H:%M:%S')}".encode()
        return Message(code=Code.CONTENT, payload=payload)

class DebugResource(resource.Resource):
    """调试资源 - 打印收到的原始请求"""
    async def render_get(self, request):
        logger.info(f"Debug: code={request.code}, token={request.token.hex()}, mid={request.mid}, opt={request.opt}")
        return Message(code=Code.CONTENT, payload=b"debug ok")

class CatchAllResource(resource.Resource):
    """捕获所有未匹配的请求，用于调试"""
    async def render_get(self, request):
        uri_path = request.opt.uri_path
        logger.info(f"CatchAll: code={request.code}, token={request.token.hex() if request.token else 'none'}, "
                   f"mid={request.mid:#06x}, uri_path={uri_path}, opt={list(request.opt.option_list())}")
        return Message(code=Code.CONTENT, payload=f"Path: {'/'.join(uri_path) if uri_path else '/'}".encode())

async def main():
    root = resource.Site()
    root.add_resource(['/time'], TimeResource())
    root.add_resource([''], CatchAllResource())  # 根路径 catch-all
    
    ctx = await Context.create_server_context(root, bind=("127.0.0.1", 5683))
    logger.info("服务器启动: coap://127.0.0.1:5683")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
