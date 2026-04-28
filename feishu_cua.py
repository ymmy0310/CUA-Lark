# -*- coding: utf-8 -*-
from desktop_automation import DesktopAutomation
from screenshot import capture_fullscreen
from ai_communicator import send_to_ai, plan_task
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
        # 窗口控制回调
        self.minimize_window_callback = None
        self.show_window_callback = None
        
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
        
        # 1. 截图前 - 隐藏界面
        if self.minimize_window_callback:
            self.minimize_window_callback()
            self.auto.wait(0.2)  # 等待窗口隐藏完成
        
        # 1. 截图全屏
        if callback:
            callback("📷 正在截图...")
        screenshot_path = capture_fullscreen()
        
        # 1. 截图后 - 显示界面
        if self.show_window_callback:
            self.show_window_callback()
        
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
        
        # 4. 执行命令前 - 隐藏界面
        if self.minimize_window_callback:
            self.minimize_window_callback()
            self.auto.wait(0.2)
        
        # 4. 解析并执行命令
        if callback:
            callback("⚡ 正在执行AI指令...")
        
        result = parse_and_execute_command(self.auto, ai_command, self.screen_w, self.screen_h)
        
        # 4. 执行命令后 - 显示界面
        if self.show_window_callback:
            self.show_window_callback()
        
        # 保存对话历史
        self.add_to_history("assistant", str(ai_command))
        
        # 5. 检查结果
        if isinstance(result, dict) and result.get('type') == 'request_input':
            # 请求用户输入，返回特殊标记
            return {'type': 'request_input', 'prompt': result['prompt']}
        elif result is not None:
            # 任务完成
            if callback:
                callback(f"✅ 任务完成: {result}")
            return True
        
        return False
    
    def run_task(self, user_task: str, max_iterations: int = 15, max_per_step: int = 5, use_planning: bool = True, callback=None):
        """
        运行一个任务（支持任务规划）
        
        :param user_task: 用户任务描述
        :param max_iterations: 总最大迭代次数
        :param max_per_step: 每个步骤最大迭代次数
        :param use_planning: 是否使用任务规划
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
        
        try:
            # 任务规划阶段
            task_steps = None
            if use_planning:
                if callback:
                    callback("\n" + "-"*60)
                    callback("📋 任务规划阶段")
                    callback("-"*60)
                
                task_steps = plan_task(user_task)
                if not task_steps:
                    if callback:
                        callback("⚠️  任务规划失败，直接执行任务")
                    use_planning = False
            
            if use_planning and task_steps:
                # 分步骤执行模式
                total_iterations = 0
                for step_idx, step_task in enumerate(task_steps, 1):
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
                        callback("\n" + "="*60)
                        callback(f"🎯 步骤 {step_idx}/{len(task_steps)}: {step_task}")
                        callback("="*60)
                    
                    # 执行当前步骤
                    step_completed = False
                    for step_iteration in range(1, max_per_step + 1):
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
                            callback(f"🔄 第 {step_iteration} 次迭代（步骤 {step_idx}）")
                            callback("-"*60)
                        
                        # 构建当前步骤的任务描述
                        current_task = f"当前步骤：{step_task}\n\n整体任务：{user_task}"
                        task_completed = self.execute_one_iteration(current_task, callback)
                        total_iterations += 1
                        
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
                            step_completed = True
                            if callback:
                                callback(f"✅ 步骤 {step_idx} 完成")
                            break
                        
                        # 检查是否达到总最大迭代次数
                        if total_iterations >= max_iterations:
                            if callback:
                                callback("\n" + "="*60)
                                callback("⚠️  达到总最大迭代次数，任务可能未完成")
                                callback("="*60)
                            self.is_running = False
                            return False
                        
                        # 执行后等待一下
                        self.auto.wait(2)
                    
                    if not step_completed:
                        if callback:
                            callback(f"⚠️  步骤 {step_idx} 未完成，继续下一步")
                    
                    # 步骤之间等待一下
                    self.auto.wait(1)
                
                if callback:
                    callback("\n" + "="*60)
                    callback("✅ 所有步骤执行完成")
                    callback("="*60)
                
                self.is_running = False
                return True
            
            else:
                # 原始单步执行模式
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
        finally:
            # 确保任务结束时窗口始终显示
            if self.show_window_callback:
                self.show_window_callback()


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
