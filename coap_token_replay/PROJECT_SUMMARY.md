# CoAP Token 重用攻击 - 项目总结

## 📊 项目概览

这是一个完整的 CoAP Token 重用攻击演示项目，展示了如何利用固定 Token 进行攻击，以及如何使用 Monkey Patch 绕过 aiocoap 的安全限制。

## 🎯 项目目标

1. ✅ 演示 CoAP Token 重用攻击的原理和危害
2. ✅ 展示如何绕过 aiocoap 的 Token 保护机制
3. ✅ 提供完整的测试套件和文档
4. ✅ 教育开发者关于 Token 安全的重要性

## 📁 项目结构（已整理）

```
coap_token_replay/
├── README.md                      # 主文档
├── HOW_TO_RUN.md                  # 运行指南
├── SERVER_USAGE.md                # 服务器使用说明
├── PROJECT_SUMMARY.md             # 本文件
│
├── server.py                      # CoAP 服务器
├── client.py                      # 客户端（包含 Monkey Patch）
├── attacker.py                    # 攻击者程序
├── demo_token_reuse_attack.py     # Token 重用攻击演示
├── demo_interface_usage.py        # 接口使用演示
├── quick_test.py                  # 快速测试脚本
├── test_server.py                 # 服务器测试
│
├── docs/                          # 📚 文档目录
│   ├── INDEX.md                   # 文档索引
│   ├── QUICK_START_TOKEN_REUSE.md # 快速开始指南
│   ├── TOKEN_REUSE_FIX_SUMMARY.md # Token 重用修复总结
│   ├── FINAL_SOLUTION.md          # 最终解决方案
│   ├── QUICK_START.md             # 通用快速开始
│   ├── USAGE.md                   # 使用说明
│   └── README_FIXED.md            # 修复说明
│
├── tests/                         # 🧪 测试目录
│   ├── README.md                  # 测试说明
│   ├── test_monkey_patch.py       # Monkey Patch 测试
│   ├── test_token_parameter.py    # Token 参数测试
│   ├── test_client_simple.py      # 简单客户端测试
│   ├── test_attack.py             # 攻击测试
│   ├── test_attacker_import.py    # 攻击者导入测试
│   └── test_interface_selection.py # 接口选择测试
│
├── logs/                          # 📝 日志目录
└── resources/                     # 📦 资源目录
```

## 🔧 核心技术

### 1. Monkey Patch 解决方案

**问题**：aiocoap 不允许手动设置 Token

**解决**：修改 `TokenManager.request()` 方法

```python
def _patched_request(self, request):
    # 只在 Token 为空时才分配新 Token
    if not msg.token:
        msg.token = self.next_token()
    # ... 其他代码
```

### 2. Token 重用攻击

**原理**：
1. 客户端使用固定 Token（如 `b'FIXED_TOKEN'`）
2. 攻击者拦截并重放响应
3. 服务器无法区分不同的请求

**演示**：
```
【请求 #1】Token: 56554c4e5f544f4b454e ⚠️ Token 被重用！
【请求 #2】Token: 56554c4e5f544f4b454e ⚠️ Token 被重用！
【请求 #3】Token: 56554c4e5f544f4b454e ⚠️ Token 被重用！
```

## 📚 文档组织

### 主文档（根目录）

- `README.md` - 项目主文档，包含快速开始和概述
- `HOW_TO_RUN.md` - 详细的运行指南
- `SERVER_USAGE.md` - 服务器配置和使用
- `PROJECT_SUMMARY.md` - 项目总结（本文件）

### 技术文档（docs/）

- `INDEX.md` - 文档索引和导航
- `QUICK_START_TOKEN_REUSE.md` - 最简单的快速开始
- `TOKEN_REUSE_FIX_SUMMARY.md` - 技术细节和实现
- `FINAL_SOLUTION.md` - 完整的解决方案
- `QUICK_START.md` - 传统攻击演示
- `USAGE.md` - 详细使用说明
- `README_FIXED.md` - 修复历史

### 测试文档（tests/）

- `README.md` - 测试套件说明
- 各种测试脚本

## 🧪 测试覆盖

| 测试 | 状态 | 说明 |
|------|------|------|
| Monkey Patch | ✅ | 验证 Token 保留功能 |
| Token 参数 | ✅ | 测试不同参数设置 |
| 简单客户端 | ✅ | 基本功能测试 |
| 攻击演示 | ✅ | 完整攻击流程 |
| 接口选择 | ✅ | 网络接口测试 |

## 🎓 学习路径

### 初学者

1. 阅读 `README.md`
2. 跟随 `docs/QUICK_START_TOKEN_REUSE.md` 运行演示
3. 查看 `docs/FINAL_SOLUTION.md` 了解实现

### 开发者

1. 阅读 `docs/TOKEN_REUSE_FIX_SUMMARY.md`
2. 查看 `docs/FINAL_SOLUTION.md`
3. 运行 `tests/` 中的测试

### 安全研究人员

1. 阅读 `docs/TOKEN_REUSE_FIX_SUMMARY.md`
2. 分析 `client.py` 和 `attacker.py`
3. 研究防御措施

## 🛡️ 安全建议

### 防御措施

- ✅ 每个请求使用唯一的随机 Token
- ✅ Token 至少 4 字节，推荐 8 字节
- ✅ 使用加密安全的随机数生成器
- ✅ 实现 Token 过期机制
- ✅ 使用 DTLS/TLS 加密传输

### 为什么 aiocoap 禁止手动设置 Token？

**这是一个安全特性！**

- Token 重用是已知的安全漏洞
- 应用层不应该管理 Token
- 库应该自动确保 Token 的唯一性

## 📊 项目成果

### 已完成

- ✅ 完整的 Token 重用攻击演示
- ✅ Monkey Patch 解决方案
- ✅ 完整的测试套件
- ✅ 详细的文档
- ✅ 清晰的项目结构

### 文件统计

- **Python 文件**: 13 个
- **文档文件**: 11 个
- **测试文件**: 6 个
- **总代码行数**: ~2000 行

## 🔗 快速链接

- **快速开始**: [docs/QUICK_START_TOKEN_REUSE.md](docs/QUICK_START_TOKEN_REUSE.md)
- **技术细节**: [docs/TOKEN_REUSE_FIX_SUMMARY.md](docs/TOKEN_REUSE_FIX_SUMMARY.md)
- **完整方案**: [docs/FINAL_SOLUTION.md](docs/FINAL_SOLUTION.md)
- **测试说明**: [tests/README.md](tests/README.md)
- **文档索引**: [docs/INDEX.md](docs/INDEX.md)

## ⚠️ 免责声明

本项目仅供教育和研究目的使用。请勿在未经授权的系统上使用这些技术。

## 📄 许可证

MIT License - 仅供教育和研究目的使用

---

**最后更新**: 2026-01-03
**版本**: 1.0.0
**状态**: ✅ 完成

