#!/usr/bin/env python3
"""
CoAP Token 重用攻击 - MITM 演示
演示如何通过中间人代理实现 Token 重用攻击

运行步骤:
1. 启动服务器: python server.py
2. 启动攻击者: python attacker.py
3. 运行此演示: python demo_mitm_attack.py
"""
import asyncio
import logging
from datetime import datetime
from aiocoap import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MITM-Demo")


class CoAPClient:
    """CoAP 客户端（通过攻击者代理连接服务器）"""
    
    def __init__(self, proxy_url="coap://127.0.0.1:5684"):
        """
        初始化客户端
        
        Args:
            proxy_url: 攻击者代理地址（不是真实服务器地址！）
        """
        self.proxy_url = proxy_url
        self.context = None
        
        logger.info("="*70)
        logger.info("CoAP 客户端（通过 MITM 代理）")
        logger.info("="*70)
        logger.info(f"代理地址: {proxy_url}")
        logger.info("="*70)
    
    async def send_request(self, path="/time", request_num=1):
        """
        发送 CoAP 请求
        
        Args:
            path: 请求路径
            request_num: 请求编号
        """
        if not self.context:
            self.context = await Context.create_client_context()
        
        # 构造请求
        request = Message(code=GET, uri=f"{self.proxy_url}{path}")
        
        logger.info("="*70)
        logger.info(f"📤 [请求 #{request_num}] 发送到代理")
        logger.info(f"   URI: {self.proxy_url}{path}")
        logger.info(f"   Token: {request.token.hex() if request.token else 'none'}")
        
        try:
            # 发送请求并等待响应
            response = await asyncio.wait_for(
                self.context.request(request).response,
                timeout=10.0
            )
            
            logger.info(f"📥 [响应 #{request_num}] 收到响应")
            logger.info(f"   Token: {response.token.hex() if response.token else 'none'}")
            logger.info(f"   状态: {response.code}")
            logger.info(f"   数据: {response.payload.decode()}")
            logger.info("="*70)
            
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"⚠️  [请求 #{request_num}] 超时！")
            logger.info("="*70)
            return None
        except Exception as e:
            logger.error(f"⚠️  [请求 #{request_num}] 错误: {e}")
            logger.info("="*70)
            return None
    
    async def close(self):
        """关闭客户端"""
        if self.context:
            await self.context.shutdown()


async def main():
    """主函数 - 演示 MITM 攻击"""
    
    print("\n" + "="*70)
    print("CoAP Token 重用攻击 - MITM 演示")
    print("="*70)
    print()
    print("📋 攻击流程:")
    print("  1. 客户端发送请求 A → 攻击者 → 服务器")
    print("  2. 服务器响应 A' → 攻击者（缓存，不转发）")
    print("  3. 客户端超时，发送请求 B（相同 Token）→ 攻击者 → 服务器")
    print("  4. 服务器响应 B' → 攻击者 → 客户端")
    print("  5. 攻击者延迟后重放 A' → 客户端（客户端误认为是新响应）")
    print("="*70)
    print()
    
    # 创建客户端（连接到攻击者代理，而不是真实服务器）
    client = CoAPClient(proxy_url="coap://127.0.0.1:5684")
    
    try:
        # 第一个请求 - 响应会被攻击者缓存
        logger.info("🚀 发送第一个请求...")
        response1 = await client.send_request(path="/time", request_num=1)
        
        if not response1:
            logger.warning("第一个请求超时（预期行为，因为攻击者缓存了响应）")
        
        # 等待一段时间
        logger.info("\n⏳ 等待 2 秒...")
        await asyncio.sleep(2)
        
        # 第二个请求 - 使用相同的 Token
        logger.info("\n🚀 发送第二个请求（相同 Token）...")
        response2 = await client.send_request(path="/time", request_num=2)
        
        if response2:
            logger.info(f"\n✅ 收到第二个请求的响应: {response2.payload.decode()}")
        
        # 等待攻击者重放旧响应
        logger.info("\n⏳ 等待攻击者重放旧响应...")
        logger.info("   （攻击者会在 5 秒后重放第一个请求的响应）")
        await asyncio.sleep(6)
        
        logger.info("\n" + "="*70)
        logger.info("✅ 演示完成！")
        logger.info("="*70)
        logger.info("")
        logger.info("📊 观察结果:")
        logger.info("  - 第一个请求的响应被攻击者缓存")
        logger.info("  - 第二个请求正常收到响应")
        logger.info("  - 攻击者延迟后重放了第一个请求的旧响应")
        logger.info("  - 客户端可能会将旧响应误认为是新请求的响应")
        logger.info("="*70)
        
    finally:
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")

