# 飞书 CUA 系统 - 完全体项目概览

## 📁 项目结构

```
e:\cpulark\11\
├── desktop_automation.py   # 桌面自动化操作核心库
├── screenshot.py           # 屏幕截图模块
├── ai_communicator.py      # AI 通信模块
├── command_parser.py       # JSON 命令解析器
├── feishu_cua.py          # 主程序入口（完整闭环）
├── config.py              # 配置文件（API、提示词）
├── requirements.txt       # 依赖列表
├── PROJECT_OVERVIEW.md    # 本文件 - 项目说明
└── CHANGELOG.md          # 开发日志
```

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

## 📦 各模块说明

### 1. config.py - 配置文件
```python
AI_CONFIG = {
    'api_endpoint': 'API地址',
    'api_key': '你的API密钥',
    'model': '模型名称',
    ...
}
```

**SYSTEM_PROMPT**: 告诉AI我们有哪些能力，以及如何返回JSON指令

### 2. screenshot.py - 截图模块
```python
from screenshot import capture_fullscreen
path = capture_fullscreen()  # 返回截图路径
```

### 3. ai_communicator.py - AI通信模块
```python
from ai_communicator import send_to_ai
command = send_to_ai("用户任务", "screenshot.png")
```

### 4. command_parser.py - 命令解析器
```python
from command_parser import parse_and_execute_command
result = parse_and_execute_command(auto, command)
```

### 5. desktop_automation.py - 桌面操作库
已开发完成，提供所有鼠标键盘操作

### 6. feishu_cua.py - 主程序（核心闭环）
整合所有模块，一键启动完整流程

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 API
编辑 `config.py`，填写你的 AI API 信息：
```python
AI_CONFIG = {
    'api_endpoint': 'https://api.openai.com/v1/chat/completions',  # 或其他兼容API
    'api_key': 'sk-xxxxxxxxxx',  # 替换为你的密钥
    'model': 'gpt-4-vision-preview',  # 支持视觉的模型
}
```

### 3. 运行主程序
```bash
python feishu_cua.py
```

### 4. 输入任务
在控制台输入你的任务，比如：
```
请帮我打开记事本，输入"Hello World"，然后保存文件
```

### 5. 准备好环境
程序会等待5秒，让你准备好工作环境

---

## 📋 AI 能操作的功能

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

## 🛡️ 安全机制

### 故障安全
- 默认启用 `fail_safe=True`
- 鼠标移动到屏幕左上角会紧急停止
- 如果程序失控，立即把鼠标移到左上角！

### 最大迭代次数
- 默认最多执行 10 次操作
- 防止无限循环

---

## 💡 使用技巧

### 任务描述建议
- 清晰描述目标
- 分步骤说明
- 告诉AI你当前的屏幕状态

### 示例任务
```
请帮我：
1. 打开记事本
2. 输入"测试内容"
3. 保存到桌面
```

---

## 🔧 调试技巧

### 1. 测试单个模块
```bash
# 测试截图
python screenshot.py

# 测试桌面操作
python desktop_automation.py
```

### 2. 修改提示词
编辑 `config.py` 中的 `SYSTEM_PROMPT`，可以调整AI的行为

---

## 📌 注意事项

1. **输入法问题**：已统一使用剪贴板输入，无影响
2. **API配置**：确保使用支持视觉的模型
3. **网络连接**：需要能访问AI API
4. **屏幕分辨率**：AI会根据截图估算坐标

---

## 🎉 未来扩展

- [ ] 飞书机器人集成（接收飞书消息）
- [ ] OCR 文字识别增强
- [ ] 多屏支持
- [ ] 任务历史记录
- [ ] 预设任务模板

---

## 📞 常见问题

**Q: 如何知道坐标是多少？**
A: 可以先用 `displayMousePosition()` 查看，或者让AI根据截图估算。

**Q: AI一直犯错怎么办？**
A: 可以更详细地描述任务，或者调整提示词。

**Q: 程序跑起来之后怎么停止？**
A: 鼠标快速移到屏幕左上角即可。

---

**版本**: v1.0 | **最后更新**: 2026-04-25
