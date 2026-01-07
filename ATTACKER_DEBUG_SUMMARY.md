# CoAP Attacker Script - Debug Summary

## Issues Found and Fixed

### 1. ❌ Incorrect Import Path for CoAP
**Problem:** 
```python
from scapy.layers.coap import *  # ❌ Wrong
```

**Solution:**
```python
from scapy.contrib.coap import *  # ✅ Correct
```

CoAP support in Scapy is in the `contrib` module, not `layers`.

---

### 2. ❌ Asyncio Integration Issue
**Problem:** 
- `sniff()` is a blocking function that doesn't work with asyncio
- `asyncio.create_task()` was called from a non-async context (packet callback)

**Solution:**
- Run `sniff()` in a separate thread using `Thread(target=self._sniff_thread, daemon=True)`
- Use `asyncio.run_coroutine_threadsafe()` to schedule coroutines from the packet callback thread
- Store the event loop reference in `self.loop` for cross-thread communication

---

### 3. ❌ Platform-Specific Interface Name
**Problem:**
- Default interface was hardcoded to `"lo"` (Linux loopback)
- This doesn't exist on Windows

**Solution:**
```python
if platform.system() == "Windows":
    self.interface = conf.iface  # Use Scapy's default interface
else:
    self.interface = "lo"  # Linux/Mac loopback
```

---

### 4. ❌ Incorrect CoAP Packet Construction
**Problem:**
```python
CoAP(type="ACK", code="2.05 Content", payload="data")  # ❌ Wrong
```

**Solution:**
```python
CoAP(type="ACK", code=69, token=b'test') / Raw(load=b"data")  # ✅ Correct
```

- CoAP `code` field expects numeric values (69 = "2.05 Content")
- Payload is added as a `Raw` layer using the `/` operator, not as a parameter

---

### 5. ✅ Added Network Interface Selection
**Enhancement:**
- Users can now select which network interface to use for sniffing
- Automatically highlights Loopback interface for local testing
- Shows all available interfaces with helpful markers

**Implementation:**
```python
# Display interfaces with markers
for i, iface in enumerate(interfaces):
    if "Loopback" in iface or iface == "lo":
        print(f"  {i+1}. {iface} ← 推荐用于本地测试")
    else:
        print(f"  {i+1}. {iface}")

# Let user choose
iface_choice = input(f"请选择网络接口 (1-{len(interfaces)}, 直接回车使用默认): ")
```

---

## How to Run

### Prerequisites

#### Windows:
1. Install **Npcap** from https://npcap.com/
2. Run PowerShell or Command Prompt **as Administrator**

#### Linux/Mac:
1. Run with `sudo` for packet capture permissions

### Running the Script

```bash
# Test that everything works
python coap_token_replay/test_attacker_import.py

# View available network interfaces
python coap_token_replay/test_interface_selection.py

# Run the attacker (requires admin/sudo)
python coap_token_replay/attacker.py
```

### Interface Selection

When you run `attacker.py`, you'll first see available interfaces:

```
可用的网络接口:
  1. \Device\NPF_{5DA2537F-06D5-4EED-BF23-992A93D6D7EB}
  ...
  9. \Device\NPF_Loopback ← 推荐用于本地测试

请选择网络接口 (1-9, 直接回车使用默认):
```

**For local testing:** Choose the Loopback interface (e.g., `9`)
**For network testing:** Choose your network adapter or press Enter for default

### Menu Options

After selecting the interface, you'll see:

```
选择攻击模式:
1. 自动嗅探和攻击    - Automatically sniff and replay CoAP responses
2. 查看攻击步骤说明   - View attack methodology explanation
3. 手动构造攻击数据包 - Show example of manual packet construction
```

---

## Testing Results

All tests passed successfully:

```
✓ scapy.all imported successfully
✓ CoAP imported successfully from scapy.contrib.coap
✓ TokenReplayAttacker imported successfully
✓ TokenReplayAttacker instance created
✓ CoAP packet created successfully
```

---

## Key Code Changes

### attacker.py

1. **Imports:**
   - Added `import platform`, `import sys`, `from threading import Thread`
   - Changed `from scapy.layers.coap import *` → `from scapy.contrib.coap import *`

2. **Class initialization:**
   - Added auto-detection of network interface based on OS
   - Added `self.loop` and `self.sniff_thread` attributes

3. **Packet callback:**
   - Changed `asyncio.create_task()` → `asyncio.run_coroutine_threadsafe()`

4. **Sniffing:**
   - Split into `_sniff_thread()` (runs in thread) and `start_sniffing()` (async wrapper)
   - Added error handling and helpful error messages

5. **Packet construction:**
   - Fixed CoAP packet syntax to use numeric codes and Raw layer for payload

---

## Additional Notes

- The script now works on both Windows and Linux/Mac
- Proper thread-safe asyncio integration
- Better error messages and user guidance
- Test script included for verification

