#!/usr/bin/env python3
"""
完整的攻击测试脚本
"""
import asyncio
import subprocess
import time
import signal
import sys

def run_command(command):
    """运行命令行命令"""
    print(f"执行: {command}")
    return subprocess.Popen(command, shell=True)

async def test_token_replay_attack():
    """测试令牌重用攻击"""
    print("="*60)
    print("CoAP令牌重用攻击测试")
    print("="*60)
    
    # 1. 启动CoAP服务器
    print("\n[1/4] 启动CoAP服务器...")
    server_proc = run_command("python3 server.py")
    time.sleep(2)
    
    # 2. 启动攻击者
    print("\n[2/4] 启动攻击者程序...")
    attacker_proc = run_command("python3 attacker.py")
    time.sleep(2)
    
    # 3. 运行易受攻击的客户端
    print("\n[3/4] 运行易受攻击的客户端...")
    print("注意观察客户端的日志输出，将看到:")
    print("  - 第一次请求的响应被延迟")
    print("  - 客户端使用相同Token发送第二次请求")
    print("  - 攻击者重放旧响应")
    print("  - 客户端混淆请求-响应对应关系")
    
    client_proc = run_command("python3 client.py")
    
    # 等待客户端完成
    time.sleep(10)
    
    # 4. 清理
    print("\n[4/4] 清理进程...")
    for proc in [server_proc, attacker_proc, client_proc]:
        if proc:
            proc.terminate()
    
    print("\n测试完成！")

def mitigation_recommendations():
    """防御建议"""
    print("\n" + "="*60)
    print("防御令牌重用攻击的建议")
    print("="*60)
    print("1. Token生成策略:")
    print("   - 使用密码学安全的随机数生成器生成Token")
    print("   - 每个请求使用唯一的Token")
    print("   - 避免Token可预测或重用")
    
    print("\n2. 协议增强:")
    print("   - 实现请求-响应绑定机制")
    print("   - 使用序列号或时间戳")
    print("   - 在TLS/DTLS上启用通道绑定")
    
    print("\n3. 实现检查:")
    print("   - 验证Token的唯一性")
    print("   - 设置Token最大使用次数限制")
    print("   - 实现响应新鲜性检查")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--defense":
        mitigation_recommendations()
    else:
        asyncio.run(test_token_replay_attack())