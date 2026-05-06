# -*- coding: utf-8 -*-
from desktop_automation import DesktopAutomation
from screenshot import capture_fullscreen
from ai_communicator import send_to_ai, understand_task
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
        self.consecutive_same_action = 0
        self.last_action_key = ""
        # 窗口控制回调
        self.minimize_window_callback = None
        self.show_window_callback = None
        
    def add_to_history(self, role: str, content: str):
        """添加内容到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def execute_one_iteration(self, user_task: str, callback=None):
        """
        执行一次迭代（改写版：窗口全程最小化，暂停丢弃AI JSON）

        :param user_task: 用户任务
        :param callback: 回调函数，用于显示状态
        :return: True=完成, False=继续, None=被终止, dict=request_input, 'PAUSED'=暂停
        """

        # --------------------- 状态变量 ---------------------
        # self.should_stop           用户点击暂停/终止
        # self.conversation_history  保存对话历史
        # self.consecutive_same_action  连续相同操作计数
        # self.last_action_key       最近一次动作 key
        # ----------------------------------------------------

        # 0️⃣ 检查是否需要暂停
        if self.should_stop:
            self.should_stop = False  # ⚠️ 复位标志
            return 'PAUSED'  # 当前循环直接暂停，AI json 不生成

        # 1️⃣ 保持窗口最小化（控制条显示）
        if self.minimize_window_callback:
            self.minimize_window_callback()
        if callback:
            callback("📷 截图中...")

        # 2️⃣ 全屏截图
        screenshot_path = capture_fullscreen()
        self.auto.wait(0.5)  # 等待屏幕刷新

        # 3️⃣ 检查是否暂停（用户可能在截图后点击暂停）
        if self.should_stop:
            self.should_stop = False  # ⚠️ 复位标志
            return 'PAUSED'  # 当前循环丢弃

        # 4️⃣ 发送任务给 AI
        if callback:
            callback("🤖 与 AI 通信中...")
        try:
            ai_command = send_to_ai(
                user_task=user_task,
                screenshot_path=screenshot_path,
                screen_w=self.screen_w,
                screen_h=self.screen_h,
                conversation_history=self.conversation_history
            )
        except Exception as e:
            if callback:
                callback(f"❌ AI通信失败: {e}")
            return False

        # 5️⃣ 检查是否暂停（AI json生成后）
        if self.should_stop:
            self.should_stop = False  # ⚠️ 复位标志
            if callback:
                callback("⏸ 用户暂停，丢弃当前 AI 指令")
            return 'PAUSED'  # 丢弃 AI json

        # 打印 AI 的思考和描述
        if "thought" in ai_command:
            thought_msg = f"💭 AI思考: {ai_command['thought']}"
            if callback:
                callback(thought_msg)

        if "description" in ai_command:
            desc_msg = f"📝 AI描述: {ai_command['description']}"
            if callback:
                callback(desc_msg)

        # 6️⃣ 连续相同操作检测（仅检测鼠标操作，排除热键等合法重复操作）
        action = ai_command.get('action', '')
        # 只检测有坐标的鼠标操作，热键(如ctrl+v)、窗口控制等不检测
        mouse_actions = ['left_click', 'right_click', 'double_click', 'click_paste', 'select_text']
        if action in mouse_actions:
            action_key = f"{action}_{ai_command.get('x','')}_{ai_command.get('y','')}"
            if action_key == self.last_action_key:
                self.consecutive_same_action += 1
            else:
                self.consecutive_same_action = 1
                self.last_action_key = action_key

            if self.consecutive_same_action >= 3:
                count = self.consecutive_same_action
                if callback:
                    callback(f"⚠️ 连续{count}次相同操作，强制请求用户帮助")
                self.consecutive_same_action = 0
                self.last_action_key = ""
                return {'type': 'request_input',
                        'prompt': f'你已经连续{count}次执行了相同操作({action})，请提供帮助。'}
        else:
            # 非鼠标操作，重置计数
            self.consecutive_same_action = 0
            self.last_action_key = ""

        # 7️⃣ 执行命令
        if callback:
            callback("⚡ 执行 AI 指令...")
        result = parse_and_execute_command(self.auto, ai_command, self.screen_w, self.screen_h)

        # 8️⃣ 处理 request_input（AI主动请求用户输入）
        if isinstance(result, dict) and result.get('type') == 'request_input':
            return result  # 直接返回，让上层处理

        # 8️⃣.5️⃣ 处理剪贴板内容（复制操作后自动读取）
        if isinstance(result, dict) and result.get('type') == 'clipboard_content':
            clipboard_content = result.get('content', '')
            if callback:
                callback(f"📋 已读取剪贴板内容: {clipboard_content[:80]}{'...' if len(clipboard_content) > 80 else ''}")
            # 将剪贴板内容加入对话历史，让AI在下一轮能看到
            self.add_to_history("system", f"[复制内容：] {clipboard_content}")

        # 9️⃣ 执行后等待
        self.auto.wait(2.0)

        # 1️⃣0️⃣ 更新对话历史
        self.add_to_history("assistant", str(ai_command))

        # 1️⃣1️⃣ 判断任务是否完成
        if ai_command.get('action') == 'task_completed':
            return True  # 任务完成

        return False  # 下一循环继续
    
    def run_task(self, user_task: str, max_iterations: int = 250, callback=None, skip_understanding: bool = False):
        """
        运行一个任务（统一迭代）
        
        :param user_task: 用户任务描述
        :param max_iterations: 最大迭代次数
        :param callback: 回调函数，用于显示状态
        :param skip_understanding: 是否跳过任务理解确认阶段
        :return: True=完成, False=达到上限/失败, None=被终止, dict=request_input
        """
        self.current_task = user_task
        self.is_running = True
        
        if callback:
            callback("\n" + "="*60)
            callback(f"🚀 开始任务: {user_task}")
            callback("="*60)
            callback(f"📺 屏幕尺寸: {self.screen_w}x{self.screen_h}")
        
        # 任务理解确认阶段（除非跳过）
        if not skip_understanding:
            if callback:
                callback("\n" + "-"*60)
                callback("🧠 正在分析任务需求...")
                callback("-"*60)
            
            understanding = understand_task(user_task)
            if understanding:
                # 构建确认信息
                confirm_msg = f"""
💡 AI理解如下：

📋 任务类型：{understanding.get('task_type', '未知')}

📝 理解：{understanding.get('understanding', '')}

📊 信息检查：
   必需信息：{', '.join(understanding.get('required_info', []))}
   已提供：{', '.join(understanding.get('provided_info', []))}
   缺失：{', '.join(understanding.get('missing_info', [])) if understanding.get('missing_info') else '无'}

📋 执行计划：{understanding.get('plan_summary', '')}

💬 {understanding.get('suggestion', '')}
"""
                if callback:
                    callback(confirm_msg)
                
                # 无论信息是否完整，都返回 request_input 让用户确认/补充
                # 信息完整时用户可以输入"确认"直接通过
                # 信息不完整时用户可以补充缺失的信息
                self.is_running = False
                return {
                    'type': 'request_input', 
                    'prompt': understanding.get('suggestion', '请确认或补充信息'),
                    'phase': 'understanding_confirmation',
                    'understanding': understanding
                }
            else:
                if callback:
                    callback("⚠️ 任务理解分析失败，跳过确认阶段")
        
        self.add_to_history("user", user_task)

        try:
            iteration_count = 0
            while iteration_count < max_iterations:
                if callback:
                    callback("\n" + "-"*60)
                    callback(f"🔄 第 {iteration_count+1}/{max_iterations} 次迭代")
                    callback("-"*60)

                result = self.execute_one_iteration(user_task, callback)
                iteration_count += 1

                if result == 'PAUSED':
                    if callback:
                        callback("\n" + "="*60)
                        callback("⏹️  任务已暂停，等待用户介入")
                        callback("="*60)
                    self.is_running = False
                    return {'type': 'request_input', 'prompt': '任务已暂停，可介入操作后输入「继续」恢复执行：', 'phase': 'user_paused'}

                if result is None:
                    self.should_stop = False
                    self.is_running = False
                    return None

                if isinstance(result, dict) and result.get('type') == 'request_input':
                    return result

                if result is True:
                    if callback:
                        callback("\n" + "="*60)
                        callback("✅ 所有步骤执行完成")
                        callback("="*60)
                    self.is_running = False
                    return True

                self.auto.wait(2)

            if callback:
                callback("\n" + "="*60)
                callback("⚠️  达到最大迭代次数，任务可能未完成")
                callback("="*60)

            self.is_running = False
            return False

        finally:
            pass


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
