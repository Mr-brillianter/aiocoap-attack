#!/usr/bin/env python3
"""
CoAP 消息验证模块
用于验证消息格式是否正确，调试消息解析问题
"""
import logging
from typing import Tuple, Optional, List

logger = logging.getLogger("Validator")

try:
    from aiocoap import Message
    from aiocoap.error import UnparsableMessage as AIOCoapUnparsable
    HAS_AIOCOAP = True
except ImportError:
    HAS_AIOCOAP = False
    logger.warning("aiocoap not available, Message.decode() validation disabled")


def validate_message(data: bytes, label: str = "") -> Tuple[bool, Optional[str]]:
    """
    使用 aiocoap Message.decode() 验证消息格式
    
    Args:
        data: 原始字节数据
        label: 调试标签 (如 "来自客户端", "来自服务器")
    
    Returns:
        (is_valid, error_message)
    """
    if not HAS_AIOCOAP:
        return True, None
    
    if len(data) < 4:
        return False, f"[{label}] 数据太短 ({len(data)} bytes)，需要至少 4 bytes"
    
    try:
        msg = Message.decode(data)
        logger.debug(f"[{label}] 验证通过: code={msg.code}, token={msg.token.hex() if msg.token else 'none'}, mid={msg.mid:#06x}")
        return True, None
    except AIOCoapUnparsable as e:
        return False, f"[{label}] 解析失败: {e}"
    except Exception as e:
        return False, f"[{label}] 未知错误: {type(e).__name__}: {e}"


def bytes_diff(original: bytes, modified: bytes, label: str = "") -> List[str]:
    """
    对比两个字节序列，输出差异详情用于调试
    
    Args:
        original: 原序列
        modified: 修改后的序列
        label: 调试标签
    
    Returns:
        差异描述列表
    """
    diff_lines = []
    prefix = f"[{label}] " if label else ""
    
    if original == modified:
        diff_lines.append(f"{prefix}序列相同，无差异")
        return diff_lines
    
    diff_lines.append(f"{prefix}序列长度: {len(original)} -> {len(modified)}")
    
    # 找出第一个差异位置
    min_len = min(len(original), len(modified))
    first_diff = 0
    for i in range(min_len):
        if original[i] != modified[i]:
            first_diff = i
            break
    
    # 打印头部（相同部分）
    if first_diff > 0:
        context = original[max(0, first_diff-2):first_diff+4]
        diff_lines.append(f"{prefix}位置 {first_diff} 前: {context.hex()}")
    
    # 打印差异区域
    diff_lines.append(f"{prefix}===== 差异开始 (位置 {first_diff}) =====")
    
    # 打印修改前
    if first_diff < len(original):
        end_orig = min(first_diff + 8, len(original))
        diff_lines.append(f"{prefix}原序列 [{first_diff}:{end_orig}]: {original[first_diff:end_orig].hex()}")
    else:
        diff_lines.append(f"{prefix}原序列: (已结束)")
    
    # 打印修改后
    if first_diff < len(modified):
        end_mod = min(first_diff + 8, len(modified))
        diff_lines.append(f"{prefix}新序列 [{first_diff}:{end_mod}]: {modified[first_diff:end_mod].hex()}")
    else:
        diff_lines.append(f"{prefix}新序列: (已结束)")
    
    diff_lines.append(f"{prefix}===== 差异结束 =====")
    
    # 打印尾部
    if first_diff + 8 < min_len:
        diff_lines.append(f"{prefix}位置 {first_diff+8} 后: {original[first_diff+8:min_len].hex()}")
    
    return diff_lines


def format_coap_header(data: bytes) -> Optional[dict]:
    """
    解析 CoAP 头部信息（不依赖 aiocoap）
    
    Returns:
        dict with keys: version, type, token_length, code, mid, token
    """
    if len(data) < 4:
        return None
    
    vttkl = data[0]
    version = (vttkl & 0xC0) >> 6
    msg_type = (vttkl & 0x30) >> 4
    tkl = vttkl & 0x0F
    code = data[1]
    mid = int.from_bytes(data[2:4], 'big')
    
    token = data[4:4+tkl] if tkl > 0 and len(data) >= 4+tkl else b''
    
    return {
        'version': version,
        'type': msg_type,
        'token_length': tkl,
        'code': code,
        'mid': mid,
        'token': token,
        'token_hex': token.hex() if token else 'none',
        'type_name': ['CON', 'NON', 'ACK', 'RST'][msg_type] if msg_type < 4 else '?',
        'code_class': code >> 5,
        'code_detail': code & 0x1F,
    }


def debug_message(data: bytes, direction: str) -> List[str]:
    """
    输出消息的详细调试信息
    
    Args:
        data: 原始字节数据
        direction: 方向标签 (如 "IN", "OUT")
    
    Returns:
        调试信息列表
    """
    lines = []
    lines.append(f"--- {direction} ({len(data)} bytes) ---")
    lines.append(f"原始: {data.hex()}")
    
    header = format_coap_header(data)
    if header:
        lines.append(f"Header: Ver={header['version']}, Type={header['type_name']}, "
                    f"TKL={header['token_length']}, Code={header['code_class']}.{header['code_detail']}, "
                    f"MID={header['mid']:#06x}")
        lines.append(f"Token: {header['token_hex']}")
    else:
        lines.append("Header: 无法解析 (数据太短)")
    
    return lines


if __name__ == "__main__":
    # 简单测试
    logging.basicConfig(level=logging.DEBUG)
    
    # 测试有效的 CoAP 消息
    valid_msg = bytes([0x42, 0x01, 0x12, 0x34]) + b'\xaa\xbb' + bytes([0xB4]) + b"/time" + bytes([0xFF]) + b"test"
    ok, err = validate_message(valid_msg, "测试有效消息")
    print(f"有效消息验证: ok={ok}, err={err}")
    
    # 测试无效消息
    invalid_msg = bytes([0xFF, 0xFF, 0xFF])
    ok, err = validate_message(invalid_msg, "测试无效消息")
    print(f"无效消息验证: ok={ok}, err={err}")
    
    # 测试字节差异
    print("\n--- 字节差异测试 ---")
    orig = bytes([0x42, 0x01, 0x12, 0x34, 0xAA, 0xBB, 0x00, 0xFF])
    mod = bytes([0x42, 0x01, 0x12, 0x34, 0xAA, 0xCC, 0x00, 0xFF])
    for line in bytes_diff(orig, mod, "TEST"):
        print(line)
