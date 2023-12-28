from ctypes import *
import win32process
import win32api
import win32gui
import win32con
import os
import time
import ctypes
from ctypes import wintypes

# 访问权限和内存地址常量
GAME_WIDTH_ADDR = 0x01005334
GAME_HEIGHT_ADDR = 0x01005338
GAME_DATA_ADDR = 0x01005361
MEM_WIDTH = 32
PAGE_EXECUTE_READWRITE = 0x40

# 设定所需的常量
PROCESS_ALL_ACCESS = (0x0020 | 0x0400 | 0x000F0000 | 0x00100000 | 0xFFF)
VIRTUAL_MEM = (0x1000 | 0x2000)

# 游戏窗口标题和路径
GAME_TITLE = "扫雷"
GAME_PATH = os.path.join(os.getcwd(), "winmine.exe")

kernel32 = windll.LoadLibrary("kernel32.dll")


def enum_windows_callback(hwnd, result):
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == GAME_TITLE:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        result.append((hwnd, pid))

def start_new_game_and_get_handle():
    os.startfile(GAME_PATH)
    time.sleep(1)  # 稍等片刻以确保游戏窗口已启动

    result = []
    win32gui.EnumWindows(enum_windows_callback, result)

    if result:
        return result[0]  # 返回找到的第一个窗口句柄
    else:
        return None


def find_game_window():
    hwnd = win32gui.FindWindow(None, GAME_TITLE)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return hwnd, pid

# 这部分代码来自https://www.lzskyline.com/index.php/archives/128
def wg(window_handle):
    _, pid = win32process.GetWindowThreadProcessId(window_handle)
    if not pid:
        return

    phand = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not phand:
        print("进程打开失败!")
        return

    game_width = c_int(0)
    kernel32.ReadProcessMemory(int(phand), GAME_WIDTH_ADDR, byref(game_width), 2, None)
    game_height = c_int(0)
    kernel32.ReadProcessMemory(int(phand), GAME_HEIGHT_ADDR, byref(game_height), 2, None)

    addr = create_string_buffer(MEM_WIDTH * game_height.value)
    kernel32.ReadProcessMemory(int(phand), GAME_DATA_ADDR, byref(addr), MEM_WIDTH * game_height.value, None)

    for i in range(game_height.value):
        for j in range(game_width.value):
            current = hex(addr.value[i * MEM_WIDTH + j])
            # print(current, end=" ")
            if current == "0xf":
                win32api.PostMessage(window_handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(19 + j * 16, 63 + i * 16))
                win32api.PostMessage(window_handle, win32con.WM_LBUTTONUP, 0, 0)
    print("通关成功!")


def mine_immortal():
    # 踩雷不死的实现代码将在这里
    pass


def patch_process(pid, address, data):
    """
    修改指定进程的内存。

    :param pid: 目标进程的PID。
    :param address: 要修改的内存地址。
    :param data: 要写入的数据，类型为bytes。
    """
    # 打开目标进程
    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, wintypes.DWORD(pid))
    if not h_process:
        raise ctypes.WinError(ctypes.get_last_error())

    # 修改内存保护设置以允许写入操作
    old_protect = wintypes.DWORD()
    if not kernel32.VirtualProtectEx(ctypes.c_void_p(h_process), ctypes.c_void_p(address), len(data),
                                     PAGE_EXECUTE_READWRITE, ctypes.byref(old_protect)):
        raise ctypes.WinError(ctypes.get_last_error())

    # 写入数据
    bytes_written = ctypes.c_size_t()
    if not kernel32.WriteProcessMemory(h_process, ctypes.c_void_p(address), create_string_buffer(data),
                                       len(data), ctypes.byref(bytes_written)):
        raise ctypes.WinError(ctypes.get_last_error())

    # 恢复原始的内存保护设置
    if not kernel32.VirtualProtectEx(h_process, ctypes.c_void_p(address), len(data), old_protect,
                                     ctypes.byref(old_protect)):
        raise ctypes.WinError(ctypes.get_last_error())

    # 关闭进程句柄
    kernel32.CloseHandle(h_process)

    print("踩雷也算通过修改成功!")


def main():
    window_handle = None
    pid = 0
    while True:
        action = input("Input Instruction!（s：start game，f：find winmine window，c：crack，d：no die，q：quit）：")
        if action == 's':
            window_handle, pid = start_new_game_and_get_handle()
        elif action == 'f':
            window_handle, pid = find_game_window()
            if window_handle:
                print("找到扫雷游戏窗口。")
            else:
                print("未找到扫雷游戏窗口。")
        elif action == 'c':
            if window_handle:
                wg(window_handle)
            else:
                print("未找到扫雷游戏窗口。")
        elif action == 'd':
            # mine_immortal()
            patch_process(pid, 0x01003591, b'\x6A\x01')
        elif action == 'q':
            break
        else:
            print("无效的指令。")


if __name__ == "__main__":
    main()
