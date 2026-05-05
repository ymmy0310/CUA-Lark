# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import threading
import sys
import time
import os
from feishu_cua import FeishuCUASystem
import config_manager
from window_controller import check_signal


class APIConfigWindow:
    """API配置窗口"""
    
    def __init__(self, parent, on_save_callback=None):
        self.window = tk.Toplevel(parent)
        self.window.title("API配置")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.attributes("-topmost", True)
        self.on_save_callback = on_save_callback
        
        self.center_window()
        
        self.current_config = config_manager.load_config() or config_manager.create_default_config()
        
        self.create_widgets()
    
    def center_window(self):
        """窗口居中"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建配置界面组件"""
        
        title_frame = tk.Frame(self.window)
        title_frame.pack(pady=(15, 10), fill="x", padx=10)
        
        title_label = tk.Label(title_frame, text="🔧 API配置", font=("微软雅黑", 14, "bold"))
        title_label.pack(side="left", padx=(10, 0))
        
        url_frame = tk.Frame(self.window)
        url_frame.pack(pady=5, padx=20, fill="x")
        
        tk.Label(url_frame, text="API地址：", font=("微软雅黑", 10)).pack(side="left")
        
        preset_frame = tk.Frame(url_frame)
        preset_frame.pack(side="left", padx=(5, 0))
        
        tk.Label(preset_frame, text="预设：", font=("微软雅黑", 10)).pack(side="left")
        
        self.preset_var = tk.StringVar(value="自定义API")
        preset_menu = ttk.Combobox(preset_frame, textvariable=self.preset_var, 
                                   values=list(config_manager.API_PRESETS.keys()), 
                                   state="readonly", width=18)
        preset_menu.pack(side="left", padx=(5, 0))
        preset_menu.bind("<<ComboboxSelected>>", self.on_preset_changed)
        
        self.url_var = tk.StringVar(value=self.current_config.get("api_endpoint", ""))
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, width=40, font=("微软雅黑", 10))
        self.url_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        current_url = self.current_config.get("api_endpoint", "")
        volcano_url = config_manager.API_PRESETS.get("火山引擎（豆包）", "")
        if current_url == volcano_url and volcano_url:
            self.preset_var.set("火山引擎（豆包）")
            self.url_entry.config(state="readonly")
        
        key_frame = tk.Frame(self.window)
        key_frame.pack(pady=5, padx=20, fill="x")
        
        tk.Label(key_frame, text="API Key：", font=("微软雅黑", 10)).pack(side="left")
        self.key_var = tk.StringVar(value=self.current_config.get("api_key", ""))
        key_entry = tk.Entry(key_frame, textvariable=self.key_var, width=50, font=("微软雅黑", 10), show="*")
        key_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        endpoint_frame = tk.Frame(self.window)
        endpoint_frame.pack(pady=5, padx=20, fill="x")
        
        tk.Label(endpoint_frame, text="接入点ID：", font=("微软雅黑", 10)).pack(side="left")
        self.endpoint_var = tk.StringVar(value=self.current_config.get("endpoint_id", ""))
        endpoint_entry = tk.Entry(endpoint_frame, textvariable=self.endpoint_var, width=50, font=("微软雅黑", 10))
        endpoint_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        hint_label = tk.Label(self.window, text="提示：从火山方舟控制台获取 API Key 和接入点 ID", 
                             font=("微软雅黑", 9), fg="#666")
        hint_label.pack(pady=(15, 5))
        
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=(10, 15))
        
        save_button = tk.Button(button_frame, text="💾 保存", command=self.save_config, 
                               bg="#4CAF50", fg="white", font=("微软雅黑", 11), width=12)
        save_button.pack(side="left", padx=(0, 10))
        
        cancel_button = tk.Button(button_frame, text="❌ 取消", command=self.window.destroy, 
                                 font=("微软雅黑", 11), width=12)
        cancel_button.pack(side="left")
    
    def on_preset_changed(self, event):
        """预设地址改变时"""
        selected = self.preset_var.get()
        if selected in config_manager.API_PRESETS:
            url = config_manager.API_PRESETS[selected]
            if url:
                self.url_var.set(url)
                self.url_entry.config(state="readonly")
            else:
                self.url_entry.config(state="normal")
    
    def save_config(self):
        """保存配置"""
        config = {
            "api_endpoint": self.url_var.get().strip(),
            "api_key": self.key_var.get().strip(),
            "endpoint_id": self.endpoint_var.get().strip(),
            "temperature": 0.1,
            "max_tokens": 2000,
        }
        
        if not config["api_key"] or not config["endpoint_id"]:
            messagebox.showwarning("警告", "请填写 API Key 和接入点 ID！", parent=self.window)
            return
        
        if config_manager.save_config(config):
            messagebox.showinfo("成功", "API配置已保存！", parent=self.window)
            if self.on_save_callback:
                self.on_save_callback(config)
            self.window.destroy()
        else:
            messagebox.showerror("错误", "保存配置失败！", parent=self.window)


class MiniControlBar:
    """迷你控制条 - 任务执行时显示在左下角"""
    
    def __init__(self, parent, on_pause=None, on_continue=None):
        self.parent = parent
        self.on_pause = on_pause
        self.on_continue = on_continue
        self.is_expanded = False
        
        self.window = tk.Toplevel(parent)
        self.window.title("CUA控制")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.9)
        
        self.screen_w = self.window.winfo_screenwidth()
        self.screen_h = self.window.winfo_screenheight()
        
        self.collapsed_w = 380  # 宽度380像素
        self.collapsed_h = 40
        self.expanded_w = 500  # 同步增加
        self.expanded_h = 200

        # 不再隐藏到边缘，直接显示在左下角
        self.shown_x = 10
        self.shown_y = self.screen_h - self.collapsed_h - 60

        self.window.geometry(f"{self.collapsed_w}x{self.collapsed_h}+{self.shown_x}+{self.shown_y}")
        
        self.create_widgets()
        self.bind_events()
        
        self.window.withdraw()
    
    def create_widgets(self):
        """创建控制条组件"""
        self.main_frame = tk.Frame(self.window, bg="#2c3e50", bd=1, relief="solid")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 头部按钮栏（始终显示在底部）
        self.header_frame = tk.Frame(self.main_frame, bg="#2c3e50", height=38)
        self.header_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.header_frame.pack_propagate(False)

        self.status_label = tk.Label(self.header_frame, text="⏳ 准备中",
                                     bg="#2c3e50", fg="#ffffff",
                                     font=("微软雅黑", 10, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=(10, 5))

        # 按钮顺序：暂停 | 继续 | 展开日志
        self.pause_btn = tk.Button(self.header_frame, text="⏸", bg="#e67e22", fg="white",
                                   font=("微软雅黑", 9, "bold"), width=3,
                                   command=self._on_pause_click)
        self.pause_btn.pack(side=tk.RIGHT, padx=(0, 5))
        self.pause_btn.bind("<Enter>", lambda e: self.show_tooltip("暂停任务"))
        self.pause_btn.bind("<Leave>", lambda e: self.hide_tooltip())

        self.continue_btn = tk.Button(self.header_frame, text="▶", bg="#27ae60", fg="white",
                                      font=("微软雅黑", 9, "bold"), width=3,
                                      command=self._on_continue_click, state=tk.DISABLED)
        self.continue_btn.pack(side=tk.RIGHT, padx=(0, 3))
        self.continue_btn.bind("<Enter>", lambda e: self.show_tooltip("继续任务"))
        self.continue_btn.bind("<Leave>", lambda e: self.hide_tooltip())

        self.expand_btn = tk.Button(self.header_frame, text="📋", bg="#34495e", fg="white",
                                    font=("微软雅黑", 8), width=3,
                                    command=self.toggle_expand)
        self.expand_btn.pack(side=tk.RIGHT, padx=(0, 3))
        self.expand_btn.bind("<Enter>", lambda e: self.show_tooltip("展开/收起日志"))
        self.expand_btn.bind("<Leave>", lambda e: self.hide_tooltip())

        # 添加按钮提示标签
        self.tooltip_label = tk.Label(self.header_frame, text="",
                                      bg="#2c3e50", fg="#bdc3c7",
                                      font=("微软雅黑", 8))
        self.tooltip_label.pack(side=tk.RIGHT, padx=(0, 5))

        # 详情面板（展开时显示在头部上方）
        self.detail_frame = tk.Frame(self.main_frame, bg="#34495e")

        self.step_label = tk.Label(self.detail_frame, text="步骤: --",
                                   bg="#34495e", fg="#3498db",
                                   font=("微软雅黑", 9), anchor=tk.W)
        self.step_label.pack(fill=tk.X, padx=10, pady=(5, 0))

        self.action_label = tk.Label(self.detail_frame, text="操作: --",
                                     bg="#34495e", fg="#e67e22",
                                     font=("微软雅黑", 9), anchor=tk.W)
        self.action_label.pack(fill=tk.X, padx=10, pady=(3, 0))

        self.log_text = scrolledtext.ScrolledText(self.detail_frame, height=9, width=45,
                                                  font=("微软雅黑", 8), bg="#2c3e50", fg="#ecf0f1")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.log_text.config(state=tk.DISABLED)
    
    def bind_events(self):
        """绑定鼠标事件"""
        # 移除悬停自动展开，改为点击展开按钮
        self.header_frame.bind("<Button-1>", self.start_drag)
        self.header_frame.bind("<B1-Motion>", self.on_drag)
        self.status_label.bind("<Button-1>", self.start_drag)
        self.status_label.bind("<B1-Motion>", self.on_drag)

    def start_drag(self, event):
        self.drag_x = event.x_root - self.window.winfo_x()
        self.drag_y = event.y_root - self.window.winfo_y()

    def on_drag(self, event):
        x = event.x_root - self.drag_x
        y = event.y_root - self.drag_y
        self.window.geometry(f"+{x}+{y}")
    
    def toggle_expand(self):
        """展开/收起详情（向上展开）"""
        # 获取当前窗口位置
        current_x = self.window.winfo_x()
        current_y = self.window.winfo_y()
        
        if self.is_expanded:
            # 收起：先隐藏详情面板，再调整窗口大小
            self.detail_frame.pack_forget()
            self.expand_btn.config(text="📋")
            # 窗口向下移动，保持底部按钮位置不变
            collapsed_y = current_y + (self.expanded_h - self.collapsed_h)
            self.window.geometry(f"{self.collapsed_w}x{self.collapsed_h}+{current_x}+{collapsed_y}")
            self.is_expanded = False
        else:
            # 展开：先调整窗口大小和位置，再显示详情面板
            expand_y = current_y - (self.expanded_h - self.collapsed_h)
            self.window.geometry(f"{self.expanded_w}x{self.expanded_h}+{current_x}+{expand_y}")
            # 使用 after 确保窗口布局完成后再 pack 详情面板
            self.detail_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.expand_btn.config(text="🔽")
            self.is_expanded = True
    
    def show(self):
        """显示控制条"""
        self.window.deiconify()
        self.window.geometry(f"{self.collapsed_w}x{self.collapsed_h}+{self.shown_x}+{self.shown_y}")
    
    def hide(self):
        """隐藏控制条"""
        self.window.withdraw()
        self.is_expanded = False
        self.detail_frame.pack_forget()
        self.expand_btn.config(text="📋")
    
    def update_status(self, status):
        """更新状态文本"""
        self.status_label.config(text=status)
    
    def update_step(self, step):
        """更新步骤信息"""
        self.step_label.config(text=f"步骤: {step}")
    
    def update_action(self, action):
        """更新操作信息"""
        self.action_label.config(text=f"操作: {action}")
    
    def log(self, message):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def set_pause_state(self, is_paused):
        """设置暂停/继续按钮状态"""
        if is_paused:
            self.pause_btn.config(state=tk.DISABLED)
            self.continue_btn.config(state=tk.NORMAL)
        else:
            self.pause_btn.config(state=tk.NORMAL)
            self.continue_btn.config(state=tk.DISABLED)
    
    def _on_pause_click(self):
        if self.on_pause:
            self.on_pause()
    
    def _on_continue_click(self):
        if self.on_continue:
            self.on_continue()

    def show_tooltip(self, text):
        """显示按钮提示"""
        self.tooltip_label.config(text=text)

    def hide_tooltip(self):
        """隐藏按钮提示"""
        self.tooltip_label.config(text="")


class FeishuCUAGUI:
    """飞书CUA系统图形界面 - v3.5 升级版本"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("飞书CUA系统 v3.5")
        
        self.window_width = 1400
        self.window_height = 1100
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        self.system = None
        self.is_initialized = False
        self.is_running = False
        self.is_waiting_for_input = False
        self.original_task = ""  # 保存原始任务
        self.current_task = ""
        self.current_step_info = ""
        self.current_action_info = ""
        
        self.create_widgets()
        self.create_mini_bar()
        
        # 启动窗口控制信号检查
        self.start_window_control_check()
        
        self.check_config_on_start()
    
    def start_window_control_check(self):
        """启动窗口控制信号检查（每500ms检查一次）"""
        self._check_window_signal()
    
    def _check_window_signal(self):
        """检查是否有外部窗口控制信号"""
        signal = check_signal()
        if signal == "SHOW":
            self.log("📩 收到外部信号：显示主窗口")
            self.show_main_window()
        elif signal == "HIDE":
            self.log("📩 收到外部信号：隐藏主窗口")
            self.hide_main_window()
        
        # 继续检查
        self.root.after(500, self._check_window_signal)
    
    def create_widgets(self):
        """创建主界面组件"""
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = tk.Frame(main_paned)
        main_paned.add(left_frame, minsize=700)
        
        right_frame = tk.Frame(main_paned, bg="#f0f4f8")
        main_paned.add(right_frame, minsize=280)
        
        top_info_frame = tk.Frame(left_frame, bg="#2c3e50", height=100)
        top_info_frame.pack(fill=tk.X)
        top_info_frame.pack_propagate(False)
        
        step_label = tk.Label(top_info_frame, text="当前步骤:", bg="#2c3e50", fg="#3498db", 
                              font=("微软雅黑", 12, "bold"))
        step_label.place(x=15, y=10)
        
        self.step_var = tk.StringVar(value="等待任务...")
        self.step_display = tk.Label(top_info_frame, textvariable=self.step_var, bg="#2c3e50", 
                                     fg="#ffffff", font=("微软雅黑", 11), wraplength=500, justify=tk.LEFT)
        self.step_display.place(x=15, y=40)
        
        action_label = tk.Label(top_info_frame, text="当前操作:", bg="#2c3e50", fg="#e67e22", 
                               font=("微软雅黑", 12, "bold"))
        action_label.place(x=550, y=10)
        
        self.action_var = tk.StringVar(value="--")
        self.action_display = tk.Label(top_info_frame, textvariable=self.action_var, bg="#2c3e50", 
                                      fg="#ffffff", font=("微软雅黑", 11), wraplength=180, justify=tk.LEFT)
        self.action_display.place(x=550, y=40)
        
        log_frame = tk.Frame(left_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        log_label = tk.Label(log_frame, text="执行日志:", font=("微软雅黑", 10, "bold"), anchor=tk.W)
        log_label.pack(fill=tk.X, padx=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80,
                                                 font=("微软雅黑", 11), bg="#fafbfc")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5)
        self.log_text.config(state=tk.DISABLED)
        
        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_label = tk.Label(input_frame, text="任务描述:", font=("微软雅黑", 10, "bold"), anchor=tk.W)
        input_label.pack(fill=tk.X, padx=5)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=4, width=80,
                                                    font=("微软雅黑", 11), bg="#ffffff")
        self.input_text.pack(fill=tk.X, padx=5, pady=(5, 5))
        self.input_text.bind("<Return>", self.on_enter_pressed)
        self.input_text.bind("<Shift-Return>", self.on_shift_enter)
        
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
        
        self.pause_btn = tk.Button(button_frame, text="⏸ 暂停", bg="#e67e22", fg="white",
                                   font=("微软雅黑", 10, "bold"), width=8,
                                   command=self.pause_task, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=3)
        
        self.continue_btn = tk.Button(button_frame, text="▶ 继续", bg="#27ae60", fg="white",
                                      font=("微软雅黑", 10, "bold"), width=8,
                                      command=self.resume_task, state=tk.DISABLED)
        self.continue_btn.pack(side=tk.LEFT, padx=3)
        
        self.clear_btn = tk.Button(button_frame, text="清空日志", bg="#95a5a6", fg="white",
                                  font=("微软雅黑", 11), width=12,
                                  command=self.clear_log)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.config_btn = tk.Button(button_frame, text="🔧 API配置", bg="#3498db", fg="white",
                                    font=("微软雅黑", 11), width=12,
                                    command=self.open_config_window)
        self.config_btn.pack(side=tk.LEFT, padx=5)
        
        guide_label = tk.Label(right_frame, text="📖 使用说明", bg="#f0f4f8", 
                               font=("微软雅黑", 13, "bold"))
        guide_label.pack(pady=(15, 10))
        
        guide_content = scrolledtext.ScrolledText(right_frame, height=35, width=30,
                                                 font=("微软雅黑", 9), bg="#ffffff")
        guide_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 15))
        
        guide_text = """
【快速开始】
1. 点击"初始化系统"
2. 等待3秒准备就绪
3. 在输入框输入任务描述
4. 按Enter发送（Shift+Enter换行）
【AI支持的操作】
• 鼠标: left_click / right_click / double_click / drag / scroll
• 输入文本(唯一方式): click_paste (点击+粘贴一步完成)
• 选中文本(连招): select_text (点击+ctrl+a一步完成，用于替换已有内容)
• 键盘: press_key / hotkey (如ctrl+v)
• 文件: open_folder / copy_file / move_file
• 窗口控制: show_cua_window(显示主窗口) / hide_cua_window(隐藏主窗口)
• 任务控制: task_completed(完成) / request_input(求助)

【暂停与继续】
• ⏸ 暂停：随时暂停任务，可手动介入操作
• ▶ 继续：恢复执行（用输入框内容或默认"继续"）
• 暂停后不会丢失上下文，AI记得之前做了什么

【迷你控制条】
• 任务执行时主窗口自动隐藏，左下角显示迷你控制条
• 控制条显示实时状态、暂停/继续按钮、日志展开按钮
• 支持鼠标拖拽调整位置
• 暂停/request_input时自动恢复主窗口

【安全机制】
• 最大迭代250次，防止无限循环
• 连续相同操作超3次自动请求帮助
• API限流时指数退避重试

【注意事项】
• 坐标为0-1归一化比例，AI自动换算像素
• 终止后补充信息会写入对话历史，AI记得之前做了什么
• 不同任务之间对话历史保留，AI有连续记忆
"""
        
        guide_content.insert(tk.END, guide_text)
        guide_content.config(state=tk.DISABLED)
    
    def create_mini_bar(self):
        """创建迷你控制条"""
        self.mini_bar = MiniControlBar(
            self.root,
            on_pause=self.pause_task,
            on_continue=self.resume_task
        )
    
    def log(self, message):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.mini_bar.log(message)
        self.root.update()
    
    def update_step_display(self, info):
        """更新当前步骤显示"""
        self.current_step_info = info
        self.step_var.set(info)
        self.mini_bar.update_step(info)
        self.root.update()
    
    def update_action_display(self, info):
        """更新当前操作显示"""
        self.current_action_info = info
        self.action_var.set(info)
        self.mini_bar.update_action(info)
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
        """Enter: 发送任务（或暂停时发送备注到历史）"""
        if self.is_waiting_for_input:
            self._send_note_during_pause()
            return "break"
        else:
            self.send_task()
            return "break"
    
    def _send_note_during_pause(self):
        """暂停/等待状态：发送备注写入历史，不恢复执行"""
        user_input = self.input_text.get(1.0, tk.END).strip()
        if not user_input:
            return
        
        self.log(f"📝 备注已记录: {user_input}")
        self.system.add_to_history("user", f"[用户备注] {user_input}")
        self.input_text.delete(1.0, tk.END)
    
    def initialize_system(self):
        """初始化系统"""
        if self.is_initialized:
            self.log("⚠️ 系统已初始化！")
            return
        
        self.log("⏳ 正在初始化系统...")
        self.root.update()
        
        try:
            self.system = FeishuCUASystem(fail_safe=True)
            self.system.minimize_window_callback = self.hide_window_for_screenshot
            self.system.show_window_callback = self.show_window_after_screenshot
            
            self.is_initialized = True
            self.log(f"✅ 系统初始化完成！")
            self.log(f"📺 屏幕尺寸: {self.system.screen_w}x{self.system.screen_h}")
            self.log("\n请在下方输入你的任务描述，然后点击发送或按回车！")
            self.log("提示：Shift+Enter 可以换行输入多行任务")
            
            self.log("\n⏳ 3秒后准备就绪，请准备好工作环境...")
            self.root.update()
            
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
            self.pause_btn.config(state=tk.NORMAL)
            self.update_step_display("等待任务...")
            self.update_action_display("--")
    
    def hide_window_for_screenshot(self):
        """截图前隐藏主窗口（不影响任务栏其他图标位置）"""
        self.root.withdraw()
    
    def show_window_after_screenshot(self):
        """截图后恢复主窗口"""
        if not self.is_running:
            self.root.deiconify()
    
    def hide_main_window(self):
        """任务开始后隐藏主窗口，显示迷你控制条"""
        self.root.withdraw()
        self.mini_bar.show()
        self.mini_bar.set_pause_state(False)
    
    def show_main_window(self):
        """显示主窗口，隐藏迷你控制条"""
        self.mini_bar.hide()
        self.root.deiconify()
        self.root.lift()
    
    def send_task(self):
        """发送任务"""
        if not self.is_initialized:
            self.log("⚠️ 请先初始化系统！")
            return
        
        if self.is_running:
            self.log("⚠️ 任务正在执行中！")
            return
        
        user_task = self.input_text.get(1.0, tk.END).strip()
        if not user_task:
            self.log("⚠️ 请输入任务描述！")
            return
        
        self.original_task = user_task  # 保存原始任务
        self.current_task = user_task
        self.input_text.delete(1.0, tk.END)
        
        self.is_running = True
        self.send_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.continue_btn.config(state=tk.DISABLED)
        
        self.hide_main_window()
        
        thread = threading.Thread(target=self._run_task_thread, args=(user_task,))
        thread.daemon = True
        thread.start()
    
    def _run_task_thread(self, user_task):
        """任务执行线程"""
        try:
            self.update_step_display("任务执行中...")
            self._execute_with_input_support(user_task)
        except Exception as e:
            self.log(f"❌ 任务执行出错: {e}")
        finally:
            self.is_running = False
            self.send_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            self.continue_btn.config(state=tk.DISABLED)
            self.mini_bar.set_pause_state(False)
            self.show_main_window()
    
    def _execute_with_input_support(self, user_task):
        """执行任务，处理用户输入交互"""
        
        # 标记是否是理解确认阶段
        is_understanding_phase = True

        while True:
            # 理解确认阶段使用 skip_understanding=False，后续循环使用 skip_understanding=True
            result = self.system.run_task(
                user_task, 
                max_iterations=250, 
                callback=self._status_callback,
                skip_understanding=not is_understanding_phase
            )
            
            # 第一次循环后，就不再是理解确认阶段了
            is_understanding_phase = False

            if result is None:
                return
            elif result is True:
                self.update_step_display("任务完成")
                self.update_action_display("--")
                return
            elif isinstance(result, dict) and result.get('type') == 'request_input':
                phase = result.get('phase', '')
                
                # 判断是否是任务理解确认阶段
                if phase == 'understanding_confirmation':
                    self.log("\n" + "="*60)
                    self.log("🧠 任务理解确认")
                    self.log("="*60)
                    
                    self._handle_understanding_confirmation(result)
                else:
                    self.log("\n" + "="*60)
                    self.log("🙋 AI请求帮助")
                    self.log("="*60)
                    self._handle_request_input(result['prompt'])

                if not self.is_running:
                    return

                # 暂停时用户输入的内容加入历史记录，不开启新任务
                user_feedback = self.current_task
                if user_feedback and user_feedback != "继续":
                    self.log(f"📝 用户反馈: {user_feedback}")
                    self.system.add_to_history("user", f"[用户反馈] {user_feedback}")

                self.system.auto.wait(1)
                continue
            else:
                self.update_step_display("达到最大迭代次数")
                return
    
    def _handle_understanding_confirmation(self, result):
        """处理任务理解确认"""
        self.is_waiting_for_input = True
        
        self.show_main_window()
        
        understanding = result.get('understanding', {})
        prompt = result.get('prompt', '请确认或补充信息')
        
        # 设置默认文本
        is_complete = understanding.get('is_complete', False)
        if is_complete:
            default_text = "确认"
        else:
            default_text = ""
        
        self.input_text.delete(1.0, tk.END)
        if default_text:
            self.input_text.insert(tk.END, default_text)
        self.input_text.focus()
        
        self.pause_btn.config(state=tk.DISABLED)
        self.continue_btn.config(state=tk.DISABLED)
        self.send_btn.config(text="确认并执行", command=self._confirm_understanding, state=tk.NORMAL)
        self.update_step_display("等待确认...")
        self.update_action_display("🧠 理解确认")
        self.mini_bar.set_pause_state(True)
        
        while self.is_waiting_for_input:
            self.root.update()
            time.sleep(0.1)
    
    def _confirm_understanding(self):
        """用户确认理解后继续执行"""
        user_input = self.input_text.get(1.0, tk.END).strip()
        
        if not user_input:
            self.log("⚠️ 请输入确认信息！")
            return
        
        # 用户输入"确认"或"无意见"表示直接开始执行
        if user_input in ["确认", "无意见", "ok", "OK", "开始"]:
            self.log("✅ 用户确认，开始执行任务...")
            # 不修改 current_task，保持原始任务
        else:
            # 用户补充了信息，追加到任务中
            self.current_task = f"{self.current_task}\n\n补充信息: {user_input}"
            self.log(f"📝 用户补充: {user_input}")
            self.system.add_to_history("user", f"[用户补充信息] {user_input}")
        
        self.input_text.delete(1.0, tk.END)
        
        self.is_waiting_for_input = False
        self.send_btn.config(text="发送任务", command=self.send_task)
        self.pause_btn.config(state=tk.NORMAL)
        self.continue_btn.config(state=tk.DISABLED)
        self.update_step_display("开始执行...")
        self.update_action_display("⚡ 执行中")
    
    def _status_callback(self, message):
        """状态回调"""
        self.log(message)
        
        if "正在截图" in message:
            self.update_action_display("📷 截图中")
            self.mini_bar.update_status("📷 截图中")
        elif "正在与AI通信" in message:
            self.update_action_display("🤖 思考中")
            self.mini_bar.update_status("🤖 思考中")
        elif "正在执行AI指令" in message:
            self.update_action_display("⚡ 执行中")
            self.mini_bar.update_status("⚡ 执行中")
        elif "AI思考" in message:
            self.update_action_display("💭 思考中")
            self.mini_bar.update_status("💭 思考中")
        elif "步骤" in message and "/" in message:
            self.update_step_display(message)
        elif "任务完成" in message:
            self.update_action_display("✅ 完成")
            self.mini_bar.update_status("✅ 完成")
    
    def _handle_request_input(self, prompt):
        """处理请求用户输入"""
        self.is_waiting_for_input = True
        
        self.show_main_window()
        
        self.log("\n" + "="*60)
        self.log(f"🙋 AI需要更多信息:")
        self.log(f"   {prompt}")
        self.log("="*60)
        
        default_text = "无意见" if "规划" in prompt or "审阅" in prompt else ""
        self.input_text.delete(1.0, tk.END)
        if default_text:
            self.input_text.insert(tk.END, default_text)
        self.input_text.focus()
        
        self.pause_btn.config(state=tk.DISABLED)
        self.continue_btn.config(state=tk.NORMAL)
        self.send_btn.config(text="发送建议", command=self._send_note_during_pause, state=tk.NORMAL)
        self.update_step_display("等待输入...")
        self.update_action_display("⏸️ 已暂停")
        self.mini_bar.set_pause_state(True)
        
        while self.is_waiting_for_input:
            self.root.update()
            time.sleep(0.1)
    
    def continue_with_user_input(self):
        """用户输入完成后继续执行"""
        user_input = self.input_text.get(1.0, tk.END).strip()
        
        if not user_input:
            self.log("⚠️ 请输入补充信息！")
            return
        
        if self.current_task:
            self.current_task = f"{self.current_task}\n\n补充信息: {user_input}"
        else:
            self.current_task = user_input
        
        self.log(f"📝 用户补充: {user_input}")
        self.log("⏳ 继续执行...")
        
        self.system.add_to_history("user", f"[用户补充信息] {user_input}")
        
        self.input_text.delete(1.0, tk.END)
        
        self.is_waiting_for_input = False
        self.pause_btn.config(state=tk.NORMAL)
        self.continue_btn.config(state=tk.DISABLED)
        self.update_step_display("继续执行...")
        self.update_action_display("⚡ 继续中")
    
    def pause_task(self):
        """暂停当前任务"""
        if not self.is_running and not self.is_waiting_for_input:
            self.log("⚠️ 没有正在执行的任务！")
            return
        
        self.log("\n" + "="*60)
        self.log("⏸️  正在暂停任务...")
        self.log("="*60)
        self.system.should_stop = True
        self.is_waiting_for_input = True
        self.pause_btn.config(state=tk.DISABLED)
        self.continue_btn.config(state=tk.DISABLED)
        self.update_action_display("⏸️ 暂停中...")
        self.mini_bar.set_pause_state(True)
    
    def resume_task(self):
        """继续已暂停的任务"""
        if not self.is_waiting_for_input:
            self.log("⚠️ 没有等待中的任务！")
            return
        
        user_input = self.input_text.get(1.0, tk.END).strip()
        if not user_input:
            user_input = "继续"
        
        self.current_task = user_input
        
        if user_input != "继续":
            self.log(f"📝 用户输入: {user_input}")
            self.system.add_to_history("user", f"[用户补充信息] {user_input}")
        else:
            self.log("📝 用户选择继续执行")
        
        self.input_text.delete(1.0, tk.END)
        self.is_waiting_for_input = False
        
        self.send_btn.config(text="发送任务", command=self.send_task)
        self.pause_btn.config(state=tk.NORMAL)
        self.continue_btn.config(state=tk.DISABLED)
        self.update_step_display("继续执行...")
        self.update_action_display("▶ 继续中")
        self.mini_bar.set_pause_state(False)
        
        self.hide_main_window()
    
    def check_config_on_start(self):
        """启动时检查配置"""
        if not config_manager.is_configured():
            messagebox.showinfo("欢迎使用", "首次使用，请先配置 API 信息！")
            self.open_config_window()
    
    def open_config_window(self):
        """打开API配置窗口"""
        self._config_window = APIConfigWindow(self.root, self.on_config_saved)
    
    def on_config_saved(self, config):
        """配置保存后的回调"""
        self.log(f"✅ API配置已更新！")
        self.log(f"   API地址: {config['api_endpoint']}")
        self.log(f"   接入点ID: {config['endpoint_id']}")


def main():
    root = tk.Tk()
    app = FeishuCUAGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
