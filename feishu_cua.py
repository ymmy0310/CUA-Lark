from desktop_automation import DesktopAutomation
from screenshot import capture_fullscreen
from ai_communicator import send_to_ai
from command_parser import parse_and_execute_command
import time


def feishu_cua_system(user_task: str, max_iterations: int = 10, fail_safe: bool = True):
    """
    飞书CUA系统主函数
    
    :param user_task: 用户任务描述
    :param max_iterations: 最大迭代次数，防止无限循环
    :param fail_safe: 是否启用故障安全
    """
    print("\n" + "="*60)
    print("🚀 飞书CUA系统启动")
    print("="*60)
    print(f"📋 用户任务: {user_task}")
    print(f"🔄 最大迭代次数: {max_iterations}")
    print()
    
    # 初始化自动化工具
    auto = DesktopAutomation(fail_safe=fail_safe, pause_duration=0.5)
    
    # 获取屏幕尺寸
    screen_w, screen_h = auto.get_screen_size()
    print(f"📺 屏幕尺寸: {screen_w}x{screen_h}")
    
    # 对话历史
    conversation_history = []
    
    # 5秒准备时间
    print("⏱️ 5秒后开始，请准备好工作环境...")
    auto.wait(5)
    
    for iteration in range(1, max_iterations + 1):
        print("\n" + "-"*60)
        print(f"🔄 第 {iteration} 次迭代")
        print("-"*60)
        
        # 1. 截图全屏
        print("📷 正在截图...")
        screenshot_path = capture_fullscreen()
        
        # 2. 发送给AI（包含屏幕尺寸）
        print("🤖 正在与AI通信...")
        try:
            ai_command = send_to_ai(
                user_task=user_task,
                screenshot_path=screenshot_path,
                screen_w=screen_w,
                screen_h=screen_h,
                conversation_history=conversation_history
            )
        except Exception as e:
            print(f"❌ AI通信失败: {e}")
            print("⚠️  系统将在2秒后重试...")
            auto.wait(2)
            continue
        
        # 打印 AI 的思考和描述
        if "thought" in ai_command:
            print(f"💭 AI思考: {ai_command['thought']}")
        if "description" in ai_command:
            print(f"📝 AI描述: {ai_command['description']}")
        
        # 3. 解析并执行命令
        print("⚡ 正在执行AI指令...")
        result = parse_and_execute_command(auto, ai_command)
        
        # 4. 检查任务是否完成
        if result is not None:
            print("\n" + "="*60)
            print(f"🎉 任务完成！")
            print(f"📝 结果: {result}")
            print("="*60)
            return result
        
        # 保存对话历史
        conversation_history.append({
            "role": "assistant",
            "content": str(ai_command)
        })
        
        # 执行后等待一下
        auto.wait(2)
    
    # 达到最大迭代次数
    print("\n" + "="*60)
    print("⚠️  达到最大迭代次数，任务可能未完成")
    print("="*60)
    return None


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║                   飞书CUA系统 v1.0                           ║
╠══════════════════════════════════════════════════════════════╣
║  使用说明:                                                   ║
║  1. 确保已配置 config.py 中的API信息                        ║
║  2. 输入你的任务描述                                         ║
║  3. 系统会自动操作电脑完成任务                               ║
║  4. 紧急停止: 鼠标移动到屏幕左上角                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 获取用户任务
    task = input("\n请输入你的任务描述: ").strip()
    
    if task:
        # 启动系统
        feishu_cua_system(
            user_task=task,
            max_iterations=10,
            fail_safe=True
        )
    else:
        print("⚠️  任务描述不能为空！")
