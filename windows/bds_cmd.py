"""
Utilitario para envio de comandos diretamente ao console do Bedrock Dedicated Server (Windows).
Utiliza Win32 API pura (Toolhelp32, AttachConsole, WriteConsoleInputW).
"""
import sys
import time
import ctypes
from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.c_size_t),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', wintypes.LONG),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', ctypes.c_char * 260)
    ]

class KEY_EVENT_RECORD(ctypes.Structure):
    _fields_ = [
        ('bKeyDown', wintypes.BOOL),
        ('wRepeatCount', wintypes.WORD),
        ('wVirtualKeyCode', wintypes.WORD),
        ('wVirtualScanCode', wintypes.WORD),
        ('uChar', wintypes.WCHAR),
        ('dwControlKeyState', wintypes.DWORD)
    ]

class INPUT_RECORD(ctypes.Structure):
    _fields_ = [
        ('EventType', wintypes.WORD),
        ('KeyEvent', KEY_EVENT_RECORD)
    ]

def get_bds_pid():
    hSnapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    if hSnapshot == -1 or hSnapshot == 0:
        return None
    pe = PROCESSENTRY32()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
    success = kernel32.Process32First(hSnapshot, ctypes.byref(pe))
    pid = None
    while success:
        if pe.szExeFile.lower() == b'bedrock_server.exe':
            pid = pe.th32ProcessID
            break
        success = kernel32.Process32Next(hSnapshot, ctypes.byref(pe))
    kernel32.CloseHandle(hSnapshot)
    return pid

def send_command(cmd_text, wait_ms=50):
    pid = get_bds_pid()
    if not pid:
        return False
        
    kernel32.FreeConsole()
    if not kernel32.AttachConsole(pid):
        return False
        
    hInput = kernel32.GetStdHandle(-10) # STD_INPUT_HANDLE
    if not hInput or hInput == -1:
        kernel32.FreeConsole()
        return False
        
    events = []
    for ch in cmd_text + '\r':
        vk = user32.VkKeyScanW(ord(ch))
        vkey = vk & 0xff if vk != -1 else ord(ch)
        vscan = user32.MapVirtualKeyW(vkey, 0)
        
        ir_down = INPUT_RECORD(1, KEY_EVENT_RECORD(True, 1, vkey, vscan, ch, 0))
        ir_up = INPUT_RECORD(1, KEY_EVENT_RECORD(False, 1, vkey, vscan, ch, 0))
        events.extend([ir_down, ir_up])
        
    arr = (INPUT_RECORD * len(events))(*events)
    written = wintypes.DWORD()
    ok = kernel32.WriteConsoleInputW(hInput, arr, len(events), ctypes.byref(written))
    kernel32.FreeConsole()
    if wait_ms > 0:
        time.sleep(wait_ms / 1000.0)
    return bool(ok)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python bds_cmd.py <comando>")
        sys.exit(1)
    cmd = " ".join(sys.argv[1:])
    success = send_command(cmd)
    if success:
        print(f"[OK] {cmd}")
    else:
        print(f"[FALHA] {cmd}")
        sys.exit(1)
