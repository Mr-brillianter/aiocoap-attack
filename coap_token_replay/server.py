#!/usr/bin/env python3
"""
CoAP服务器程序，模拟受攻击的服务端
用于演示 Token 重用攻击
"""
import asyncio
import logging
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap import Message, Context
from aiocoap.numbers.codes import Code

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CoAP-Server")


class RequestCounter:
    """请求计数器，用于跟踪每个 Token 的请求次数"""
    def __init__(self):
        self.counter = {}

    def increment(self, token):
        """增加计数并返回当前值"""
        token_str = token.hex() if token else "no-token"
        self.counter[token_str] = self.counter.get(token_str, 0) + 1
        return self.counter[token_str]

    def get(self, token):
        """获取当前计数"""
        token_str = token.hex() if token else "no-token"
        return self.counter.get(token_str, 0)


class ToggleResource(resource.Resource):
    """处理 /toggle 路径的资源 - 模拟状态切换"""

    def __init__(self, counter):
        super().__init__()
        self.counter = counter
        self.state = False

    async def render_get(self, request):
        """处理 GET 请求"""
        token = request.token.hex() if request.token else "no-token"
        count = self.counter.increment(request.token)

        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 收到 GET /toggle - "
                   f"Token: {token}, MsgID: {request.mid}, 请求序号: {count}")

        # 第一个请求添加延迟（模拟网络延迟，便于攻击者捕获）
        if count == 1:
            logger.info(f"   → 第一个请求，延迟 2 秒响应...")
            await asyncio.sleep(2)

        # 切换状态
        self.state = not self.state
        response_data = f"Toggle状态: {'ON' if self.state else 'OFF'} (请求#{count})".encode('utf-8')

        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 发送响应 - "
                   f"Token: {token}, 数据: {response_data.decode('utf-8')}")

        return Message(code=Code.CONTENT, payload=response_data)

    async def render_post(self, request):
        """处理 POST 请求"""
        token = request.token.hex() if request.token else "no-token"
        count = self.counter.increment(request.token)

        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 收到 POST /toggle - "
                   f"Token: {token}, MsgID: {request.mid}, 请求序号: {count}")

        # 第一个请求添加延迟
        if count == 1:
            logger.info(f"   → 第一个请求，延迟 2 秒响应...")
            await asyncio.sleep(2)

        # 切换状态
        self.state = not self.state
        response_data = f"Toggle状态已更新: {'ON' if self.state else 'OFF'} (请求#{count})".encode('utf-8')

        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 发送响应 - "
                   f"Token: {token}, 数据: {response_data.decode('utf-8')}")

        return Message(code=Code.CHANGED, payload=response_data)


class StatusResource(resource.Resource):
    """处理 /status 路径的资源 - 返回服务器状态"""

    def __init__(self, counter):
        super().__init__()
        self.counter = counter

    async def render_get(self, request):
        """处理 GET 请求"""
        token = request.token.hex() if request.token else "no-token"
        count = self.counter.increment(request.token)

        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 收到 GET /status - "
                   f"Token: {token}, MsgID: {request.mid}, 请求序号: {count}")

        # 第一个请求添加延迟
        if count == 1:
            logger.info(f"   → 第一个请求，延迟 2 秒响应...")
            await asyncio.sleep(2)

        response_data = f"服务器状态: 运行中 (请求#{count}, 时间: {datetime.now().strftime('%H:%M:%S')})".encode('utf-8')

        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 发送响应 - "
                   f"Token: {token}, 数据: {response_data.decode('utf-8')}")

        return Message(code=Code.CONTENT, payload=response_data)


class TimeResource(resource.Resource):
    """处理 /time 路径的资源 - 返回当前时间"""

    def __init__(self, counter):
        super().__init__()
        self.counter = counter

    async def render_get(self, request):
        """处理 GET 请求"""
        token = request.token.hex() if request.token else "no-token"
        count = self.counter.increment(request.token)

        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 收到 GET /time - "
                   f"Token: {token}, MsgID: {request.mid}, 请求序号: {count}")

        # 第一个请求添加延迟
        if count == 1:
            logger.info(f"   → 第一个请求，延迟 2 秒响应...")
            await asyncio.sleep(2)

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response_data = f"当前时间: {current_time} (请求#{count})".encode('utf-8')

        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] 发送响应 - "
                   f"Token: {token}, 数据: {response_data.decode('utf-8')}")

        return Message(code=Code.CONTENT, payload=response_data)


class WelcomeResource(resource.Resource):
    """处理根路径的资源 - 欢迎信息"""

    async def render_get(self, request):
        """处理 GET 请求"""
        welcome_msg = b"CoAP Token Replay Attack Demo Server\nAvailable resources:\n  - /toggle\n  - /status\n  - /.well-known/core"
        return Message(code=Code.CONTENT, payload=welcome_msg)


async def main():
    """主函数 - 启动 CoAP 服务器"""

    # 创建请求计数器
    counter = RequestCounter()

    # 创建资源树
    root = resource.Site()

    # 添加资源
    root.add_resource([], WelcomeResource())
    root.add_resource(['toggle'], ToggleResource(counter))
    root.add_resource(['status'], StatusResource(counter))
    root.add_resource(['time'], TimeResource(counter))
    root.add_resource(['.well-known', 'core'],
                     resource.WKCResource(root.get_resources_as_linkheader))

    # 启动服务器（绑定到 127.0.0.1，避免 any-address 问题）
    host = "127.0.0.1"
    port = 5683

    await Context.create_server_context(root, bind=(host, port))

    print("="*60)
    print("CoAP Token Replay Attack - Demo Server")
    print("="*60)
    print(f"服务器地址: coap://{host}:{port}")
    print(f"可用资源:")
    print(f"  - coap://{host}:{port}/          (欢迎信息)")
    print(f"  - coap://{host}:{port}/toggle    (状态切换)")
    print(f"  - coap://{host}:{port}/status    (服务器状态)")
    print(f"  - coap://{host}:{port}/time      (当前时间)")
    print(f"  - coap://{host}:{port}/.well-known/core")
    print("="*60)
    print("服务器已启动，按 Ctrl+C 停止")
    print("="*60)
    logger.info("CoAP 服务器已启动并等待请求...")

    # 保持运行
    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已停止")