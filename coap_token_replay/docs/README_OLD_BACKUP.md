# CoAP令牌重用攻击模拟实验

## ✅ 项目状态

**所有问题已修复！** 项目现在可以正常运行。

- ✅ **attacker.py** - 已修复所有导入和异步问题
- ✅ **server.py** - 已完全重写，使用正确的 aiocoap Resource 类
- ✅ **client.py** - 工作正常
- ✅ **测试脚本** - 已添加完整的测试套件
- ✅ **文档** - 已添加详细的使用说明

**快速开始**: 查看 [`HOW_TO_RUN.md`](HOW_TO_RUN.md) 获取详细的运行指南。

---

## 概述
本实验模拟了CoAP协议中的令牌重用攻击，展示在缺乏强请求绑定机制时，CoAP客户端错误使用Token字段可能引发的安全风险。攻击通过延迟和重放响应，破坏请求-响应对应关系，导致客户端处理错误的响应数据。

## 目录结构
```
coap_token_replay/
├── README.md          # 本文件
├── attacker.py        # 攻击者脚本（模拟网络攻击者）
├── client.py          # CoAP客户端（包含漏洞的实现）
├── server.py          # CoAP服务器（正常响应）
├── test_attack.py     # 完整测试脚本
├── requirements.txt   # Python依赖
├── resources/         # 资源文件目录
└── logs/             # 运行日志目录
```

## 环境准备

### 1. 安装CoAP工具
```bash
sudo apt-get update

# 安装Python CoAP库 scapy库
pip install aiocoap scapy
```

### 2. 依赖文件
创建`requirements.txt`：
```
aiocoap>=0.4.3
scapy>=2.4.5
```

安装依赖：
```bash
pip install -r requirements.txt
```

## 快速开始

### 步骤1：启动CoAP服务器
```bash
# 终端1 - 启动服务器
python3 server.py
```
**输出示例：**
```
INFO:CoAP-Server:CoAP服务器启动在 coap://127.0.0.1:5683
```

### 步骤2：启动攻击者程序
```bash
# 终端2 - 启动攻击者（需要管理员权限）
sudo python3 attacker.py
```
选择攻击模式：
```
选择攻击模式:
1. 自动嗅探和攻击
2. 查看攻击步骤说明
3. 手动构造攻击数据包
请输入选择 (1-3): 1
```

### 步骤3：运行易受攻击的客户端
```bash
# 终端3 - 运行客户端
python3 client.py
```

## 攻击执行流程

### 预期攻击效果
```
==================================================
开始模拟令牌重用攻击场景
==================================================

1. 第一次请求（响应将被攻击者延迟）
[时间戳] 发送请求#1 - 路径: toggle, Token: 6669786564313233

2. 第二次请求（使用相同的Token）
[时间戳] 发送请求#2 - 路径: toggle, Token: 6669786564313233

[攻击者日志] 捕获Token为 6669786564313233 的响应，将延迟发送
[攻击者日志] 等待5秒后重放Token为 6669786564313233 的响应...

[客户端日志] 收到响应#1 - Token: 6669786564313233, 数据: 状态已切换 - 请求#1
[客户端日志] 收到响应#2 - Token: 6669786564313233, 数据: 状态已切换 - 请求#2
[攻击者日志] 重放旧响应！Token: 6669786564313233
[客户端日志] 收到响应#3 - Token: 6669786564313233, 数据: 状态已切换 - 请求#1
```

### 攻击关键点

1. **Token固定/可预测**  
   - 客户端使用固定Token：`b'fixed123'`
   - 或使用可预测的生成方式

2. **响应捕获与延迟**  
   - 攻击者嗅探网络流量
   - 捕获特定Token的响应
   - 延迟发送（模拟网络延迟）

3. **Token重用**  
   - 客户端在第二个请求中重用相同Token
   - 服务器无法区分不同请求的Token

4. **响应重放与错误匹配**  
   - 攻击者重放旧的响应
   - 客户端错误地将旧响应关联到新请求
   - 导致状态不一致或逻辑错误

## 程序功能说明

### 1. server.py - CoAP服务器
- 监听端口：5683
- 提供资源：`/toggle`、`/status`
- 记录请求计数并返回差异化响应
- 模拟网络延迟场景

### 2. client.py - 易受攻击的客户端
- 包含漏洞的Token生成机制
- 支持多种Token生成策略
- 模拟攻击场景的请求序列
- 详细的请求/响应日志

### 3. attacker.py - 攻击者程序
- 网络流量嗅探（使用Scapy）
- CoAP协议包解析
- 响应捕获与延迟机制
- 手动/自动攻击模式

### 4. test_attack.py - 集成测试脚本
```bash
# 运行完整测试
python3 test_attack.py

# 查看防御建议
python3 test_attack.py --defense
```

## 漏洞分析

### 攻击原理
CoAP协议依赖Token字段匹配请求和响应，当：
1. 客户端重用Token
2. 攻击者可延迟/重排序报文
3. 缺乏请求-响应绑定机制

导致旧响应被错误关联到新请求，引发状态不一致。

### 影响范围
- IoT设备（智能家居、工业控制）
- 状态敏感的操作（门锁控制、设备开关）
- 需要精确请求-响应匹配的场景

## 防御措施

### 在client.py中修复
```python
# 安全Token生成
import os
import secrets

def generate_secure_token():
    """生成安全的随机Token"""
    return secrets.token_bytes(8)  # 8字节随机Token

# 每个请求使用唯一Token
token = generate_secure_token()
```

### 推荐防御策略
1. **Token管理**
   - 每个请求生成唯一随机Token
   - 使用密码学安全的随机数生成器
   - 设置Token生命周期和最大使用次数

2. **协议增强**
   - 实现请求-响应绑定（如使用序列号）
   - 添加时间戳和新鲜性检查
   - 在DTLS/TLS上启用通道绑定

3. **实现检查**
   - 验证Token的唯一性
   - 检测异常的响应延迟
   - 实施重放攻击防护

## 故障排除

### 常见问题
1. **权限错误**
   ```bash
   sudo: python3: command not found
   ```
   **解决**：使用完整路径或配置sudoers

2. **依赖安装失败**
   ```bash
   pip install aiocoap 失败
   ```
   **解决**：确保Python版本≥3.7，或使用虚拟环境

3. **Scapy权限问题**
   ```bash
   PermissionError: [Errno 1] Operation not permitted
   ```
   **解决**：使用sudo运行攻击者脚本

4. **端口冲突**
   ```bash
   OSError: [Errno 98] Address already in use
   ```
   **解决**：更改端口号或结束占用进程

### 调试模式
```bash
# 启用详细日志
export PYTHONPATH=.
python3 -m logging client.py --log-level=DEBUG
```

## 扩展实验

### 实验1：不同Token策略对比
修改`client.py`中的`generate_token()`函数，测试：
- 固定Token
- 可预测Token（如基于计数器）
- 随机Token

### 实验2：攻击变种
1. **重排序攻击**：交换两个响应的顺序
2. **注入攻击**：伪造响应数据
3. **DoS攻击**：大量重放旧响应

### 实验3：防御机制实现
1. **Token时效性**：添加时间戳和过期检查
2. **序列号绑定**：请求和响应绑定序列号
3. **密码学绑定**：使用HMAC验证请求-响应对应关系

## 参考资料

1. **CoAP协议规范**  
   RFC 7252: The Constrained Application Protocol (CoAP)

2. **安全分析**  
   - "Security Considerations for CoAP" (RFC 7252 §11)
   - "CoAP Attacks and Mitigation" (IoT Security Foundation)

3. **相关工具**  
   - aiocoap: https://github.com/chrysn/aiocoap

## 许可证
本项目仅供教育和研究目的使用。在实际系统中实施攻击需获得明确授权。

---
**注意**：本实验需在隔离的测试环境中进行，避免对生产系统造成影响。