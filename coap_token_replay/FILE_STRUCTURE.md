# CoAP Token 重用攻击 - 文件结构说明

## 📁 完整文件结构

```
coap_token_replay/
│
├── 📄 主文档（根目录）
│   ├── README.md                  # 项目主文档
│   ├── HOW_TO_RUN.md              # 运行指南
│   ├── SERVER_USAGE.md            # 服务器使用说明
│   ├── PROJECT_SUMMARY.md         # 项目总结
│   └── FILE_STRUCTURE.md          # 本文件
│
├── 🐍 Python 脚本（根目录）
│   ├── server.py                  # CoAP 服务器
│   ├── client.py                  # 客户端（包含 Monkey Patch）
│   ├── attacker.py                # 攻击者程序
│   ├── demo_token_reuse_attack.py # Token 重用攻击演示
│   ├── demo_interface_usage.py    # 接口使用演示
│   ├── quick_test.py              # 快速测试脚本
│   └── test_server.py             # 服务器测试
│
├── 📚 docs/ - 文档目录
│   ├── INDEX.md                   # 文档索引和导航
│   ├── QUICK_START_TOKEN_REUSE.md # 快速开始指南
│   ├── TOKEN_REUSE_FIX_SUMMARY.md # Token 重用修复总结
│   ├── FINAL_SOLUTION.md          # 最终解决方案
│   ├── QUICK_START.md             # 通用快速开始
│   ├── USAGE.md                   # 使用说明
│   ├── README_FIXED.md            # 修复说明
│   └── README_OLD_BACKUP.md       # 旧 README 备份
│
├── 🧪 tests/ - 测试目录
│   ├── README.md                  # 测试说明
│   ├── test_monkey_patch.py       # Monkey Patch 测试
│   ├── test_token_parameter.py    # Token 参数测试
│   ├── test_client_simple.py      # 简单客户端测试
│   ├── test_attack.py             # 攻击测试
│   ├── test_attacker_import.py    # 攻击者导入测试
│   └── test_interface_selection.py # 接口选择测试
│
├── 📝 logs/ - 日志目录
│   └── (运行时生成的日志文件)
│
└── 📦 resources/ - 资源目录
    └── (资源文件)
```

## 📋 文件分类

### 核心文件（必需）

| 文件 | 说明 | 重要性 |
|------|------|--------|
| `server.py` | CoAP 服务器 | ⭐⭐⭐ |
| `client.py` | 客户端（包含 Monkey Patch） | ⭐⭐⭐ |
| `demo_token_reuse_attack.py` | Token 重用攻击演示 | ⭐⭐⭐ |
| `README.md` | 项目主文档 | ⭐⭐⭐ |

### 文档文件

| 文件 | 说明 | 适合人群 |
|------|------|----------|
| `README.md` | 项目主文档 | 所有人 |
| `HOW_TO_RUN.md` | 运行指南 | 初学者 |
| `SERVER_USAGE.md` | 服务器使用说明 | 开发者 |
| `PROJECT_SUMMARY.md` | 项目总结 | 所有人 |
| `FILE_STRUCTURE.md` | 文件结构说明（本文件） | 所有人 |
| `docs/INDEX.md` | 文档索引 | 所有人 |
| `docs/QUICK_START_TOKEN_REUSE.md` | 快速开始 | 初学者 |
| `docs/TOKEN_REUSE_FIX_SUMMARY.md` | 技术细节 | 开发者 |
| `docs/FINAL_SOLUTION.md` | 完整方案 | 所有人 |
| `tests/README.md` | 测试说明 | 开发者 |

### 测试文件

| 文件 | 说明 | 测试内容 |
|------|------|----------|
| `tests/test_monkey_patch.py` | Monkey Patch 测试 | Token 保留功能 |
| `tests/test_token_parameter.py` | Token 参数测试 | 不同参数设置 |
| `tests/test_client_simple.py` | 简单客户端测试 | 基本功能 |
| `tests/test_attack.py` | 攻击测试 | 完整攻击流程 |
| `tests/test_attacker_import.py` | 导入测试 | 模块导入 |
| `tests/test_interface_selection.py` | 接口测试 | 网络接口 |

### 演示文件

| 文件 | 说明 | 用途 |
|------|------|------|
| `demo_token_reuse_attack.py` | Token 重用攻击演示 | 主要演示 |
| `demo_interface_usage.py` | 接口使用演示 | 接口选择 |
| `quick_test.py` | 快速测试 | 服务器测试 |
| `test_server.py` | 服务器测试 | 服务器功能 |

### 辅助文件

| 文件 | 说明 |
|------|------|
| `attacker.py` | 攻击者程序（传统方式） |
| `logs/` | 日志目录 |
| `resources/` | 资源目录 |
| `__pycache__/` | Python 缓存 |

## 🎯 快速查找

### 我想...

**运行演示**
- 查看：`README.md` 或 `docs/QUICK_START_TOKEN_REUSE.md`
- 运行：`server.py` + `demo_token_reuse_attack.py`

**了解技术细节**
- 查看：`docs/TOKEN_REUSE_FIX_SUMMARY.md`
- 代码：`client.py`（Monkey Patch 部分）

**运行测试**
- 查看：`tests/README.md`
- 运行：`tests/test_monkey_patch.py`

**配置服务器**
- 查看：`SERVER_USAGE.md`
- 代码：`server.py`

**查看所有文档**
- 查看：`docs/INDEX.md`

## 📊 文件统计

### 按类型

- **Python 文件**: 13 个
- **Markdown 文档**: 12 个
- **测试文件**: 6 个
- **演示文件**: 4 个

### 按目录

- **根目录**: 12 个文件
- **docs/**: 8 个文件
- **tests/**: 7 个文件（包括 README）
- **总计**: 27 个文件

## 🔍 文件依赖关系

```
server.py
    ↑
    │ (CoAP 请求)
    │
client.py ←→ demo_token_reuse_attack.py
    ↑
    │ (使用)
    │
tests/test_*.py
```

## 📝 维护建议

### 添加新功能

1. 在根目录添加 Python 脚本
2. 在 `docs/` 添加相关文档
3. 在 `tests/` 添加测试
4. 更新 `README.md` 和 `docs/INDEX.md`

### 添加新文档

1. 在 `docs/` 目录创建文档
2. 更新 `docs/INDEX.md`
3. 在 `README.md` 添加链接

### 添加新测试

1. 在 `tests/` 目录创建测试
2. 更新 `tests/README.md`
3. 确保测试可以独立运行

## ⚠️ 注意事项

1. **不要删除核心文件**：`server.py`, `client.py`, `demo_token_reuse_attack.py`
2. **保持文档同步**：修改代码后更新相关文档
3. **测试独立性**：每个测试应该可以独立运行
4. **文档清晰性**：确保文档易于理解

---

**最后更新**: 2026-01-03
**版本**: 1.0.0

