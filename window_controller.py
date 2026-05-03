# -*- coding: utf-8 -*-
"""
CUA 窗口控制器
提供命令行接口，用于从外部（包括AI）控制CUA窗口的显示/隐藏
"""

import argparse
import os
import tempfile


# 控制信号文件路径
SIGNAL_FILE = os.path.join(tempfile.gettempdir(), "cua_window_signal.txt")


def show_window():
    """发送显示窗口信号"""
    with open(SIGNAL_FILE, "w", encoding="utf-8") as f:
        f.write("SHOW")
    print("✅ 已发送显示窗口信号")


def hide_window():
    """发送隐藏窗口信号"""
    with open(SIGNAL_FILE, "w", encoding="utf-8") as f:
        f.write("HIDE")
    print("✅ 已发送隐藏窗口信号")


def check_signal():
    """检查是否有信号（由GUI调用）"""
    if os.path.exists(SIGNAL_FILE):
        with open(SIGNAL_FILE, "r", encoding="utf-8") as f:
            signal = f.read().strip()
        os.remove(SIGNAL_FILE)
        return signal
    return None


def main():
    parser = argparse.ArgumentParser(description="CUA窗口控制器")
    parser.add_argument("action", choices=["show", "hide"], help="窗口操作：show=显示, hide=隐藏")
    args = parser.parse_args()
    
    if args.action == "show":
        show_window()
    elif args.action == "hide":
        hide_window()


if __name__ == "__main__":
    main()
