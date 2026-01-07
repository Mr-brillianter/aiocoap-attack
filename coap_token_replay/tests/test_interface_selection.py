#!/usr/bin/env python3
"""
测试网络接口选择功能
"""
from scapy.all import *
import platform

print("="*60)
print("网络接口测试")
print("="*60)

print(f"\n操作系统: {platform.system()}")
print(f"默认接口: {conf.iface}")

print("\n所有可用的网络接口:")
interfaces = get_if_list()

for i, iface in enumerate(interfaces):
    # 尝试获取接口的更多信息
    try:
        # 高亮显示特殊接口
        if "Loopback" in iface or iface == "lo":
            marker = " ← 本地回环接口 (推荐用于本地测试)"
        elif iface == conf.iface:
            marker = " ← 当前默认接口"
        else:
            marker = ""
        
        print(f"  {i+1}. {iface}{marker}")
        
    except Exception as e:
        print(f"  {i+1}. {iface}")

print("\n" + "="*60)
print("提示:")
print("  - 对于本地 CoAP 服务器测试，选择 Loopback 接口")
print("  - 对于网络上的 CoAP 服务器，选择对应的网络接口")
print("="*60)

