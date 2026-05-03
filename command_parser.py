from desktop_automation import DesktopAutomation
from typing import Dict, Optional
import subprocess
import sys
import os


def parse_and_execute_command(auto: DesktopAutomation, command: Dict, screen_w: int, screen_h: int) -> Optional[str]:
    """
    解析并执行 AI 返回的 JSON 命令
    
    :param auto: DesktopAutomation 实例
    :param command: AI 返回的 JSON 命令
    :param screen_w: 屏幕宽度
    :param screen_h: 屏幕高度
    :return: 如果任务完成返回结果，否则返回 None
    """
    action = command.get('action')
    
    print(f"🎯 执行操作: {action}")
    
    # 有效的操作列表
    valid_actions = [
        'left_click', 'right_click', 'double_click', 'drag', 'hover', 
        'select_area', 'scroll', 'type_text', 'press_key', 'hotkey',
        'type_password', 'task_completed', 'continue', 'open_folder',
        'click_paste', 'select_text', 'delete_text', 'delete_selected',
        'select_all', 'delete_all', 'delete_word_left', 'delete_word_right',
        'request_input', 'show_cua_window', 'hide_cua_window'
    ]
    
    # 如果不是有效的操作，且有description或thought，就直接结束（纯聊天模式）
    if action not in valid_actions and action is not None:
        description = command.get('description', '')
        thought = command.get('thought', '')
        result = description or thought or '好的，我明白了！'
        print(f"💬 {result}")
        return result
    
    try:
        # 鼠标操作
        if action == 'left_click':
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * screen_w)
            if y is not None:
                y = int(y * screen_h)
            print(f"📍 左键点击位置: (x={x}, y={y}) [归一化系数: x={command.get('x'):.3f}, y={command.get('y'):.3f}]")
            auto.left_click(x=x, y=y)
            auto.wait(0.5)
            
        elif action == 'right_click':
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * screen_w)
            if y is not None:
                y = int(y * screen_h)
            print(f"📍 右键点击位置: (x={x}, y={y}) [归一化系数: x={command.get('x'):.3f}, y={command.get('y'):.3f}]")
            auto.right_click(x=x, y=y)
            auto.wait(0.5)
            
        elif action == 'double_click':
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * screen_w)
            if y is not None:
                y = int(y * screen_h)
            print(f"📍 双击位置: (x={x}, y={y}) [归一化系数: x={command.get('x'):.3f}, y={command.get('y'):.3f}]")
            auto.double_click(x=x, y=y)
            auto.wait(0.5)
            
        elif action == 'drag':
            start_x = command.get('start_x')
            start_y = command.get('start_y')
            end_x = command.get('end_x')
            end_y = command.get('end_y')
            duration = command.get('duration', 0.5)
            if start_x is not None:
                start_x = int(start_x * screen_w)
            if start_y is not None:
                start_y = int(start_y * screen_h)
            if end_x is not None:
                end_x = int(end_x * screen_w)
            if end_y is not None:
                end_y = int(end_y * screen_h)
            print(f"📍 拖拽: ({start_x}, {start_y}) → ({end_x}, {end_y}) [归一化系数]")
            auto.drag_to(end_x, end_y, start_x=start_x, start_y=start_y, duration=duration)
            auto.wait(0.5)
            
        elif action == 'hover':
            x = command.get('x')
            y = command.get('y')
            duration = command.get('duration', 0.3)
            if x is not None:
                x = int(x * screen_w)
            if y is not None:
                y = int(y * screen_h)
            print(f"📍 悬停位置: (x={x}, y={y}) [归一化系数: x={command.get('x'):.3f}, y={command.get('y'):.3f}]")
            auto.hover(x=x, y=y, duration=duration)
            auto.wait(0.5)
            
        elif action == 'select_area':
            start_x = command.get('start_x')
            start_y = command.get('start_y')
            end_x = command.get('end_x')
            end_y = command.get('end_y')
            if start_x is not None:
                start_x = int(start_x * screen_w)
            if start_y is not None:
                start_y = int(start_y * screen_h)
            if end_x is not None:
                end_x = int(end_x * screen_w)
            if end_y is not None:
                end_y = int(end_y * screen_h)
            print(f"📍 框选: ({start_x}, {start_y}) → ({end_x}, {end_y}) [归一化系数]")
            auto.select_area(start_x, start_y, end_x, end_y)
            auto.wait(0.5)
            
        elif action == 'scroll':
            clicks = command.get('clicks', 10)
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * screen_w)
            if y is not None:
                y = int(y * screen_h)
            print(f"📍 滚轮滚动: {clicks} 格, 位置: (x={x}, y={y}) [归一化系数]")
            auto.scroll(clicks=clicks, x=x, y=y)
            auto.wait(0.5)
            
        # 键盘操作
        elif action == 'type_text':
            text = command.get('text', '')
            use_clipboard = command.get('use_clipboard', True)
            auto.type_text(text=text, use_clipboard=use_clipboard)
            auto.wait(0.5)
            
        elif action == 'press_key':
            key = command.get('key')
            presses = command.get('presses', 1)
            interval = command.get('interval', 0.0)
            auto.press_key(key=key, presses=presses, interval=interval)
            auto.wait(0.5)
            
        elif action == 'hotkey':
            keys = command.get('keys', [])
            interval = command.get('interval', 0.0)
            auto.hotkey(*keys, interval=interval)
            auto.wait(0.5)
            
        # 密码输入
        elif action == 'type_password':
            password = command.get('password', '')
            confirm = command.get('confirm', True)
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * screen_w)
            if y is not None:
                y = int(y * screen_h)
            print(f"🔐 密码输入: (x={x}, y={y}) [归一化系数: x={command.get('x'):.3f}, y={command.get('y'):.3f}]")
            auto.type_password(password=password, confirm=confirm, x=x, y=y)
            auto.wait(0.5)
            
        # 任务控制
        elif action == 'task_completed':
            result = command.get('result', '任务完成')
            print(f"✅ {result}")
            return result
            
        elif action == 'continue':
            print("⏳ 继续执行...")
            return None
        
        elif action == 'request_input':
            prompt = command.get('prompt', '请补充更多信息')
            print(f"🙋 请求用户输入: {prompt}")
            return {'type': 'request_input', 'prompt': prompt}
        
        elif action == 'open_folder':
            folder_path = command.get('path', '')
            auto.open_folder(folder_path)
            auto.wait(1.5)
            
        elif action == 'click_paste':
            text = command.get('text', '')
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * screen_w)
            if y is not None:
                y = int(y * screen_h)
            print(f"🎯 点击粘贴连招: (x={x}, y={y}) 文本: {text[:30]}{'...' if len(text) > 30 else ''}")
            auto.click_paste(text=text, x=x, y=y)
            auto.wait(0.5)
        
        elif action == 'select_text':
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * screen_w)
            if y is not None:
                y = int(y * screen_h)
            print(f"🎯 选中文本连招(点击+全选): (x={x}, y={y}) [归一化系数]")
            auto.left_click(x=x, y=y)
            auto.wait(0.3)
            auto.hotkey('ctrl', 'a')
            auto.wait(0.3)
        
        # 文本编辑操作
        elif action == 'delete_text':
            count = command.get('count', 1)
            print(f"⌫ 删除字符: {count} 个")
            auto.delete_text(count=count)
            auto.wait(0.3)
            
        elif action == 'delete_selected':
            print(f"⌫ 删除选中文本")
            auto.delete_selected()
            auto.wait(0.3)
            
        elif action == 'select_all':
            print(f"📋 全选文本")
            auto.select_all()
            auto.wait(0.3)
            
        elif action == 'delete_all':
            print(f"⌫ 删除所有文本")
            auto.delete_all()
            auto.wait(0.5)
            
        elif action == 'delete_word_left':
            count = command.get('count', 1)
            print(f"⌫ 删除左侧词: {count} 个")
            auto.delete_word_left(count=count)
            auto.wait(0.3)
            
        elif action == 'delete_word_right':
            count = command.get('count', 1)
            print(f"⌫ 删除右侧词: {count} 个")
            auto.delete_word_right(count=count)
            auto.wait(0.3)
            
        elif action == 'show_cua_window':
            print(f"🖥️  显示CUA主窗口")
            _send_window_command("show")
            auto.wait(0.5)
            
        elif action == 'hide_cua_window':
            print(f"🖥️  隐藏CUA主窗口")
            _send_window_command("hide")
            auto.wait(0.5)
            
        else:
            print(f"⚠️  未知操作: {action}")
            return None
            
    except Exception as e:
        print(f"❌ 执行操作时出错: {e}")
        return None
        
    return None


def _send_window_command(command: str):
    """
    发送窗口控制命令到CUA主程序
    :param command: show 或 hide
    """
    try:
        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        controller_script = os.path.join(script_dir, "window_controller.py")
        
        # 使用python解释器运行控制器脚本
        python_exe = sys.executable
        result = subprocess.run(
            [python_exe, controller_script, command],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ 窗口控制命令已发送: {command}")
        else:
            print(f"⚠️  窗口控制命令发送失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 发送窗口控制命令时出错: {e}")

