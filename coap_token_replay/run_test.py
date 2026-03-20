#!/usr/bin/env python3
"""一次性运行 server + attacker + client 进行测试"""
import subprocess
import time
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 启动 server
server = subprocess.Popen(
    ["uv", "run", "python", "server.py"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(1)

# 启动 attacker
attacker = subprocess.Popen(
    ["uv", "run", "python", "attacker.py"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(1)

# 运行 client
client = subprocess.Popen(
    ["uv", "run", "python", "client.py"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# 等待 client 完成
try:
    stdout, _ = client.communicate(timeout=15)
    print("=== CLIENT ===")
    print(stdout.decode())
except subprocess.TimeoutExpired:
    client.kill()
    print("Client timeout")

# 等待重放
time.sleep(6)

# 终止 server 和 attacker
server.terminate()
attacker.terminate()

print("=== SERVER ===")
print(server.stdout.read().decode())
print("=== ATTACKER ===")
print(attacker.stdout.read().decode())
