#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoAP 测试服务器 (CoAP Test Server)

一个简单的 CoAP 服务器，用于测试攻击脚本。
包含请求统计和日志记录功能。

使用方法:
    python test_server.py [--port PORT] [--host HOST]
"""

import asyncio
import argparse
import logging
import datetime
import json
from collections import defaultdict
from aiocoap import Context, Message, resource
from aiocoap.numbers.codes import Code

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RequestStats:
    """请求统计类"""
    
    def __init__(self):
        self.total_requests = 0
        self.method_counts = defaultdict(int)
        self.path_counts = defaultdict(int)
        self.start_time = datetime.datetime.now()
        self.last_report_time = datetime.datetime.now()
        self.requests_since_last_report = 0
    
    def record_request(self, method, path):
        """记录请求"""
        self.total_requests += 1
        self.requests_since_last_report += 1
        self.method_counts[method] += 1
        self.path_counts[path] += 1
    
    def should_report(self, interval=5):
        """是否应该报告统计信息"""
        now = datetime.datetime.now()
        if (now - self.last_report_time).total_seconds() >= interval:
            self.last_report_time = now
            return True
        return False
    
    def get_stats(self):
        """获取统计信息"""
        uptime = (datetime.datetime.now() - self.start_time).total_seconds()
        rate = self.total_requests / uptime if uptime > 0 else 0
        
        return {
            'total_requests': self.total_requests,
            'uptime_seconds': uptime,
            'requests_per_second': rate,
            'methods': dict(self.method_counts),
            'paths': dict(self.path_counts)
        }


# 全局统计对象
stats = RequestStats()


class SensorResource(resource.Resource):
    """模拟传感器资源"""
    
    async def render_get(self, request):
        """处理 GET 请求"""
        stats.record_request('GET', '/sensor')
        
        # 模拟传感器数据
        data = {
            'temperature': 22.5,
            'humidity': 60,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        payload = json.dumps(data).encode('utf-8')
        
        if stats.should_report():
            logger.info(f"📊 统计: {stats.requests_since_last_report} 请求/5秒, "
                       f"总计: {stats.total_requests}")
            stats.requests_since_last_report = 0
        
        return Message(code=Code.CONTENT, payload=payload)
    
    async def render_post(self, request):
        """处理 POST 请求"""
        stats.record_request('POST', '/sensor')
        
        logger.debug(f"收到 POST 数据: {request.payload[:100]}")
        
        return Message(code=Code.CHANGED, payload=b"Data received")


class DataResource(resource.Resource):
    """模拟数据资源"""
    
    async def render_get(self, request):
        """处理 GET 请求"""
        stats.record_request('GET', '/data')
        
        payload = b"Sample data from server"
        return Message(code=Code.CONTENT, payload=payload)
    
    async def render_post(self, request):
        """处理 POST 请求"""
        stats.record_request('POST', '/data')
        
        logger.debug(f"收到数据: {len(request.payload)} 字节")
        
        return Message(code=Code.CREATED, payload=b"Data created")
    
    async def render_put(self, request):
        """处理 PUT 请求"""
        stats.record_request('PUT', '/data')
        
        return Message(code=Code.CHANGED, payload=b"Data updated")
    
    async def render_delete(self, request):
        """处理 DELETE 请求"""
        stats.record_request('DELETE', '/data')
        
        return Message(code=Code.DELETED, payload=b"Data deleted")


class StatsResource(resource.Resource):
    """统计信息资源"""
    
    async def render_get(self, request):
        """返回服务器统计信息"""
        stats.record_request('GET', '/stats')
        
        stats_data = stats.get_stats()
        payload = json.dumps(stats_data, indent=2).encode('utf-8')
        
        return Message(code=Code.CONTENT, payload=payload)


async def main(host='localhost', port=5683):
    """启动 CoAP 服务器"""
    
    # 创建资源树
    root = resource.Site()
    root.add_resource(['sensor'], SensorResource())
    root.add_resource(['data'], DataResource())
    root.add_resource(['stats'], StatsResource())
    
    logger.info("=" * 60)
    logger.info("CoAP 测试服务器启动")
    logger.info("=" * 60)
    logger.info(f"监听地址: {host}:{port}")
    logger.info(f"可用资源:")
    logger.info(f"  - coap://{host}:{port}/sensor  (GET, POST)")
    logger.info(f"  - coap://{host}:{port}/data    (GET, POST, PUT, DELETE)")
    logger.info(f"  - coap://{host}:{port}/stats   (GET - 查看统计)")
    logger.info("=" * 60)
    logger.info("按 Ctrl+C 停止服务器\n")
    
    # 创建服务器上下文
    bind_addr = (host, port)
    context = await Context.create_server_context(root, bind=bind_addr)
    
    try:
        # 保持服务器运行
        await asyncio.get_running_loop().create_future()
    except KeyboardInterrupt:
        logger.info("\n服务器正在关闭...")
        
        # 显示最终统计
        final_stats = stats.get_stats()
        logger.info("\n" + "=" * 60)
        logger.info("最终统计")
        logger.info("=" * 60)
        logger.info(f"总请求数: {final_stats['total_requests']}")
        logger.info(f"运行时间: {final_stats['uptime_seconds']:.2f} 秒")
        logger.info(f"平均速率: {final_stats['requests_per_second']:.2f} 请求/秒")
        logger.info(f"方法分布: {final_stats['methods']}")
        logger.info(f"路径分布: {final_stats['paths']}")
        logger.info("=" * 60)
    finally:
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='CoAP 测试服务器 - 用于测试攻击脚本'
    )
    
    parser.add_argument('--host', default='localhost',
                       help='监听地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=5683,
                       help='监听端口 (默认: 5683)')
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(host=args.host, port=args.port))
    except KeyboardInterrupt:
        pass

