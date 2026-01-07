#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoAP 攻击演示脚本 (CoAP Attack Demo Script)

自动演示重放攻击和泛洪攻击的效果。
需要先启动 test_server.py

使用方法:
    python demo_attacks.py
"""

import asyncio
import subprocess
import sys
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_server_running():
    """检查测试服务器是否运行"""
    try:
        import aiocoap
        context = await aiocoap.Context.create_client_context()
        try:
            request = aiocoap.Message(code=aiocoap.GET, uri="coap://localhost/sensor")
            response = await asyncio.wait_for(
                context.request(request).response,
                timeout=2.0
            )
            logger.info("✓ 测试服务器正在运行")
            return True
        except asyncio.TimeoutError:
            logger.error("✗ 无法连接到测试服务器")
            return False
        finally:
            await context.shutdown()
    except Exception as e:
        logger.error(f"✗ 检查服务器时出错: {e}")
        return False


def run_attack(script_name, args):
    """运行攻击脚本"""
    cmd = [sys.executable, script_name] + args
    logger.info(f"\n{'='*60}")
    logger.info(f"运行: {' '.join(cmd)}")
    logger.info(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"脚本执行失败: {e}")
        return False
    except KeyboardInterrupt:
        logger.info("\n演示被用户中断")
        return False


async def get_server_stats():
    """获取服务器统计信息"""
    try:
        import aiocoap
        context = await aiocoap.Context.create_client_context()
        try:
            request = aiocoap.Message(code=aiocoap.GET, uri="coap://localhost/stats")
            response = await asyncio.wait_for(
                context.request(request).response,
                timeout=2.0
            )
            logger.info("\n" + "="*60)
            logger.info("服务器统计信息:")
            logger.info("="*60)
            logger.info(response.payload.decode('utf-8'))
            logger.info("="*60)
        finally:
            await context.shutdown()
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")


async def main():
    """主演示流程"""
    logger.info("="*60)
    logger.info("CoAP 攻击演示程序")
    logger.info("="*60)
    logger.info("本演示将依次运行以下攻击:")
    logger.info("1. 重放攻击 (10秒, 5请求/秒)")
    logger.info("2. 泛洪攻击 (10秒, 20请求/秒)")
    logger.info("="*60)
    
    # 检查服务器
    logger.info("\n检查测试服务器状态...")
    if not await check_server_running():
        logger.error("\n请先启动测试服务器:")
        logger.error("  python test_server.py")
        return
    
    # 等待用户确认
    logger.info("\n准备开始演示...")
    logger.info("按 Enter 继续，或 Ctrl+C 取消...")
    try:
        input()
    except KeyboardInterrupt:
        logger.info("\n演示已取消")
        return
    
    # 演示 1: 重放攻击
    logger.info("\n" + "🎯 演示 1: 重放攻击".center(60, "="))
    logger.info("重放攻击会捕获一个请求并重复发送...")
    time.sleep(2)
    
    success = run_attack(
        "coap_replay_attack.py",
        ["coap://localhost/sensor", "-d", "10", "-r", "5"]
    )
    
    if not success:
        logger.error("重放攻击演示失败")
        return
    
    # 显示统计
    await get_server_stats()
    
    # 等待
    logger.info("\n等待 3 秒后继续...")
    time.sleep(3)
    
    # 演示 2: 泛洪攻击
    logger.info("\n" + "🎯 演示 2: 泛洪攻击".center(60, "="))
    logger.info("泛洪攻击会发送大量请求...")
    time.sleep(2)
    
    success = run_attack(
        "coap_flood_attack.py",
        ["coap://localhost/sensor", "-d", "10", "-r", "20", "-c", "10"]
    )
    
    if not success:
        logger.error("泛洪攻击演示失败")
        return
    
    # 显示最终统计
    await get_server_stats()
    
    # 演示完成
    logger.info("\n" + "="*60)
    logger.info("✓ 演示完成！")
    logger.info("="*60)
    logger.info("\n你可以尝试:")
    logger.info("1. 修改攻击参数以测试不同强度")
    logger.info("2. 同时运行多个攻击脚本")
    logger.info("3. 实现防御机制并测试效果")
    logger.info("\n详细文档:")
    logger.info("  - QUICKSTART.md - 快速开始指南")
    logger.info("  - ATTACK_SCRIPTS_README.md - 详细使用文档")
    logger.info("  - ATTACK_TOOLS_SUMMARY.md - 工具总结")
    logger.info("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\n演示被用户中断")
    except Exception as e:
        logger.error(f"\n演示过程中出错: {e}")
        import traceback
        traceback.print_exc()

