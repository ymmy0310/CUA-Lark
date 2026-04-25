# 飞书 CUA 系统 - AI 桌面自动化

让 AI 替你操作电脑！通过自然语言描述任务，系统会自动截图、分析并执行桌面操作。

---

## 🌟 功能特性

- 🤖 **AI 智能控制** - 基于豆包 2.0 Pro（火山方舟），通过视觉理解屏幕内容
- 🖱️ **完整鼠标操作** - 点击、双击、拖拽、悬停、框选、滚轮
- ⌨️ **全功能键盘** - 文本输入（支持中文）、按键、热键、密码输入
- 🔄 **闭环执行** - 截图 → AI 决策 → 执行操作 → 再截图检查，循环直至任务完成
- 🛡️ **安全机制** - 故障安全、最大迭代次数限制
- 📷 **自动截图** - 每次迭代自动保存屏幕截图

---

## 📁 项目结构

```
e:\cualark\11\
├── desktop_automation.py   # 桌面自动化操作核心库
├── screenshot.py           # 屏幕截图模块
├── ai_communicator.py      # AI 通信模块（火山方舟）
├── command_parser.py       # JSON 命令解析器
├── feishu_cua.py          # 主程序入口（完整闭环）
├── config.py              # 配置文件（API、提示词）
├── requirements.txt       # 依赖列表
├── README.md              # 本文档
├── PROJECT_OVERVIEW.md    # 项目概览
├── CHANGELOG.md          # 开发日志
└── screenshots/          # 截图保存目录（自动创建）
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API

编辑 `config.py`，填写你的火山方舟 API 信息：

```python
AI_CONFIG = {
    'api_endpoint': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    'api_key': 'ark-你的API密钥',      # 替换为你的密钥
    'endpoint_id': 'ep-你的接入点ID',   # 替换为你的接入点ID
    'temperature': 0.1,
    'max_tokens': 2000,
}
```

⚠️ **安全提示**：请妥善保管 `config.py` 中的 API Key，不要提交到公开仓库！

### 3. 运行主程序

```bash
python feishu_cua.py
```

### 4. 输入任务

在控制台输入你的任务描述，例如：

```
请帮我打开记事本，输入"飞书 CUA 测试"，然后保存到桌面
```

### 5. 准备环境

程序会等待 5 秒，让你准备好工作环境。

---

## 🎯 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户任务输入                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 【第1步】截图 - capture_fullscreen()                        │
│  功能：全屏截图并保存到 screenshots/ 目录                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 【第2步】发AI - send_to_ai()                                │
│  功能：发送prompt+截图给AI，等待返回JSON指令                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 【第3步】解析执行 - parse_and_execute_command()            │
│  功能：解读JSON，调用desktop_automation执行桌面操作        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  任务完成？                                                   │
│     ├── 是 → 完成，返回结果                                  │
│     └── 否 → 回到第1步，继续循环                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 AI 支持的操作

AI 可以通过以下 JSON 指令控制你的电脑：

### 鼠标操作

```json
{"action":"left_click","x":500,"y":300}           // 左键点击
{"action":"right_click","x":500,"y":300}          // 右键点击
{"action":"double_click","x":500,"y":300}         // 双击
{"action":"drag","start_x":100,"start_y":100,"end_x":300,"end_y":300}  // 拖拽
{"action":"hover","x":500,"y":300}               // 悬停
{"action":"select_area","start_x":100,"start_y":100,"end_x":300,"end_y":300}  // 框选
{"action":"scroll","clicks":10}                   // 滚轮
```

### 键盘操作

```json
{"action":"type_text","text":"要输入的内容"}       // 输入文本
{"action":"press_key","key":"enter"}              // 按键
{"action":"hotkey","keys":["ctrl","v"]}           // 热键
```

### 密码输入

```json
{"action":"type_password","password":"xxx"}       // 密码输入
```

### 任务控制

```json
{"action":"task_completed","result":"成功！"}     // 任务完成
{"action":"continue"}                             // 继续执行
```

---

## 💡 使用技巧

### 任务描述建议

- 清晰描述目标
- 分步骤说明
- 告诉 AI 你当前的屏幕状态
- 对于"打开软件"，可明确说明优先返回桌面（`Win+D`）

### 示例任务

```
请帮我：
1. 打开记事本
2. 输入"测试内容"
3. 保存到桌面
```

---

## 🔧 各模块说明

### config.py - 配置文件

包含 AI API 配置和系统提示词。

- `AI_CONFIG`：火山方舟 API 配置
- `SYSTEM_PROMPT`：告诉 AI 我们有哪些能力，以及如何返回 JSON 指令

### screenshot.py - 截图模块

```python
from screenshot import capture_fullscreen
path = capture_fullscreen()  # 返回截图路径
```

### ai_communicator.py - AI 通信模块

```python
from ai_communicator import send_to_ai
command = send_to_ai("用户任务", "screenshot.png", screen_w, screen_h)
```

### command_parser.py - 命令解析器

解析 AI 返回的 JSON 并执行相应操作。

⚠️ 注意：坐标修正系数（`x_scale=2.55`, `y_scale=1.44`）硬编码在此文件中，可根据实际屏幕调整。

### desktop_automation.py - 桌面操作库

核心自动化操作类，提供所有鼠标键盘操作。

### feishu_cua.py - 主程序

整合所有模块，一键启动完整流程。

---

## 🛡️ 安全机制

### 故障安全

- 默认启用 `fail_safe=True`
- 鼠标移动到屏幕左上角会紧急停止
- 如果程序失控，立即把鼠标移到左上角！

### 最大迭代次数

- 默认最多执行 10 次操作
- 防止无限循环

---

## 📌 注意事项

1. **输入法问题**：已统一使用剪贴板输入，无影响
2. **API 配置**：确保使用支持视觉的模型（豆包 2.0 Pro）
3. **网络连接**：需要能访问火山方舟 API
4. **屏幕分辨率**：AI 会根据截图估算坐标
5. **坐标修正**：如果点击位置不准确，可调整 `command_parser.py` 中的 `x_scale` 和 `y_scale`

---

## 🔍 调试技巧

### 1. 测试单个模块

```bash
# 测试截图
python screenshot.py

# 测试桌面操作
python desktop_automation.py
```

### 2. 修改提示词

编辑 `config.py` 中的 `SYSTEM_PROMPT`，可以调整 AI 的行为

---

## ❓ 常见问题

**Q: 如何知道坐标是多少？**
A: 可以先用 `pyautogui.displayMousePosition()` 查看，或者让 AI 根据截图估算。

**Q: AI 一直犯错怎么办？**
A: 可以更详细地描述任务，或者调整提示词。

**Q: 程序跑起来之后怎么停止？**
A: 鼠标快速移到屏幕左上角即可。

**Q: 点击位置不准确怎么办？**
A: 调整 `command_parser.py` 中的 `x_scale` 和 `y_scale` 系数。

---

## 🎉 未来扩展

- [ ] 飞书机器人集成（接收飞书消息）
- [ ] OCR 文字识别增强
- [ ] 多屏支持
- [ ] 任务历史记录
- [ ] 预设任务模板
- [ ] 配置化坐标修正系数

---

**版本**: v2.0 | **最后更新**: 2026-04-25
