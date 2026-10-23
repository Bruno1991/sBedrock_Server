import sys
import ctypes
from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

class COORD(ctypes.Structure):
    _fields_ = [('X', wintypes.SHORT), ('Y', wintypes.SHORT)]

class SMALL_RECT(ctypes.Structure):
    _fields_ = [
        ('Left', wintypes.SHORT),
        ('Top', wintypes.SHORT),
        ('Right', wintypes.SHORT),
        ('Bottom', wintypes.SHORT)
    ]

class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ('dwSize', COORD),
        ('dwCursorPosition', COORD),
        ('wAttributes', wintypes.WORD),
        ('srWindow', SMALL_RECT),
        ('dwMaximumWindowSize', COORD)
    ]

from bds_cmd import get_bds_pid

pid = get_bds_pid()
if not pid:
    print("BDS not running")
    sys.exit(1)

kernel32.FreeConsole()
if not kernel32.AttachConsole(pid):
    print("Failed to attach console")
    sys.exit(1)

hOutput = kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE
csbi = CONSOLE_SCREEN_BUFFER_INFO()
kernel32.GetConsoleScreenBufferInfo(hOutput, ctypes.byref(csbi))

width = csbi.dwSize.X
height = csbi.dwSize.Y
cursor_y = csbi.dwCursorPosition.Y

# Read last 30 lines up to cursor_y
start_y = max(0, cursor_y - 25)
num_lines = cursor_y - start_y + 1

lines = []
for y in range(start_y, cursor_y + 1):
    coord = COORD(0, y)
    buf = ctypes.create_unicode_buffer(width)
    read = wintypes.DWORD()
    kernel32.ReadConsoleOutputCharacterW(hOutput, buf, width, coord, ctypes.byref(read))
    line = buf.value.rstrip()
    if line:
        lines.append(line)

kernel32.FreeConsole()

for l in lines:
    try:
        print(l)
    except Exception:
        print(l.encode("ascii", errors="replace").decode("ascii"))
