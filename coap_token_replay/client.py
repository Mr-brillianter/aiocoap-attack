#!/usr/bin/env python3
"""
CoAP 客户端 - 使用原始 UDP 实现 Token 重放攻击演示
"""
import socket
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Client")

def make_coap_request(token, path=b"/time", mid=0x1234):
    """构造 CoAP GET 请求"""
    tkl = len(token)
    # CoAP header: Ver=1(2bit), Type=CON(0), TKL(4bit)
    # Byte 0: Ver=01, Type=00(CON), TKL=token长度
    # Code=0.01 (GET), Message ID (16bit)
    # 0x40 = Ver=1(01), Type=CON(00), TKL=0; | tkl 设置 Token 长度
    header = bytes([0x40 | (tkl & 0x0F), 0x01]) + mid.to_bytes(2, 'big')
    # Options: Uri-Path Option 11 (Delta=11, Length=path长度)
    # 0xB4 = 1011 0100 = delta=11, length=4; 0xB5 = delta=11, length=5
    opt_header = 0xB0 | (len(path) & 0x0F)  # 动态计算 length
    options = bytes([opt_header]) + path
    return header + token + options + b'\xff'

async def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)  # 缩短超时，便于接收循环
    proxy = ("127.0.0.1", 5684)
    
    # 固定 Token
    token = b'\xaa\xbb'
    
    print("\n" + "="*50)
    print("CoAP Token 重放攻击演示")
    print("="*50)
    
    # 用于存储接收到的响应
    received_responses = []
    stop_receiver = False
    
    async def receiver():
        """独立接收协程：持续监听响应（使用 run_in_executor 避免阻塞事件循环）"""
        loop = asyncio.get_event_loop()
        logger.info("[接收器] 启动")
        while not stop_receiver:
            try:
                data, _ = await loop.run_in_executor(None, sock.recvfrom, 4096)
                received_responses.append(data)
                logger.info(f"[接收器] 收到响应 | 数据: {data.hex()}")
            except socket.timeout:
                continue  # 超时后继续循环
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[接收器] 错误: {e}")
                break
        logger.info("[接收器] 关闭")
    
    # 启动接收协程
    receiver_task = asyncio.create_task(receiver())
    await asyncio.sleep(0.1)  # 短暂等待接收协程启动
    
    async def request(n, delay=0):
        if delay:
            await asyncio.sleep(delay)
        req = make_coap_request(token)
        logger.info(f"发送请求 #{n} | Token: {token.hex()}")
        sock.sendto(req, proxy)
    
    # 第一次请求（攻击者缓存）
    await request(1)
    await asyncio.sleep(2)  # 等待足够长的时间让响应到达
    
    # 1秒后第二次请求
    await request(2, delay=1)
    await asyncio.sleep(2)  # 等待响应
    
    # 等待重放
    print("\n等待攻击者重放旧响应...\n")
    await asyncio.sleep(10)  # 等待重放发生
    
    # 停止接收协程
    stop_receiver = True
    receiver_task.cancel()
    try:
        await receiver_task
    except asyncio.CancelledError:
        pass
    
    # 显示收到的所有响应
    print(f"\n共收到 {len(received_responses)} 个响应:")
    for i, resp in enumerate(received_responses, 1):
        print(f"  响应 #{i}: {resp.hex()}")
    
    print("="*50)
    print("演示完成")
    print("="*50)
    sock.close()

if __name__ == "__main__":
    asyncio.run(main())
