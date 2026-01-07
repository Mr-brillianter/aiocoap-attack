#!/usr/bin/env python3
"""
测试 attacker.py 的导入和基本功能
"""
import sys
import platform

print("="*60)
print("Testing CoAP Attacker Script")
print("="*60)

# Test 1: Import scapy
print("\n[Test 1] Importing scapy...")
try:
    from scapy.all import *
    print("✓ scapy.all imported successfully")
except ImportError as e:
    print(f"✗ Failed to import scapy.all: {e}")
    sys.exit(1)

# Test 2: Import CoAP from scapy.contrib
print("\n[Test 2] Importing CoAP from scapy.contrib...")
try:
    from scapy.contrib.coap import CoAP
    print("✓ CoAP imported successfully from scapy.contrib.coap")
except ImportError as e:
    print(f"✗ Failed to import CoAP: {e}")
    sys.exit(1)

# Test 3: Import attacker module
print("\n[Test 3] Importing TokenReplayAttacker...")
try:
    from attacker import TokenReplayAttacker
    print("✓ TokenReplayAttacker imported successfully")
except ImportError as e:
    print(f"✗ Failed to import TokenReplayAttacker: {e}")
    sys.exit(1)

# Test 4: Create attacker instance
print("\n[Test 4] Creating TokenReplayAttacker instance...")
try:
    attacker = TokenReplayAttacker()
    print(f"✓ TokenReplayAttacker instance created")
    print(f"  - Interface: {attacker.interface}")
    print(f"  - Server port: {attacker.server_port}")
    print(f"  - Client port: {attacker.client_port}")
except Exception as e:
    print(f"✗ Failed to create instance: {e}")
    sys.exit(1)

# Test 5: Test CoAP packet creation
print("\n[Test 5] Testing CoAP packet creation...")
try:
    # CoAP payload is added as Raw layer after CoAP
    fake_response = (IP(src="127.0.0.1", dst="127.0.0.1") /
                    UDP(sport=5683, dport=5684) /
                    CoAP(type="ACK", code=69, token=b'test123') /  # code 69 = "2.05 Content"
                    Raw(load=b"Test payload"))
    print("✓ CoAP packet created successfully")
    print(f"  - Token: {fake_response[CoAP].token.hex()}")
    print(f"  - Type: {fake_response[CoAP].type}")
    print(f"  - Code: {fake_response[CoAP].code}")
except Exception as e:
    print(f"✗ Failed to create CoAP packet: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: System information
print("\n[Test 6] System information...")
print(f"  - OS: {platform.system()}")
print(f"  - Default interface: {conf.iface}")

print("\n" + "="*60)
print("All tests passed! ✓")
print("="*60)

print("\n提示:")
if platform.system() == "Windows":
    print("  - 在Windows上运行嗅探功能需要:")
    print("    1. 安装 Npcap (https://npcap.com/)")
    print("    2. 以管理员权限运行脚本")
else:
    print("  - 在Linux/Mac上运行嗅探功能可能需要 sudo 权限")

print("\n运行攻击脚本:")
print("  python attacker.py")

