from ctypes import *
import win32process
import win32api
import win32gui
import win32con
import os
import time

# 访问权限和内存地址常量
PROCESS_ALL_ACCESS = 0X1F0FFF  # 最高权限
GAME_WIDTH_ADDR = 0x01005334
GAME_HEIGHT_ADDR = 0x01005338
GAME_DATA_ADDR = 0x01005361
MEM_WIDTH = 32

# 游戏窗口标题和路径
GAME_TITLE = "扫雷"
GAME_PATH = os.path.join(os.getcwd(), "winmine.exe")

kernel32 = windll.LoadLibrary("kernel32.dll")


def enum_windows_callback(hwnd, resultList):
    '''用于EnumWindows的回调函数，检查窗口标题'''
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == GAME_TITLE:
        resultList.append(hwnd)

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
    return win32gui.FindWindow(None, GAME_TITLE)

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
            print(current, end=" ")
            if current == "0xf":
                win32api.PostMessage(window_handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(19 + j * 16, 63 + i * 16))
                win32api.PostMessage(window_handle, win32con.WM_LBUTTONUP, 0, 0)
        print()


def mine_immortal():
    # 踩雷不死的实现代码将在这里
    pass


def main():
    window_handle = None
    while True:
        action = input("请输入指令（s：开始新游戏，f：查找扫雷窗口，c：一键破解，d：踩雷不死，q：退出）：")
        if action == 's':
            window_handle = start_new_game_and_get_handle()
        elif action == 'f':
            window_handle = find_game_window()
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
            mine_immortal()
        elif action == 'q':
            break
        else:
            print("无效的指令。")


if __name__ == "__main__":
    main()
