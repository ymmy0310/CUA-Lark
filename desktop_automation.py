import pyautogui
import pyperclip
import time
from typing import Tuple, List, Optional

class DesktopAutomation:
    """
    桌面自动化操作类，封装了常用的GUI操作功能
    """
    
    def __init__(self, fail_safe: bool = True, pause_duration: float = 0.5):
        """
        初始化自动化工具
        :param fail_safe: 是否启用故障安全，鼠标移动到左上角会触发异常
        :param pause_duration: 每次操作后的暂停时间（秒）
        """
        pyautogui.FAILSAFE = fail_safe
        pyautogui.PAUSE = pause_duration
        self.screen_width, self.screen_height = pyautogui.size()
    
    # ==================== 底层功能 ====================
    
    def left_click(self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1, interval: float = 0.0):
        """
        鼠标左键点击
        :param x: 点击的x坐标，不提供则点击当前位置
        :param y: 点击的y坐标，不提供则点击当前位置
        :param clicks: 点击次数
        :param interval: 点击间隔时间（秒）
        """
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, interval=interval, button='left')
        else:
            pyautogui.click(clicks=clicks, interval=interval, button='left')
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1, interval: float = 0.0):
        """
        鼠标右键点击
        :param x: 点击的x坐标，不提供则点击当前位置
        :param y: 点击的y坐标，不提供则点击当前位置
        :param clicks: 点击次数
        :param interval: 点击间隔时间（秒）
        """
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, interval=interval, button='right')
        else:
            pyautogui.click(clicks=clicks, interval=interval, button='right')
    
    def type_text(self, text: str, interval: float = 0.0, use_clipboard: bool = True):
        """
        输入文本（默认使用剪贴板方式，兼容中英文）
        :param text: 要输入的文本内容
        :param interval: 每个字符输入的间隔时间（秒）- 仅在非剪贴板模式下有效
        :param use_clipboard: 是否使用剪贴板方式输入（默认 True，推荐）
        """
        if use_clipboard:
            # 使用剪贴板方式输入，支持中文，不受输入法影响
            self.copy_to_clipboard(text)
            self.hotkey('ctrl', 'v')
        else:
            # 直接键盘输入，仅支持英文
            pyautogui.typewrite(text, interval=interval)
    
    def type_password(self, password: str, confirm: bool = True):
        """
        专门用于输入密码的函数
        密码框会自动切换到英文输入模式，使用直接键盘输入更安全
        :param password: 要输入的密码
        :param confirm: 是否按两次 enter 确认（默认 True，防止换行问题）
        """
        # 直接键盘输入密码，避免剪贴板泄露风险
        pyautogui.typewrite(password, interval=0.02)
        if confirm:
            # 按两次 enter，确保输入完成且避免换行问题
            self.press_key('enter')
            self.press_key('enter')
    
    def press_key(self, key: str, presses: int = 1, interval: float = 0.0):
        """
        按下并释放单个按键
        :param key: 按键名称，如 'enter', 'backspace', 'a', 'ctrl' 等
        :param presses: 按键次数
        :param interval: 每次按键间隔时间（秒）
        """
        pyautogui.press(key, presses=presses, interval=interval)
    
    def hotkey(self, *keys: str, interval: float = 0.0):
        """
        按下组合热键，如 hotkey('ctrl', 'c')
        :param keys: 按键列表，按顺序按下，逆序释放
        :param interval: 按键之间的间隔时间（秒）
        """
        pyautogui.hotkey(*keys, interval=interval)
    
    def copy_to_clipboard(self, text: str):
        """
        将文本复制到系统剪贴板
        :param text: 要复制的文本内容
        """
        pyperclip.copy(text)
    
    def get_from_clipboard(self) -> str:
        """
        从系统剪贴板获取内容
        :return: 剪贴板中的文本内容
        """
        return pyperclip.paste()
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None):
        """
        鼠标滚轮滚动
        :param clicks: 滚动的单位数，正数向上滚动，负数向下滚动
        :param x: 滚动位置的x坐标，不提供则在当前位置滚动
        :param y: 滚动位置的y坐标，不提供则在当前位置滚动
        """
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x=x, y=y)
        else:
            pyautogui.scroll(clicks)
    
    # ==================== 二层功能 ====================
    
    def press_combination(self, keys: List[str], hold_time: float = 0.1):
        """
        按下组合键，支持更复杂的组合操作
        :param keys: 按键列表，按顺序按下，保持hold_time后逆序释放
        :param hold_time: 按键保持时间（秒）
        """
        for key in keys:
            pyautogui.keyDown(key)
            time.sleep(hold_time)
        
        time.sleep(hold_time)
        
        for key in reversed(keys):
            pyautogui.keyUp(key)
            time.sleep(hold_time)
    
    def drag_to(self, end_x: int, end_y: int, start_x: Optional[int] = None, start_y: Optional[int] = None, duration: float = 0.5):
        """
        鼠标拖拽操作
        :param end_x: 目标位置x坐标
        :param end_y: 目标位置y坐标
        :param start_x: 起始位置x坐标，不提供则从当前位置开始
        :param start_y: 起始位置y坐标，不提供则从当前位置开始
        :param duration: 拖拽持续时间（秒）
        """
        if start_x is not None and start_y is not None:
            pyautogui.moveTo(start_x, start_y)
        
        pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None, interval: float = 0.0):
        """
        鼠标左键双击
        :param x: 点击的x坐标，不提供则点击当前位置
        :param y: 点击的y坐标，不提供则点击当前位置
        :param interval: 两次点击的间隔时间（秒）
        """
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y, interval=interval, button='left')
        else:
            pyautogui.doubleClick(interval=interval, button='left')
    
    def hover(self, x: int, y: int, duration: float = 0.0):
        """
        鼠标悬停到指定位置
        :param x: 目标位置x坐标
        :param y: 目标位置y坐标
        :param duration: 移动持续时间（秒）
        """
        pyautogui.moveTo(x, y, duration=duration)
    
    def select_area(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
        """
        框选区域
        :param start_x: 框选起始x坐标
        :param start_y: 框选起始y坐标
        :param end_x: 框选结束x坐标
        :param end_y: 框选结束y坐标
        :param duration: 拖拽持续时间（秒）
        """
        self.drag_to(end_x, end_y, start_x, start_y, duration=duration)
    
    # ==================== 辅助功能 ====================
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        获取当前鼠标位置
        :return: (x, y) 坐标元组
        """
        return pyautogui.position()
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        获取屏幕分辨率
        :return: (width, height) 分辨率元组
        """
        return self.screen_width, self.screen_height
    
    def wait(self, seconds: float):
        """
        等待指定时间
        :param seconds: 等待时间（秒）
        """
        time.sleep(seconds)


# 使用示例
if __name__ == "__main__":
    # 创建自动化实例
    auto = DesktopAutomation(pause_duration=0.5)  # 增加默认等待时间
    
    print("⚠️  警告：即将开始自动化演示")
    print("请确保现在处于桌面，没有其他窗口遮挡")
    print("如果程序失控，快速将鼠标移到屏幕左上角即可停止")
    print("5秒后开始演示...")
    auto.wait(5)
    
    # 示例 1: 打开记事本 - 使用剪贴板方式输入，不受输入法影响
    auto.hotkey('win', 'd')  # 先显示桌面
    auto.wait(1.5)
    
    auto.hotkey('win', 'r')
    auto.wait(1.5)  # 等待运行窗口打开
    auto.copy_to_clipboard('notepad')  # 复制到剪贴板
    auto.hotkey('ctrl', 'v')  # 粘贴到运行窗口
    auto.wait(0.5)
    auto.press_key('enter')  # 按回车打开记事本
    auto.wait(2.5)  # 等待记事本启动
    
    # 获取屏幕中心位置，确保点击在记事本窗口内
    screen_w, screen_h = auto.get_screen_size()
    center_x, center_y = screen_w // 2, screen_h // 2
    auto.hover(center_x, center_y, duration=0.3)  # 移动到屏幕中心
    auto.left_click()  # 点击确保记事本窗口激活
    auto.wait(0.5)
    
    # 示例 2: 输入文本（默认使用剪贴板方式，兼容中文）
    auto.type_text('这是桌面自动化测试演示\n\n底层功能演示：\n1. 文字输入功能正常\n')
    
    # 示例 3: 复制粘贴
    auto.copy_to_clipboard('2. 剪贴板复制功能正常\n')
    auto.hotkey('ctrl', 'v')
    
    # 示例 4: 快捷键操作演示
    auto.press_key('end')  # 移动到末尾
    auto.press_key('enter')
    auto.type_text('\n二层功能演示：\n')
    auto.copy_to_clipboard('3. 拖拽、双击、悬停等功能也都正常')
    auto.hotkey('ctrl', 'v')
    
    # 示例 5: 鼠标操作 - 拖拽、悬停、双击
    screen_w, screen_h = auto.get_screen_size()
    center_x, center_y = screen_w // 2, screen_h // 2
    
    # 在屏幕中心 50x50 区域内做拖拽动作
    start_x, start_y = center_x - 25, center_y - 25  # 区域左上角
    end_x, end_y = center_x + 25, center_y + 25      # 区域右下角
    auto.drag_to(end_x, end_y, start_x=start_x, start_y=start_y, duration=0.3)
    
    # 移动到屏幕中心悬停
    auto.hover(center_x, center_y, duration=0.5)
    
    # 双击两次
    auto.double_click(center_x, center_y)
    auto.wait(0.3)
    auto.double_click(center_x, center_y)
    
    # 示例 6: 鼠标操作
    print("演示完成，5 秒后关闭记事本...")
    auto.wait(5)
    
    # 关闭记事本（不保存）- 使用更可靠的方法
    auto.hotkey('alt', 'f4')  # 尝试 Alt+F4
    auto.wait(1)
    # 如果 Alt+F4 没反应，使用任务管理器关闭
    auto.press_key('n')  # 按 N 不保存
    auto.wait(1)
    
    # 检查记事本是否关闭，如果没有，使用 taskkill 强制关闭
    print("正在关闭记事本...")
    import subprocess
    subprocess.run(['taskkill', '/F', '/IM', 'Notepad.exe'], capture_output=True)
    
    print("✅ 演示结束！")
