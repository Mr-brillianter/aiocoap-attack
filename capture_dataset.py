#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoAP 攻击数据集自动采集脚本
Automated CoAP Attack Dataset Collection Script

此脚本自动化采集正常流量、重放攻击和泛洪攻击的 PCAP 数据。
需要配合 Wireshark/tshark 使用。

使用方法:
    python capture_dataset.py --output-dir ./dataset --duration 30
"""

import asyncio
import argparse
import logging
import subprocess
import time
import csv
import os
from datetime import datetime
from pathlib import Path
import platform

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatasetCollector:
    """数据集采集器"""
    
    def __init__(self, output_dir, duration=30, interface='lo'):
        """
        初始化数据集采集器
        
        Args:
            output_dir: 输出目录
            duration: 每个场景的持续时间（秒）
            interface: 网络接口名称
        """
        self.output_dir = Path(output_dir)
        self.duration = duration
        self.interface = interface
        self.metadata = []
        
        # 创建目录结构
        self.normal_dir = self.output_dir / 'normal'
        self.replay_dir = self.output_dir / 'replay_attack'
        self.flood_dir = self.output_dir / 'flood_attack'
        
        for dir_path in [self.normal_dir, self.replay_dir, self.flood_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_tshark_command(self):
        """获取 tshark 命令"""
        system = platform.system()
        
        if system == 'Windows':
            # Windows 上使用 Loopback 接口
            interface = 'Adapter for loopback traffic capture'
        else:
            # Linux/Mac 使用 lo
            interface = self.interface
        
        return ['tshark', '-i', interface, '-f', 'udp port 5683']
    
    def start_capture(self, output_file):
        """启动 tshark 捕获"""
        cmd = self.get_tshark_command() + ['-w', str(output_file)]
        logger.info(f"启动捕获: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)  # 等待 tshark 启动
            return process
        except FileNotFoundError:
            logger.error("未找到 tshark，请确保已安装 Wireshark")
            logger.error("Windows: 下载 https://www.wireshark.org/download.html")
            logger.error("Linux: sudo apt-get install tshark")
            return None
    
    def stop_capture(self, process):
        """停止 tshark 捕获"""
        if process:
            logger.info("停止捕获...")
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()
    
    async def collect_normal_traffic(self, count=20, interval=2):
        """采集正常流量"""
        logger.info("=" * 60)
        logger.info("场景 1: 采集正常流量")
        logger.info("=" * 60)
        
        output_file = self.normal_dir / f'normal_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pcap'
        
        # 启动捕获
        capture_process = self.start_capture(output_file)
        if not capture_process:
            return False
        
        try:
            # 发送正常请求
            logger.info(f"发送 {count} 个正常请求，间隔 {interval} 秒...")
            
            import aiocoap
            context = await aiocoap.Context.create_client_context()
            
            for i in range(count):
                try:
                    request = aiocoap.Message(
                        code=aiocoap.GET,
                        uri="coap://localhost/sensor"
                    )
                    await asyncio.wait_for(
                        context.request(request).response,
                        timeout=5.0
                    )
                    logger.info(f"  发送请求 {i+1}/{count}")
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.warning(f"  请求失败: {e}")
            
            await context.shutdown()
            
        finally:
            # 停止捕获
            time.sleep(2)
            self.stop_capture(capture_process)
        
        # 记录元数据
        self.metadata.append({
            'filename': output_file.name,
            'label': 0,
            'attack_type': 'normal',
            'duration_sec': count * interval,
            'request_rate': 1.0 / interval,
            'concurrent': 1,
            'payload_size': 0,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"✓ 正常流量已保存: {output_file}")
        return True
    
    def collect_replay_attack(self, rate=20):
        """采集重放攻击流量"""
        logger.info("=" * 60)
        logger.info(f"场景 2: 采集重放攻击流量 (速率: {rate} req/s)")
        logger.info("=" * 60)
        
        output_file = self.replay_dir / f'replay_r{rate}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pcap'
        
        # 启动捕获
        capture_process = self.start_capture(output_file)
        if not capture_process:
            return False
        
        try:
            # 执行重放攻击
            logger.info(f"执行重放攻击，持续 {self.duration} 秒...")
            cmd = [
                'python', 'coap_replay_attack.py',
                'coap://localhost/sensor',
                '-d', str(self.duration),
                '-r', str(rate)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"重放攻击执行失败: {result.stderr}")
                return False
            
        finally:
            # 停止捕获
            time.sleep(2)
            self.stop_capture(capture_process)
        
        # 记录元数据
        self.metadata.append({
            'filename': output_file.name,
            'label': 1,
            'attack_type': 'replay',
            'duration_sec': self.duration,
            'request_rate': rate,
            'concurrent': 1,
            'payload_size': 50,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"✓ 重放攻击流量已保存: {output_file}")
        return True
    
    def collect_flood_attack(self, rate=50, concurrent=20):
        """采集泛洪攻击流量"""
        logger.info("=" * 60)
        logger.info(f"场景 3: 采集泛洪攻击流量 (速率: {rate} req/s, 并发: {concurrent})")
        logger.info("=" * 60)
        
        output_file = self.flood_dir / f'flood_r{rate}_c{concurrent}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pcap'
        
        # 启动捕获
        capture_process = self.start_capture(output_file)
        if not capture_process:
            return False
        
        try:
            # 执行泛洪攻击
            logger.info(f"执行泛洪攻击，持续 {self.duration} 秒...")
            cmd = [
                'python', 'coap_flood_attack.py',
                'coap://localhost/sensor',
                '-d', str(self.duration),
                '-r', str(rate),
                '-c', str(concurrent)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"泛洪攻击执行失败: {result.stderr}")
                return False
            
        finally:
            # 停止捕获
            time.sleep(2)
            self.stop_capture(capture_process)
        
        # 记录元数据
        self.metadata.append({
            'filename': output_file.name,
            'label': 2,
            'attack_type': 'flood',
            'duration_sec': self.duration,
            'request_rate': rate,
            'concurrent': concurrent,
            'payload_size': 100,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"✓ 泛洪攻击流量已保存: {output_file}")
        return True
    
    def save_metadata(self):
        """保存元数据到 CSV"""
        metadata_file = self.output_dir / 'metadata.csv'
        
        with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
            if self.metadata:
                writer = csv.DictWriter(f, fieldnames=self.metadata[0].keys())
                writer.writeheader()
                writer.writerows(self.metadata)
        
        logger.info(f"✓ 元数据已保存: {metadata_file}")
    
    async def run_full_collection(self):
        """运行完整的数据采集流程"""
        logger.info("=" * 60)
        logger.info("CoAP 攻击数据集自动采集")
        logger.info("=" * 60)
        logger.info(f"输出目录: {self.output_dir}")
        logger.info(f"场景持续时间: {self.duration} 秒")
        logger.info("=" * 60)
        
        # 检查服务器
        logger.info("\n检查 CoAP 服务器...")
        import aiocoap
        try:
            context = await aiocoap.Context.create_client_context()
            request = aiocoap.Message(code=aiocoap.GET, uri="coap://localhost/sensor")
            await asyncio.wait_for(context.request(request).response, timeout=2.0)
            await context.shutdown()
            logger.info("✓ CoAP 服务器正在运行")
        except:
            logger.error("✗ 无法连接到 CoAP 服务器")
            logger.error("请先启动: python test_server.py")
            return
        
        # 场景 1: 正常流量
        await self.collect_normal_traffic(count=20, interval=2)
        await asyncio.sleep(5)
        
        # 场景 2: 重放攻击（多种速率）
        for rate in [5, 20, 50]:
            self.collect_replay_attack(rate=rate)
            time.sleep(5)
        
        # 场景 3: 泛洪攻击（多种配置）
        configs = [
            (20, 10),   # 低速率
            (50, 20),   # 中速率
            (100, 30),  # 高速率
        ]
        for rate, concurrent in configs:
            self.collect_flood_attack(rate=rate, concurrent=concurrent)
            time.sleep(5)
        
        # 保存元数据
        self.save_metadata()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ 数据集采集完成！")
        logger.info("=" * 60)
        logger.info(f"总共采集 {len(self.metadata)} 个 PCAP 文件")
        logger.info(f"数据集位置: {self.output_dir}")
        logger.info("=" * 60)


async def main():
    parser = argparse.ArgumentParser(
        description='CoAP 攻击数据集自动采集工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--output-dir', default='./CoAP_Dataset',
                       help='输出目录 (默认: ./CoAP_Dataset)')
    parser.add_argument('--duration', type=int, default=30,
                       help='每个场景持续时间（秒） (默认: 30)')
    parser.add_argument('--interface', default='lo',
                       help='网络接口名称 (默认: lo)')
    
    args = parser.parse_args()
    
    collector = DatasetCollector(
        output_dir=args.output_dir,
        duration=args.duration,
        interface=args.interface
    )
    
    await collector.run_full_collection()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n数据采集被用户中断")

