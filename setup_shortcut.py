import os
import sys
import pythoncom
from win32com.shell import shell, shellcon

def create_shortcut():
    """创建桌面快捷方式"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 找到gui_app.py
    gui_app_path = os.path.join(current_dir, 'gui_app.py')
    
    if not os.path.exists(gui_app_path):
        print(f"❌ 找不到gui_app.py: {gui_app_path}")
        return False
    
    # 获取Python路径 - 使用pythonw.exe（无控制台版本）
    python_dir = os.path.dirname(sys.executable)
    python_path = os.path.join(python_dir, 'pythonw.exe')
    
    # 如果pythonw不存在，就用python
    if not os.path.exists(python_path):
        python_path = sys.executable
    
    # 获取桌面路径
    desktop_path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0)
    
    # 快捷方式路径
    shortcut_path = os.path.join(desktop_path, 'CUA-Lark.lnk')
    
    # 创建快捷方式对象
    shell_obj = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink,
        None,
        pythoncom.CLSCTX_INPROC_SERVER,
        shell.IID_IShellLink
    )
    
    # 设置快捷方式属性
    shell_obj.SetPath(python_path)
    shell_obj.SetArguments(f'"{gui_app_path}"')
    shell_obj.SetWorkingDirectory(f'"{current_dir}"')
    shell_obj.SetDescription('CUA-Lark - 飞书AI操作助手')
    shell_obj.SetIconLocation(python_path, 0)
    
    # 保存快捷方式
    persist_file = shell_obj.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(shortcut_path, 0)
    
    print(f"✅ 桌面快捷方式已创建: {shortcut_path}")
    print("📝 提示：请先配置config.py中的API配置后再使用！")
    return True

if __name__ == '__main__':
    try:
        create_shortcut()
        input("\n按回车键退出...")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        input("\n按回车键退出...")

