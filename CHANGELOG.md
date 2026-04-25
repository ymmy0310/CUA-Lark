# Desktop Automation 开发日志

## 版本：v1.0

### 最终功能列表

#### 底层功能
- ✅ 鼠标左右键点击（支持指定坐标和当前位置）
- ✅ 键盘字符输入
- ✅ 热键/快捷键操作
- ✅ 剪贴板操作（复制/粘贴）
- ✅ 鼠标滚轮滚动

#### 二层功能
- ✅ 组合快捷键
- ✅ 鼠标拖拽
- ✅ 鼠标双击
- ✅ 鼠标悬停
- ✅ 区域框选

#### 核心方法
```python
auto = DesktopAutomation(fail_safe=False, pause_duration=0.5)

# 文本输入（默认剪贴板方式，兼容中英文）
auto.type_text(text, use_clipboard=True)

# 密码输入（直接键盘输入，安全）
auto.type_password(password, confirm=True)

# 基础操作
auto.left_click(x, y)
auto.right_click(x, y)
auto.double_click(x, y)
auto.hover(x, y, duration)
auto.drag_to(end_x, end_y, start_x, start_y, duration)
auto.scroll(clicks, x, y)
auto.select_area(start_x, start_y, end_x, end_y, duration)

# 键盘操作
auto.press_key(key, presses, interval)
auto.hotkey(*keys, interval)

# 剪贴板
auto.copy_to_clipboard(text)
auto.get_from_clipboard()

# 辅助功能
auto.get_mouse_position()
auto.get_screen_size()
auto.wait(seconds)
```

---

### 开发过程中遇到的问题及解决方案

#### 问题 1：中文输入法干扰命令输入
**问题描述**：
- 运行 `auto.type_text('notepad')` 后没有打开记事本
- 原因是用户使用中文输入法，按 `Enter` 只是确认输入而不是执行命令

**尝试的解决方案**：
1. ❌ 使用 `Shift` 键切换中英文模式 - 但如果本来就是英文输入，会切回中文
2. ❌ 使用 `Win+Space` 切换输入法 - 但用户有多个输入法（日语 + 微软拼音），会切换到日语
3. ❌ 检测当前输入模式 - 实现复杂，不同系统 API 不同

**最终解决方案**：
✅ **统一使用剪贴板粘贴方式**
- 所有文本输入默认使用 `use_clipboard=True`
- 剪贴板方式不受输入法影响，支持中英文
- 只在输入密码时使用直接键盘输入（密码框会自动切换英文模式）

**代码变更**：
```python
def type_text(self, text: str, interval: float = 0.0, use_clipboard: bool = True):
    if use_clipboard:
        self.copy_to_clipboard(text)
        self.hotkey('ctrl', 'v')
    else:
        pyautogui.typewrite(text, interval=interval)

def type_password(self, password: str, confirm: bool = True):
    pyautogui.typewrite(password, interval=0.02)
    if confirm:
        self.press_key('enter')
        self.press_key('enter')
```

**删除的代码**：
- `switch_to_english()` - 输入法切换函数
- `ensure_english_mode()` - 确保英文模式函数
- `input_command()` - 安全输入命令函数
- `input_text_safe()` - 安全输入文本函数

---

#### 问题 2：鼠标点击位置不确定
**问题描述**：
- 示例代码中 `auto.left_click()` 可能在任意位置点击
- 可能点到桌面图标而不是记事本窗口

**解决方案**：
✅ 获取屏幕中心坐标，确保点击在窗口内
```python
screen_w, screen_h = auto.get_screen_size()
center_x, center_y = screen_w // 2, screen_h // 2
auto.hover(center_x, center_y, duration=0.3)
auto.left_click()
```

---

#### 问题 3：Alt+F4 无法关闭记事本
**问题描述**：
- `auto.hotkey('alt', 'f4')` 能关闭 Trae 却关不掉记事本
- 原因：焦点可能不在记事本窗口上

**尝试的解决方案**：
1. ❌ 先点击记事本确保焦点 - 仍然有时失效
2. ❌ 使用 psutil 查找并 kill 进程 - 进程名大小写问题

**最终解决方案**：
✅ 使用 Windows 系统命令强制关闭
```python
import subprocess
subprocess.run(['taskkill', '/F', '/IM', 'Notepad.exe'], capture_output=True)
```

**关键点**：
- 进程名必须是 `Notepad.exe`（首字母大写）
- `/F` 参数强制终止
- `/IM` 参数按镜像名查找

---

#### 问题 4：演示内容重复输入
**问题描述**：
- "二层功能演示"被输入了两次
- 原因：执行了 `ctrl+a` 全选 + `ctrl+c` 复制，然后粘贴后又用 `type_text` 输入了一遍

**解决方案**：
✅ 删除多余的全选复制操作，直接输入内容
```python
# 修改前
auto.hotkey('ctrl', 'a')
auto.hotkey('ctrl', 'c')
auto.press_key('end')
auto.press_key('enter')
auto.type_text('\n二层功能演示：\n', use_clipboard=True)
auto.hotkey('ctrl', 'v')  # 这里重复粘贴了

# 修改后
auto.press_key('end')
auto.press_key('enter')
auto.type_text('\n二层功能演示：\n')
auto.copy_to_clipboard('3. 拖拽、双击、悬停等功能也都正常')
auto.hotkey('ctrl', 'v')
```

---

#### 问题 4：故障安全机制误触发
**问题描述**：
- 运行过程中触发 `pyautogui.FailSafeException`
- 原因：鼠标移动到屏幕左上角触发了故障安全

**解决方案**：
✅ 示例代码中临时禁用故障安全
```python
auto = DesktopAutomation(fail_safe=False, pause_duration=0.5)
```

**注意**：
- 开发测试阶段可以禁用故障安全
- 正式使用时建议保持开启（默认 `fail_safe=True`）
- 紧急停止方法：关闭终端窗口或按 `Ctrl+C`

---

### 设计哲学

1. **简单优先**：代码逻辑要简单清晰，避免过度设计
2. **剪贴板万能**：默认使用剪贴板方式，避开输入法问题
3. **场景专用**：密码输入等特殊场景使用专门函数
4. **可靠性**：关键操作（如关闭进程）使用系统级命令

---

### 依赖安装
```bash
pip install pyautogui pyperclip
```

### 使用示例
```python
from desktop_automation import DesktopAutomation

auto = DesktopAutomation(fail_safe=False, pause_duration=0.5)

# 文本输入（推荐）
auto.type_text('这是中文内容')
auto.type_text('English text')

# 密码输入
auto.type_password('your_password')

# 鼠标操作
auto.left_click(500, 300)
auto.double_click()
auto.drag_to(600, 400, start_x=500, start_y=300)

# 键盘操作
auto.hotkey('ctrl', 'c')
auto.press_key('enter')
```

---

**最后更新**: 2026-04-24

---

---

## 版本：v2.0 - 飞书 CUA 完全体

### 项目设计目标

构建完整的 AI 驱动桌面自动化系统：
1. 截图全屏 + 用户任务输入
2. 发送 prompt+截图 给 AI
3. AI 返回 JSON 指令，系统执行
4. 循环直到任务完成

---

### 新增模块

| 文件名 | 功能 |
|--------|------|
| `screenshot.py` | 全屏截图模块，自动保存带时间戳的图片 |
| `ai_communicator.py` | AI 通信模块，发送 prompt+截图，接收 JSON |
| `command_parser.py` | JSON 命令解析器，执行桌面操作 |
| `config.py` | 配置文件（API、系统提示词） |
| `feishu_cua.py` | 🚀 主程序，完整闭环 |
| `requirements.txt` | 依赖列表 |
| `PROJECT_OVERVIEW.md` | 完整项目说明 |

---

### 核心功能实现

#### 1. 截图模块 - screenshot.py
```python
capture_fullscreen(save_dir='screenshots', filename=None)
# 自动生成时间戳文件名
# 返回截图完整路径
```

#### 2. AI 通信模块 - ai_communicator.py
```python
send_to_ai(user_task, screenshot_path, conversation_history=None)
# 功能：base64编码截图，发送给支持视觉的AI模型
# 自动解析JSON响应，支持Markdown包裹的JSON
```

#### 3. 命令解析器 - command_parser.py
```python
parse_and_execute_command(auto, command)
# 支持的action：
# - left_click, right_click, double_click
# - drag, hover, select_area, scroll
# - type_text, press_key, hotkey
# - type_password
# - task_completed, continue
```

#### 4. 主程序闭环 - feishu_cua.py
```python
feishu_cua_system(user_task, max_iterations=10, fail_safe=True)
# 工作流：
# 1. 用户输入任务
# 2. 5秒准备时间
# 3. 循环执行：截图→发AI→执行→检查完成
# 4. 最多10次迭代，防止无限循环
```

---

### 系统提示词设计 - config.py

**SYSTEM_PROMPT** 包含：
1. AI 能力说明（告诉 AI 能做什么）
2. 所有操作的 JSON 格式示例
3. 坐标系统说明
4. 工作流程说明

---

### 新增依赖

- ✅ `requests` - HTTP 请求库，用于调用 AI API

---

### 项目结构

```
e:\cpulark\11\
├── 【v1.0 核心库】
│   └── desktop_automation.py    # 桌面自动化操作
│
├── 【v2.0 新增模块】
│   ├── screenshot.py            # 屏幕截图
│   ├── ai_communicator.py       # AI 通信
│   ├── command_parser.py        # JSON 命令解析
│   ├── feishu_cua.py          # 主程序（完整闭环）
│   └── config.py              # 配置文件
│
├── 【文档 & 配置】
│   ├── requirements.txt       # 依赖列表
│   ├── README.md            # 使用说明（原始）
│   ├── PROJECT_OVERVIEW.md  # 完整项目说明
│   └── CHANGELOG.md         # 本文档
```

---

### 使用方法

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 配置 API
   ```python
   # config.py
   AI_CONFIG = {
       'api_endpoint': '你的API地址',
       'api_key': '你的API密钥',
       'model': '支持视觉的模型',
   }
   ```

3. 运行主程序
   ```bash
   python feishu_cua.py
   ```

---

### 安全机制

- ✅ **故障安全**：鼠标移到屏幕左上角紧急停止
- ✅ **最大迭代次数**：默认 10 次，防止无限循环
- ✅ **操作间隔**：每个操作后暂停 0.5 秒

---

### AI 能力清单

#### 鼠标操作
```json
{"action":"left_click","x":500,"y":300}
{"action":"right_click","x":500,"y":300}
{"action":"double_click","x":500,"y":300}
{"action":"drag","start_x":100,"start_y":100,"end_x":300,"end_y":300}
{"action":"hover","x":500,"y":300}
{"action":"select_area","start_x":100,"start_y":100,"end_x":300,"end_y":300}
{"action":"scroll","clicks":10}
```

#### 键盘操作
```json
{"action":"type_text","text":"要输入的内容"}
{"action":"press_key","key":"enter"}
{"action":"hotkey","keys":["ctrl","v"]}
```

#### 密码输入
```json
{"action":"type_password","password":"xxx"}
```

#### 任务控制
```json
{"action":"task_completed","result":"成功！"}
{"action":"continue"}
```

---

### 本次更新总结

- ✅ 完整实现 CUA 系统闭环
- ✅ 模块化设计，清晰易用
- ✅ 包含完整的开发文档
- ✅ 保留 v1.0 所有功能

---

---

## 版本：v2.1 - 适配火山方舟（豆包 2.0 Pro）

### 更新内容
- ✅ 配置文件适配火山方舟 API
- ✅ 使用 endpoint_id 代替 model 参数
- ✅ temperature 调至 0.1，更稳定输出 JSON
- ✅ 填入真实 API Key 和接入点 ID

---

---

## 版本：v2.2 - 屏幕尺寸比例计算坐标

### 更新内容
- ✅ 在 SYSTEM_PROMPT 中加入屏幕尺寸说明
- ✅ 告诉 AI 使用比例计算坐标（比例×屏幕尺寸）
- ✅ 在 feishu_cua 中获取屏幕尺寸
- ✅ 在发送给 AI 的消息中加入【屏幕尺寸：宽x高】信息

---

---

## 版本：v2.3 - 修复火山方舟 API 不兼容问题

### 问题
- ❌ 火山方舟模型不支持 `response_format: {"type": "json_object"}` 参数
- ❌ 导致 400 Bad Request 错误

### 修复
- ✅ 删除 payload 中的 `response_format` 参数
- ✅ 保留 JSON 解析逻辑（从 AI 回复中提取 JSON）

---

---

## 版本：v2.4 - AI 描述和返回桌面提示

### 改进内容
- ✅ 在 SYSTEM_PROMPT 中加入 description 字段，让 AI 描述看到了什么、要做什么
- ✅ 在 SYSTEM_PROMPT 中加入 thought 字段，让 AI 写下思考过程
- ✅ 在 SYSTEM_PROMPT 中加入【特殊提示】：对于“打开软件”操作，优先尝试返回桌面（Win+D）
- ✅ 在 feishu_cua 中打印💭 AI思考 和 📝 AI描述
- ✅ 更新 command_parser，支持 task_completed 字段在顶层

---

---

## 版本：v2.5 - 打印鼠标坐标，方便调试定位

### 更新内容
- ✅ 在 command_parser.py 中加入鼠标操作坐标打印
- ✅ 打印格式：`📍 左键点击位置: (x, y)`
- ✅ 支持所有鼠标操作（left_click, right_click, double_click, drag, hover, select_area, scroll）

---

---

## 版本：v2.6 - 加入豆包坐标线性修正

### 更新内容
- ✅ 在 command_parser.py 中加入坐标修正系数 x_scale = 2.55, y_scale = 1.44
- ✅ 对所有鼠标操作坐标进行修正
- ✅ 打印时显示 `[修正: x*2.55, y*1.44]` 提示

---

**最后更新**: 2026-04-25
