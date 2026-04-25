import pyautogui
import os
from datetime import datetime


def capture_fullscreen(save_dir: str = 'screenshots', filename: str = None) -> str:
    """
    全屏截图并保存
    
    :param save_dir: 截图保存目录，默认 screenshots
    :param filename: 文件名，不指定则自动生成时间戳
    :return: 截图保存的完整路径
    """
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 生成文件名
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshot_{timestamp}.png'
    
    # 确保文件扩展名是 .png
    if not filename.lower().endswith('.png'):
        filename += '.png'
    
    # 完整路径
    filepath = os.path.join(save_dir, filename)
    
    # 截图
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    
    print(f'📷 截图已保存: {filepath}')
    return filepath


if __name__ == '__main__':
    # 测试截图
    print('3秒后开始截图...')
    import time
    time.sleep(3)
    path = capture_fullscreen()
    print(f'测试完成！截图保存在: {path}')
