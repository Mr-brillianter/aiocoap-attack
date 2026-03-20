#!/usr/bin/env python3
"""
运行流程：
1. 启动 attacker.py
2. 等待 0.5 秒
3. 运行 client.py
4. client 完成后关闭 attacker
"""
import subprocess
import time
import sys

def main():
    attacker = subprocess.Popen([sys.executable, "attacker.py"])
    print(f"attacker.py 已启动 (PID: {attacker.pid})")
    
    time.sleep(0.5)
    print("启动 client.py...")
    
    client = subprocess.run([sys.executable, "client.py"])
    
    print("client.py 完成，关闭 attacker...")
    attacker.terminate()
    attacker.wait()
    print("attacker.py 已关闭")

if __name__ == "__main__":
    main()
