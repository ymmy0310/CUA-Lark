# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import sys
import time
from feishu_cua import FeishuCUASystem


class FeishuCUAGUI:
    """飞书CUA系统图形界面 - v3.3 升级版本"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("飞书CUA系统 v3.3")
        
        # 设置窗口更大、居中显示
        self.window_width = 1000
        self.window_height = 1100  # 增加高度到1100，确保功能按钮完整显示
        
        # 获取屏幕尺寸，居中显示
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        # 设置窗口置顶
        self.root.attributes("-topmost", True)
        
        # 初始化系统
        self.system = None
        self.is_initialized = False
        self.is_running = False
        self.is_waiting_for_input = False
        self.current_task = ""
        self.current_step_info = ""
        self.current_action_info = ""
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主容器 - 左右分栏
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 主操作区
        left_frame = tk.Frame(main_paned)
        main_paned.add(left_frame, minsize=700)
        
        # 右侧面板 - 说明书
        right_frame = tk.Frame(main_paned, bg="#f0f4f8")
        main_paned.add(right_frame, minsize=280)
        
        # === 左侧面板内容 ===
        
        # 顶部信息栏 - 显示当前步骤和操作
        top_info_frame = tk.Frame(left_frame, bg="#2c3e50", height=100)
        top_info_frame.pack(fill=tk.X)
        top_info_frame.pack_propagate(False)
        
        # 当前执行步骤
        step_label = tk.Label(top_info_frame, text="当前步骤:", bg="#2c3e50", fg="#3498db", 
                              font=("微软雅黑", 12, "bold"))
        step_label.place(x=15, y=10)
        
        self.step_var = tk.StringVar(value="等待任务...")
        self.step_display = tk.Label(top_info_frame, textvariable=self.step_var, bg="#2c3e50", 
                                     fg="#ffffff", font=("微软雅黑", 11), wraplength=500, justify=tk.LEFT)
        self.step_display.place(x=15, y=40)
        
        # 当前操作
        action_label = tk.Label(top_info_frame, text="当前操作:", bg="#2c3e50", fg="#e67e22", 
                               font=("微软雅黑", 12, "bold"))
        action_label.place(x=550, y=10)
        
        self.action_var = tk.StringVar(value="--")
        self.action_display = tk.Label(top_info_frame, textvariable=self.action_var, bg="#2c3e50", 
                                      fg="#ffffff", font=("微软雅黑", 11), wraplength=180, justify=tk.LEFT)
        self.action_display.place(x=550, y=40)
        
        # 日志显示区域 - 更大的字体
        log_frame = tk.Frame(left_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        log_label = tk.Label(log_frame, text="执行日志:", font=("微软雅黑", 10, "bold"), anchor=tk.W)
        log_label.pack(fill=tk.X, padx=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80,
                                                 font=("微软雅黑", 11), bg="#fafbfc")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5)
        self.log_text.config(state=tk.DISABLED)
        
        # 输入区域 - 支持shift+enter换行
        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_label = tk.Label(input_frame, text="任务描述:", font=("微软雅黑", 10, "bold"), anchor=tk.W)
        input_label.pack(fill=tk.X, padx=5)
        
        # 输入框 - 支持多行输入
        self.input_text = scrolledtext.ScrolledText(input_frame, height=4, width=80,
                                                    font=("微软雅黑", 11), bg="#ffffff")
        self.input_text.pack(fill=tk.X, padx=5, pady=(5, 5))
        self.input_text.bind("<Return>", self.on_enter_pressed)
        self.input_text.bind("<Shift-Return>", self.on_shift_enter)
        
        # 任务规划选项
        options_frame = tk.Frame(left_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.use_planning_var = tk.BooleanVar(value=True)
        planning_check = tk.Checkbutton(options_frame, text="启用任务规划（推荐）", 
                                        variable=self.use_planning_var,
                                        font=("微软雅黑", 10))
        planning_check.pack(side=tk.LEFT, padx=5)
        
        # 按钮区域
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X)
        
        self.init_btn = tk.Button(button_frame, text="初始化系统", bg="#3498db", fg="white",
                                  font=("微软雅黑", 11, "bold"), width=15,
                                  command=self.initialize_system)
        self.init_btn.pack(side=tk.LEFT, padx=5)
        
        self.send_btn = tk.Button(button_frame, text="发送任务", bg="#2ecc71", fg="white",
                                  font=("微软雅黑", 11, "bold"), width=15,
                                  command=self.send_task, state=tk.DISABLED)
        self.send_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="终止任务", bg="#c0392b", fg="white",
                                  font=("微软雅黑", 11, "bold"), width=15,
                                  command=self.stop_task, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(button_frame, text="清空日志", bg="#95a5a6", fg="white",
                                  font=("微软雅黑", 11), width=12,
                                  command=self.clear_log)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # === 右侧面板 - 说明书 ===
        
        guide_label = tk.Label(right_frame, text="📖 使用说明", bg="#f0f4f8", 
                               font=("微软雅黑", 13, "bold"))
        guide_label.pack(pady=(15, 10))
        
        guide_content = scrolledtext.ScrolledText(right_frame, height=35, width=30,
                                                 font=("微软雅黑", 9), bg="#ffffff")
        guide_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 15))
        
        # 说明书内容
        guide_text = """
【快速开始】
1. 点击"初始化系统"
2. 等待3秒准备
3. 在输入框输入任务
4. 按Enter发送，Shift+Enter换行

【文本编辑操作】
• delete_text - 删除字符
• delete_selected - 删除选中
• select_all - 全选
• delete_all - 删除全部
• delete_word_left - 删除左词
• delete_word_right - 删除右词

【快捷连招】
• click_paste_enter - 点击、粘贴、回车

【任务规划】
• 勾选后AI会先分析拆分任务
• 每步最多5次迭代
• 总迭代不超过15次

【智能界面】
• 截图和操作阶段自动隐藏
• 查看和思考阶段显示
• 任务结束界面保持显示

【请求补充信息】
• 当任务信息不完整时，AI会暂停
• 用户可以补充信息继续执行
• 可以修改原始任务描述

【故障安全】
• 快速移动鼠标到左上角
• 系统会立即停止

【注意事项】
• 屏幕左上角为(0,0)
• AI返回0-1归一化比例
• 不要在任务执行时手动操作
"""
        
        guide_content.insert(tk.END, guide_text)
        guide_content.config(state=tk.DISABLED)
    
    def log(self, message):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def update_step_display(self, info):
        """更新当前步骤显示"""
        self.current_step_info = info
        self.step_var.set(info)
        self.root.update()
    
    def update_action_display(self, info):
        """更新当前操作显示"""
        self.current_action_info = info
        self.action_var.set(info)
        self.root.update()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def on_shift_enter(self, event):
        """Shift+Enter: 换行"""
        self.input_text.insert(tk.INSERT, "\n")
        return "break"
    
    def on_enter_pressed(self, event):
        """Enter: 发送任务（或继续执行）"""
        if self.is_waiting_for_input:
            # 等待用户输入模式 - 使用输入内容继续
            self.continue_with_user_input()
            return "break"
        else:
            # 正常发送任务
            self.send_task()
            return "break"
    
    def initialize_system(self):
        """初始化系统"""
        if self.is_initialized:
            self.log("⚠️ 系统已初始化！")
            return
        
        self.log("⏳ 正在初始化系统...")
        self.root.update()
        
        try:
            self.system = FeishuCUASystem(fail_safe=True)
            # 设置窗口控制回调
            self.system.minimize_window_callback = self.hide_window
            self.system.show_window_callback = self.show_window
            
            self.is_initialized = True
            self.log(f"✅ 系统初始化完成！")
            self.log(f"📺 屏幕尺寸: {self.system.screen_w}x{self.system.screen_h}")
            self.log("\n请在下方输入你的任务描述，然后点击发送或按回车！")
            self.log("提示：Shift+Enter 可以换行输入多行任务")
            
            # 3秒准备时间
            self.log("\n⏳ 3秒后准备就绪，请准备好工作环境...")
            self.root.update()
            
            # 用非阻塞方式等待
            self.countdown = 3
            self.wait_and_ready()
            
        except Exception as e:
            self.log(f"❌ 初始化失败: {e}")
    
    def wait_and_ready(self):
        """倒计时准备"""
        if self.countdown > 0:
            self.log(f"   ... {self.countdown}")
            self.countdown -= 1
            self.root.after(1000, self.wait_and_ready)
        else:
            self.log("✅ 准备就绪！")
            self.init_btn.config(text="系统已就绪", bg="#95a5a6", state=tk.DISABLED)
            self.send_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.update_step_display("等待任务...")
            self.update_action_display("--")
    
    def hide_window(self):
        """隐藏窗口（用于截图和操作阶段）"""
        self.root.withdraw()
    
    def show_window(self):
        """显示窗口（用于查看状态阶段）"""
        self.root.deiconify()
    
    def send_task(self):
        """发送任务"""
        if not self.is_initialized:
            self.log("⚠️ 请先初始化系统！")
            return
        
        if self.is_running:
            self.log("⚠️ 任务正在执行中！")
            return
        
        # 获取任务描述
        user_task = self.input_text.get(1.0, tk.END).strip()
        if not user_task:
            self.log("⚠️ 请输入任务描述！")
            return
        
        self.current_task = user_task
        self.input_text.delete(1.0, tk.END)
        
        # 启动任务线程
        self.is_running = True
        self.send_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._run_task_thread, args=(user_task,))
        thread.daemon = True
        thread.start()
    
    def _run_task_thread(self, user_task):
        """任务执行线程"""
        try:
            use_planning = self.use_planning_var.get()
            self.log("\n" + "="*60)
            self.log(f"🚀 开始任务: {user_task}")
            self.log("="*60)
            self.update_step_display("任务执行中...")
            
            # 执行任务 - 带request_input支持
            self._execute_with_input_support(user_task, use_planning)
            
        except Exception as e:
            self.log(f"❌ 任务执行出错: {e}")
        finally:
            self.is_running = False
            self.send_btn.config(state=tk.NORMAL)
    
    def _execute_with_input_support(self, user_task, use_planning):
        """执行任务，支持等待用户输入"""
        current_task = user_task
        iteration_count = 0
        max_total_iterations = 30
        
        while iteration_count < max_total_iterations:
            # 检查是否需要停止
            if self.system.should_stop:
                self.log("\n" + "="*60)
                self.log("⏹️  任务已被用户终止")
                self.log("="*60)
                self.system.should_stop = False
                self.system.is_running = False
                return
            
            self.update_step_display(f"执行第 {iteration_count+1} 次迭代...")
            
            # 执行一次迭代
            result = self.system.execute_one_iteration(current_task, self._status_callback)
            
            # 检查是否被终止
            if result is None:
                return
            
            # 检查是否是请求用户输入
            if isinstance(result, dict) and result.get('type') == 'request_input':
                self._handle_request_input(result['prompt'])
                # 用户补充信息后，更新任务
                current_task = self.current_task
                self.log(f"📝 继续执行任务: {current_task}")
                iteration_count += 1
                continue
            
            # 检查是否任务完成
            if result is True:
                self.log("\n" + "="*60)
                self.log("✅ 任务完成！")
                self.log("="*60)
                self.update_step_display("任务完成")
                self.update_action_display("--")
                return
            
            # 继续执行
            iteration_count += 1
            self.system.auto.wait(2)
        
        # 达到最大迭代次数
        self.log("\n" + "="*60)
        self.log("⚠️  达到最大迭代次数，任务可能未完成")
        self.log("="*60)
        self.update_step_display("达到最大迭代次数")
    
    def _status_callback(self, message):
        """状态回调"""
        self.log(message)
        
        # 更新当前操作显示
        if "正在截图" in message:
            self.update_action_display("📷 截图中")
        elif "正在与AI通信" in message:
            self.update_action_display("🤖 思考中")
        elif "正在执行AI指令" in message:
            self.update_action_display("⚡ 执行中")
        elif "AI思考" in message:
            self.update_action_display("💭 思考中")
        elif "步骤" in message and "/" in message:
            self.update_step_display(message)
        elif "任务完成" in message:
            self.update_action_display("✅ 完成")
    
    def _handle_request_input(self, prompt):
        """处理请求用户输入"""
        self.is_waiting_for_input = True
        
        self.log("\n" + "="*60)
        self.log(f"🙋 AI需要更多信息:")
        self.log(f"   {prompt}")
        self.log("="*60)
        self.log("\n请在输入框中补充信息，然后按Enter继续...")
        
        # 更新显示
        self.update_step_display(f"等待用户输入: {prompt}")
        self.update_action_display("⌨️ 等待输入")
        
        # 清空输入框，提示用户
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(tk.END, f"# 补充信息: {prompt}\n\n")
        self.input_text.focus()
        
        # 等待用户输入 - 这里会阻塞，直到用户按Enter
        while self.is_waiting_for_input:
            self.root.update()
            time.sleep(0.1)
    
    def continue_with_user_input(self):
        """用户输入完成后继续执行"""
        # 获取用户输入
        user_input = self.input_text.get(1.0, tk.END).strip()
        
        if not user_input:
            self.log("⚠️ 请输入补充信息！")
            return
        
        # 更新任务 - 组合原始任务和补充信息
        if self.current_task:
            # 如果有原始任务，组合
            self.current_task = f"{self.current_task}\n\n补充信息: {user_input}"
        else:
            self.current_task = user_input
        
        self.log(f"📝 用户补充: {user_input}")
        self.log("⏳ 继续执行...")
        
        # 清空输入框
        self.input_text.delete(1.0, tk.END)
        
        # 恢复状态
        self.is_waiting_for_input = False
        self.update_step_display("继续执行...")
        self.update_action_display("⚡ 继续中")
    
    def stop_task(self):
        """停止当前任务"""
        if not self.is_running and not self.is_waiting_for_input:
            self.log("⚠️ 没有正在执行的任务！")
            return
        
        self.log("\n⏹️  正在停止任务...")
        self.system.should_stop = True
        self.is_waiting_for_input = False
        self.update_step_display("任务已终止")
        self.update_action_display("⏹️ 停止")


def main():
    root = tk.Tk()
    app = FeishuCUAGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
