

## 🚀 Method 1: Use the Stable Y Address to Find X and Z (Simplest)

Your Y address `0x100b667e8` is stable and direct. X and Z are usually stored nearby. Run this command to automatically find them:

```bash
cd /home/cyber-demon/Documents/Making\ the\ Minecraft\ Automation/mc_ai_automation
source venv/bin/activate
python3 -c "
import struct
import subprocess
pid = int(subprocess.check_output(['pgrep', '-f', 'java.*minecraft']).decode().strip())
y_addr = 0x100b667e8
with open(f'/proc/{pid}/mem', 'rb') as f:
    # Read values around Y
    for offset in range(-32, 33, 4):
        f.seek(y_addr + offset)
        val = struct.unpack('<f', f.read(4))[0]
        if -1000 < val < 1000:   # plausible coordinate
            print(f'offset {offset:+4}: {val:.2f}')
"
```

It will print a list like:
```
offset  -8: 158.29
offset  -4: 64.00
offset   0: 64.00
offset  +4: -79.08
...
```

Look for the values that match your current X and Z (check F3). Suppose X is at offset `-8` and Z at offset `+4`. Then you would set in `offsets.json`:

```json
"position": {
    "x": {
        "type": "direct",
        "address": "0x100b667e0"   // Y_addr - 8
    },
    "y": {
        "type": "direct",
        "address": "0x100b667e8"
    },
    "z": {
        "type": "direct",
        "address": "0x100b667ec"   // Y_addr + 4
    }
}
```

**Replace the placeholder** with these direct addresses. This method uses only the stable Y address and is very safe.

---

## 🔧 Method 2: Use libjvm.so Offset (If You Prefer Pointer Chains)

If you still want to use the `libjvm.so` pointer chain, here’s how to get the offset **without any manual hex typing**:

1. **Find the current dynamic address for X** (use scanmem, which you already know how to do).  
   For example, after scanning, you get an address like `0x8659cf94`.

2. **Find the base address of `libjvm.so`**:
   ```bash
   PID=$(pgrep -f "java.*minecraft")
   cat /proc/$PID/maps | grep libjvm.so | head -1 | awk '{print $1}' | cut -d- -f1
   ```
   It will output something like `7f8c4a000000`.

3. **Compute the offset** using Python (no mental math):
   ```bash
   python3 -c "
   dynamic = 0x8659cf94          # replace with your X address
   base = 0x7f8c4a000000         # replace with the base from step 2
   offset = dynamic - base
   print(f'Offset: 0x{offset:x}')
   "
   ```

4. Replace `0xPLACEHOLDER` in `offsets.json` with that offset (e.g., `0x123456`). For Z, use the same base but a different final offset (probably `offset + 4`).

5. **If the chain requires intermediate pointers**, the placeholder would need to be something like `["libjvm.so+0x123456", 0x7890, 0xabcd]`. If you only have one offset, the current code will treat it as a direct pointer from the base. If it doesn't work, you may need to use Cheat Engine to find the full chain. But for many Minecraft versions, the coordinates are directly reachable from a module base.

---

## ✅ After Updating `offsets.json`

Run the bot:
```bash
sudo python3 main.py --provider groq
```

If coordinates match F3, you’re done! The bot will now work across Minecraft restarts.

