import tkinter as tk
from tkinter import scrolledtext
import threading
import sys
import time
from feishu_cua import FeishuCUASystem


class FeishuCUAGUI:
    """飞书CUA系统图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("飞书CUA系统")
        
        # 设置窗口尺寸
        self.root.geometry("500x920")
        
        # 设置窗口置顶
        self.root.attributes("-topmost", True)
        
        # 初始化系统
        self.system = None
        self.is_initialized = False
        self.is_running = False
        
        # 创建界面
        self.create_widgets()
        
        # 绑定拖拽功能
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.drag_window)
        
        self.offset_x = 0
        self.offset_y = 0
        
        # 将窗口放到右上角
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"+{screen_width - 520}+20")
    
    def create_widgets(self):
        """创建界面组件"""
        # 标题栏
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="飞书CUA系统", bg="#2c3e50", fg="white", font=("微软雅黑", 12, "bold"))
        title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 关闭按钮
        close_btn = tk.Button(title_frame, text="×", bg="#e74c3c", fg="white", 
                              width=3, command=self.close_window,
                              relief=tk.FLAT)
        close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 最小化按钮
        min_btn = tk.Button(title_frame, text="−", bg="#f39c12", fg="white",
                           width=3, command=self.minimize_window,
                           relief=tk.FLAT)
        min_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 日志显示区域
        self.log_text = scrolledtext.ScrolledText(self.root, height=25, width=60,
                                               font=("微软雅黑", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text.config(state=tk.DISABLED)
        
        # 输入区域
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.input_entry = tk.Entry(input_frame, font=("微软雅黑", 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_entry.bind("<Return>", self.send_message)
        
        send_btn = tk.Button(input_frame, text="发送", bg="#3498db", fg="white",
                            command=self.send_message, width=8)
        send_btn.pack(side=tk.RIGHT)
        
        # 按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 初始化按钮
        self.init_btn = tk.Button(button_frame, text="初始化系统", bg="#27ae60",
                                  fg="white", command=self.initialize_system,
                                  height=2)
        self.init_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 终止按钮
        self.stop_btn = tk.Button(button_frame, text="终止", bg="#e74c3c",
                                  fg="white", command=self.stop_task,
                                  height=2, width=8, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.RIGHT)
        
        # 欢迎信息
        self.log("欢迎使用飞书CUA系统！")
        self.log("请点击【初始化系统】按钮开始。")
    
    def log(self, message):
        """添加日志到界面"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def initialize_system(self):
        """初始化系统"""
        if self.is_initialized:
            self.log("⚠️ 系统已初始化！")
            return
        
        self.log("⏳ 正在初始化系统...")
        self.root.update()
        
        try:
            self.system = FeishuCUASystem(fail_safe=True)
            self.is_initialized = True
            self.log(f"✅ 系统初始化完成！")
            self.log(f"📺 屏幕尺寸: {self.system.screen_w}x{self.system.screen_h}")
            self.log("\n请在下方输入你的任务描述，然后点击发送或按回车！")
            
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
            self.stop_btn.config(state=tk.NORMAL)
            self.keep_window_activated()
    
    def keep_window_activated(self):
        """每隔5秒检查并恢复窗口，防止被win+D关掉"""
        # 只在窗口被隐藏时才显示
        if not self.root.winfo_viewable():
            self.root.deiconify()  # 显示窗口
        # 不使用lift()和focus_force()，避免打断用户输入
        self.root.after(5000, self.keep_window_activated)  # 5秒后再次执行
    
    def stop_task(self):
        """停止当前任务"""
        if not self.is_running:
            self.log("⚠️ 当前没有正在执行的任务")
            return
        
        if self.system:
            self.log("⏹️ 正在终止任务...")
            self.system.should_stop = True
    
    def send_message(self, event=None):
        """发送任务"""
        if not self.is_initialized:
            self.log("⚠️ 请先点击【初始化系统】！")
            return
        
        if self.is_running:
            self.log("⚠️ 当前任务正在执行中，请稍候...")
            return
        
        task = self.input_entry.get().strip()
        if not task:
            return
        
        self.input_entry.delete(0, tk.END)
        
        # 在新线程中执行任务
        self.is_running = True
        thread = threading.Thread(target=self.run_task_thread, args=(task,))
        thread.daemon = True
        thread.start()
    
    def run_task_thread(self, task):
        """在后台线程运行任务"""
        try:
            def gui_callback(msg):
                self.root.after(0, lambda: self.log(msg))
            
            self.system.run_task(task, max_iterations=15, callback=gui_callback)
        except Exception as e:
            self.log(f"❌ 执行出错: {e}")
        finally:
            self.is_running = False
    
    def close_window(self):
        """关闭窗口"""
        self.root.destroy()
        sys.exit(0)
    
    def minimize_window(self):
        """最小化窗口"""
        self.root.withdraw()
        # 3秒后重新显示
        self.root.after(3000, self.root.deiconify)
    
    def start_drag(self, event):
        """开始拖拽"""
        self.offset_x = event.x
        self.offset_y = event.y
    
    def drag_window(self, event):
        """拖拽窗口"""
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")


def main():
    """主函数"""
    root = tk.Tk()
    app = FeishuCUAGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
