from desktop_automation import DesktopAutomation
from screenshot import capture_fullscreen
from ai_communicator import send_to_ai
from command_parser import parse_and_execute_command
import time


class FeishuCUASystem:
    """飞书CUA系统类，支持连续任务"""
    
    def __init__(self, fail_safe: bool = True):
        """
        初始化系统
        
        :param fail_safe: 是否启用故障安全
        """
        self.auto = DesktopAutomation(fail_safe=fail_safe, pause_duration=0.5)
        self.screen_w, self.screen_h = self.auto.get_screen_size()
        self.conversation_history = []
        self.current_task = ""
        self.is_running = False
        self.should_stop = False
        
    def add_to_history(self, role: str, content: str):
        """添加内容到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def execute_one_iteration(self, user_task: str, callback=None) -> bool:
        """
        执行一次迭代
        
        :param user_task: 用户任务
        :param callback: 回调函数，用于显示状态
        :return: 任务是否完成，或者返回 None 表示任务被终止
        """
        # 0. 检查是否需要停止
        if self.should_stop:
            return None
        
        # 1. 截图全屏
        if callback:
            callback("📷 正在截图...")
        screenshot_path = capture_fullscreen()
        
        # 0. 检查是否需要停止
        if self.should_stop:
            return None
        
        # 2. 等待页面加载
        if callback:
            callback("⏳ 等待页面加载...")
        self.auto.wait(2)
        
        # 0. 检查是否需要停止
        if self.should_stop:
            return None
        
        # 3. 发送给AI
        if callback:
            callback("🤖 正在与AI通信...")
        
        try:
            ai_command = send_to_ai(
                user_task=user_task,
                screenshot_path=screenshot_path,
                screen_w=self.screen_w,
                screen_h=self.screen_h,
                conversation_history=self.conversation_history
            )
        except Exception as e:
            error_msg = f"❌ AI通信失败: {e}"
            if callback:
                callback(error_msg)
            return False
        
        # 0. 检查是否需要停止
        if self.should_stop:
            return None
        
        # 打印 AI 的思考和描述
        if "thought" in ai_command:
            thought_msg = f"💭 AI思考: {ai_command['thought']}"
            if callback:
                callback(thought_msg)
        
        if "description" in ai_command:
            desc_msg = f"📝 AI描述: {ai_command['description']}"
            if callback:
                callback(desc_msg)
        
        # 0. 检查是否需要停止
        if self.should_stop:
            return None
        
        # 4. 解析并执行命令
        if callback:
            callback("⚡ 正在执行AI指令...")
        
        result = parse_and_execute_command(self.auto, ai_command, self.screen_w, self.screen_h)
        
        # 保存对话历史
        self.add_to_history("assistant", str(ai_command))
        
        # 5. 检查任务是否完成
        if result is not None:
            if callback:
                callback(f"✅ 任务完成: {result}")
            return True
        
        return False
    
    def run_task(self, user_task: str, max_iterations: int = 15, callback=None):
        """
        运行一个任务
        
        :param user_task: 用户任务描述
        :param max_iterations: 最大迭代次数
        :param callback: 回调函数，用于显示状态
        """
        self.current_task = user_task
        self.is_running = True
        
        if callback:
            callback("\n" + "="*60)
            callback(f"🚀 开始任务: {user_task}")
            callback("="*60)
            callback(f"📺 屏幕尺寸: {self.screen_w}x{self.screen_h}")
        
        # 添加用户任务到历史
        self.add_to_history("user", user_task)
        
        for iteration in range(1, max_iterations + 1):
            # 检查是否需要停止
            if self.should_stop:
                if callback:
                    callback("\n" + "="*60)
                    callback("⏹️  任务已被用户终止")
                    callback("="*60)
                self.should_stop = False
                self.is_running = False
                return False
            
            if callback:
                callback("\n" + "-"*60)
                callback(f"🔄 第 {iteration} 次迭代")
                callback("-"*60)
            
            task_completed = self.execute_one_iteration(user_task, callback)
            
            # 检查是否被终止
            if task_completed is None:
                if callback:
                    callback("\n" + "="*60)
                    callback("⏹️  任务已被用户终止")
                    callback("="*60)
                self.should_stop = False
                self.is_running = False
                return False
            
            if task_completed:
                self.is_running = False
                return True
            
            # 执行后等待一下
            self.auto.wait(2)
        
        # 达到最大迭代次数
        if callback:
            callback("\n" + "="*60)
            callback("⚠️  达到最大迭代次数，任务可能未完成")
            callback("="*60)
        
        self.is_running = False
        return False


def feishu_cua_system(user_task: str, max_iterations: int = 15, fail_safe: bool = True):
    """
    飞书CUA系统主函数（保留原接口）
    
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
    
    # 初始化系统
    system = FeishuCUASystem(fail_safe=fail_safe)
    
    # 5秒准备时间
    print("⏱️ 5秒后开始，请准备好工作环境...")
    system.auto.wait(5)
    
    # 运行任务
    def console_callback(msg):
        print(msg)
    
    system.run_task(user_task, max_iterations, console_callback)


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
            max_iterations=15,
            fail_safe=True
        )
    else:
        print("⚠️  任务描述不能为空！")
