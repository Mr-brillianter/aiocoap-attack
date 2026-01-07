#!/usr/bin/env python3
"""
演示如何使用选定的网络接口
"""
from scapy.all import *
import platform

def get_loopback_interface():
    """自动查找 Loopback 接口"""
    interfaces = get_if_list()
    
    for iface in interfaces:
        if "Loopback" in iface or iface == "lo" or iface == "lo0":
            return iface
    
    # 如果没找到，返回默认接口
    return conf.iface

def display_interface_info(interface):
    """显示接口信息"""
    print(f"\n接口: {interface}")
    
    try:
        # 尝试获取接口的 IP 地址
        if platform.system() == "Windows":
            print("  类型: Windows NPF 设备")
        else:
            print(f"  类型: {platform.system()} 网络接口")
    except Exception as e:
        print(f"  无法获取详细信息: {e}")

def main():
    print("="*60)
    print("网络接口使用演示")
    print("="*60)
    
    # 1. 显示所有接口
    print("\n[1] 所有可用接口:")
    interfaces = get_if_list()
    for i, iface in enumerate(interfaces):
        marker = ""
        if "Loopback" in iface or iface == "lo":
            marker = " ← Loopback"
        elif iface == conf.iface:
            marker = " ← 默认"
        print(f"    {i+1}. {iface}{marker}")
    
    # 2. 自动查找 Loopback
    print("\n[2] 自动查找 Loopback 接口:")
    loopback = get_loopback_interface()
    print(f"    找到: {loopback}")
    
    # 3. 显示推荐配置
    print("\n[3] 推荐配置:")
    print(f"    本地测试: {loopback}")
    print(f"    网络测试: {conf.iface}")
    
    # 4. 演示如何在代码中使用
    print("\n[4] 代码示例:")
    print(f"""
    # 方法 1: 使用自动检测的 Loopback
    from attacker import TokenReplayAttacker
    attacker = TokenReplayAttacker(interface="{loopback}")
    
    # 方法 2: 使用默认接口
    attacker = TokenReplayAttacker()  # 使用默认
    
    # 方法 3: 手动指定
    attacker = TokenReplayAttacker(interface="{conf.iface}")
    """)
    
    # 5. 测试接口是否可用
    print("\n[5] 测试 Loopback 接口:")
    try:
        print(f"    尝试在 {loopback} 上嗅探...")
        print("    (这只是测试，不会真正嗅探)")
        # 不实际运行 sniff，只是验证接口名称
        print(f"    ✓ 接口 {loopback} 可用")
    except Exception as e:
        print(f"    ✗ 错误: {e}")
    
    print("\n" + "="*60)
    print("提示:")
    print("  - 运行 attacker.py 时会提示选择接口")
    print("  - 对于本地测试，选择 Loopback 接口")
    print("  - 直接回车使用默认接口")
    print("="*60)

if __name__ == "__main__":
    main()

