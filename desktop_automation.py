import pyautogui
import pyperclip
import time
import os
import subprocess
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
    
    def type_password(self, password: str, confirm: bool = True, x: Optional[int] = None, y: Optional[int] = None):
        """
        专门用于输入密码的函数
        密码框会自动切换到英文输入模式，使用直接键盘输入更安全
        :param password: 要输入的密码
        :param confirm: 是否按两次 enter 确认（默认 True，防止换行问题）
        :param x: 密码框的x坐标，提供则先点击激活
        :param y: 密码框的y坐标，提供则先点击激活
        """
        # 如果提供了坐标，先点击激活密码框
        if x is not None and y is not None:
            self.left_click(x, y)
            self.wait(0.3)
        
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
    
    def open_folder(self, folder_path: str):
        """
        通过路径打开文件夹
        :param folder_path: 文件夹路径
        """
        if os.path.exists(folder_path):
            os.startfile(folder_path)
            print(f"📂 已打开文件夹: {folder_path}")
        else:
            raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    def click_paste(self, text: str, x: Optional[int] = None, y: Optional[int] = None):
        """
        组合操作：写入剪贴板 + 点击输入框 + 粘贴（完整输入连招！）
        :param text: 要输入的文本内容
        :param x: 点击的x坐标，不提供则点击当前位置
        :param y: 点击的y坐标，不提供则点击当前位置
        """
        self.copy_to_clipboard(text)
        if x is not None and y is not None:
            self.left_click(x, y)
        else:
            self.left_click()
        self.wait(0.3)
        self.hotkey('ctrl', 'v')
        self.wait(0.2)
    
    # ==================== 文本编辑功能 ====================
    
    def delete_text(self, count: int = 1):
        """
        删除文本（使用退格键）
        :param count: 删除字符数，默认 1
        """
        self.press_key('backspace', presses=count)
    
    def delete_selected(self):
        """
        删除选中的文本（使用 delete 键）
        """
        self.press_key('delete')
    
    def select_all(self):
        """
        全选文本（ctrl + a）
        """
        self.hotkey('ctrl', 'a')
    
    def delete_all(self):
        """
        全选后删除所有文本
        """
        self.select_all()
        self.wait(0.1)
        self.delete_selected()
    
    def delete_word_left(self, count: int = 1):
        """
        删除光标左侧的词（ctrl + backspace）
        :param count: 删除词数，默认 1
        """
        for _ in range(count):
            self.hotkey('ctrl', 'backspace')
            self.wait(0.05)
    
    def delete_word_right(self, count: int = 1):
        """
        删除光标右侧的词（ctrl + delete）
        :param count: 删除词数，默认 1
        """
        for _ in range(count):
            self.hotkey('ctrl', 'delete')
            self.wait(0.05)



