from desktop_automation import DesktopAutomation
from typing import Dict, Optional


def parse_and_execute_command(auto: DesktopAutomation, command: Dict) -> Optional[str]:
    """
    解析并执行 AI 返回的 JSON 命令
    
    :param auto: DesktopAutomation 实例
    :param command: AI 返回的 JSON 命令
    :return: 如果任务完成返回结果，否则返回 None
    """
    # 检查是否任务完成
    if command.get('task_completed'):
        result = command.get('result', '任务完成')
        print(f"✅ {result}")
        return result
    
    action = command.get('action')
    
    print(f"🎯 执行操作: {action}")
    
    # 坐标修正系数
    x_scale = 2.55
    y_scale = 1.44
    
    try:
        # 鼠标操作
        if action == 'left_click':
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * x_scale)
            if y is not None:
                y = int(y * y_scale)
            print(f"📍 左键点击位置: (x={x}, y={y}) [修正: x*2.55, y*1.44]")
            auto.left_click(x=x, y=y)
            auto.wait(0.5)
            
        elif action == 'right_click':
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * x_scale)
            if y is not None:
                y = int(y * y_scale)
            print(f"📍 右键点击位置: (x={x}, y={y}) [修正: x*2.55, y*1.44]")
            auto.right_click(x=x, y=y)
            auto.wait(0.5)
            
        elif action == 'double_click':
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * x_scale)
            if y is not None:
                y = int(y * y_scale)
            print(f"📍 双击位置: (x={x}, y={y}) [修正: x*2.55, y*1.44]")
            auto.double_click(x=x, y=y)
            auto.wait(0.5)
            
        elif action == 'drag':
            start_x = command.get('start_x')
            start_y = command.get('start_y')
            end_x = command.get('end_x')
            end_y = command.get('end_y')
            duration = command.get('duration', 0.5)
            if start_x is not None:
                start_x = int(start_x * x_scale)
            if start_y is not None:
                start_y = int(start_y * y_scale)
            if end_x is not None:
                end_x = int(end_x * x_scale)
            if end_y is not None:
                end_y = int(end_y * y_scale)
            print(f"📍 拖拽: ({start_x}, {start_y}) → ({end_x}, {end_y}) [修正: x*2.55, y*1.44]")
            auto.drag_to(end_x, end_y, start_x=start_x, start_y=start_y, duration=duration)
            auto.wait(0.5)
            
        elif action == 'hover':
            x = command.get('x')
            y = command.get('y')
            duration = command.get('duration', 0.3)
            if x is not None:
                x = int(x * x_scale)
            if y is not None:
                y = int(y * y_scale)
            print(f"📍 悬停位置: (x={x}, y={y}) [修正: x*2.55, y*1.44]")
            auto.hover(x=x, y=y, duration=duration)
            auto.wait(0.5)
            
        elif action == 'select_area':
            start_x = command.get('start_x')
            start_y = command.get('start_y')
            end_x = command.get('end_x')
            end_y = command.get('end_y')
            if start_x is not None:
                start_x = int(start_x * x_scale)
            if start_y is not None:
                start_y = int(start_y * y_scale)
            if end_x is not None:
                end_x = int(end_x * x_scale)
            if end_y is not None:
                end_y = int(end_y * y_scale)
            print(f"📍 框选: ({start_x}, {start_y}) → ({end_x}, {end_y}) [修正: x*2.55, y*1.44]")
            auto.select_area(start_x, start_y, end_x, end_y)
            auto.wait(0.5)
            
        elif action == 'scroll':
            clicks = command.get('clicks', 10)
            x = command.get('x')
            y = command.get('y')
            if x is not None:
                x = int(x * x_scale)
            if y is not None:
                y = int(y * y_scale)
            print(f"📍 滚轮滚动: {clicks} 格, 位置: (x={x}, y={y}) [修正: x*2.55, y*1.44]")
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
            auto.type_password(password=password, confirm=confirm)
            auto.wait(0.5)
            
        # 任务控制
        elif action == 'task_completed':
            result = command.get('result', '任务完成')
            print(f"✅ {result}")
            return result
            
        elif action == 'continue':
            print("⏳ 继续执行...")
            return None
            
        else:
            print(f"⚠️  未知操作: {action}")
            return None
            
    except Exception as e:
        print(f"❌ 执行操作时出错: {e}")
        return None
        
    return None


if __name__ == '__main__':
    print("命令解析器测试")
    print("请运行主程序测试")
