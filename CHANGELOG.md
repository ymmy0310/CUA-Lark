# CUA-Lark 飞书桌面自动化系统 更新日志

---

## 版本：v3.6 (2026-05-04)

### 更新目标
基于 v3.5 的实际运行反馈，修复按钮状态、优化文本阅读流程、完善操作指导，提升 AI 执行稳定性。

### 新增功能
1. **创建日程指导**
   - 新增飞书创建日程操作流程（仿照预约会议）
   - 步骤：点击创建日程按钮 → 粘贴主题 → 添加联系人 → 设定时间 → 添加备注

2. **群公告修改指导**
   - 新增飞书群公告修改流程
   - 步骤：进入群聊 → 点击群公告按钮 → 编辑内容 → 保存发布

3. **Shift+点击选中文本**
   - 新增 `shift_click` 原子操作，支持从起始位置 Shift+点击选中到结束位置
   - 用于复制部分文本内容，替代不稳定的拖拽选中

4. **复制粘贴操作流程**
   - 新增完整的复制粘贴指导：全选复制、部分选中复制、粘贴后的 enter 规则
   - 明确区分"修改文本不需要 enter"和"发送消息需要 enter"

5. **信息不足再次提问机制**
   - 替换原有的"常见模糊词映射表"
   - 改为通用原则：时间/人物/内容/位置不明确时，使用 request_input 追问
   - 提问原则：一次只问最关键的一两个问题

6. **自动读取剪贴板**
   - AI 执行 `ctrl+c` 复制后，系统自动读取剪贴板内容
   - 内容自动加入对话历史，AI 下一轮可直接看到文本资料
   - 简化文本阅读流程，无需再粘贴到输入栏

### 改进优化
1. **任务理解确认按钮状态修复**
   - 修复：AI 预先思考环节，"确认并执行"按钮被锁定无法点击
   - 修复："继续"按钮在理解确认阶段错误地处于可点击状态
   - 现在：理解确认阶段，暂停和继续按钮都锁定，仅发送按钮可点击

2. **重复行为检测逻辑修复**
   - 修复：不同热键（如 ctrl+v、ctrl+c）被误检测为重复操作
   - 现在：只检测有坐标的鼠标操作（left_click、right_click、double_click、click_paste、select_text）
   - 热键、窗口控制等合法重复操作不再触发检测

3. **暂停时发送建议按钮修复**
   - 修复：暂停/等待输入状态下，"发送建议"按钮被锁死无法使用
   - 现在：等待输入时发送建议按钮保持可点击状态

4. **迷你控制条日志栏增高**
   - 日志栏高度从 6 行增加到 9 行（1.5 倍增高）
   - 显示更多日志内容，减少滚动频率

5. **Prompt 增强**
   - 强化文本阅读要求：明确"文本阅读是必要前置步骤，绝非可选项"
   - 添加常见场景示例（写总结、分析记录、参考资料、修改文字）
   - 告知 AI CUA 界面不在任务栏，必须使用 show_cua_window 指令调出
   - 告知 AI 必须在最大化窗口下操作，否则坐标计算会出错
   - 指导 AI 点击飞书任务栏图标时瞄准下端蓝色部分
   - 指导 AI 使用 Ctrl+Alt+X 热键打开 QQ

6. **移除不稳定功能**
   - 删除 `select_text_drag` 拖拽选中文本（点击精度差，效果不稳定）
   - 删除"常见模糊词应对"固定映射表（过于僵化，改为通用提问原则）

### 代码更新
- `gui_app.py` - 修复理解确认阶段按钮状态，增高迷你控制条日志栏
- `feishu_cua.py` - 修复重复行为检测逻辑（只检测鼠标操作），添加剪贴板内容处理
- `command_parser.py` - 添加 shift_click 支持，删除 select_text_drag，复制后自动读取剪贴板
- `desktop_automation.py` - 新增 shift_click 和 select_text_drag 原子操作（后者已移除使用）
- `config.py` - 大量 prompt 更新：群公告、创建日程、复制粘贴、文本阅读、信息不足处理、窗口最大化等

---

## 版本：v3.5 (2026-05-03)

### 更新目标
修复暂停后继续变新任务的问题，解决窗口反复最小化干扰操作，新增迷你控制条替代主窗口监控。

### 新增功能
1. **迷你控制条（MiniControlBar）**
   - 位置：屏幕左下角，任务执行期间始终显示
   - 实时状态显示（📷 截图中 / 🤖 思考中 / ⚡ 执行中 / ✅ 完成）
   - 暂停/继续按钮（⏸ / ▶）
   - 日志展开/收起按钮（📋），点击向上展开显示详细日志
   - 按钮悬停提示功能
   - 支持鼠标拖拽调整位置
   - 宽度 380px，避免按钮拥挤
   - 移除边缘自动隐藏，保持始终可见便于点击

2. **窗口管理重构**
   - 任务执行期间：主窗口隐藏，仅显示迷你控制条
   - 暂停/request_input时：自动恢复主窗口，隐藏控制条
   - 任务完成后：自动恢复主窗口
   - 截图阶段：窗口保持隐藏，不干扰飞书焦点

### Bug修复
1. **暂停后继续变成新任务（Bug1）**
   - 问题：用户暂停后输入内容，系统把用户输入当成全新任务执行
   - 修复：保存原始任务到 `self.original_task`，循环中使用原始任务参数，用户输入只写入对话历史

2. **用户反馈重复显示（Bug2）**
   - 问题：暂停时用户输入被重复记录
   - 修复：区分"继续"和具体输入，避免重复记录

3. **AI request_input 未触发**
   - 问题：AI返回 `request_input` 指令后未暂停，继续执行
   - 修复：在 `execute_one_iteration` 中添加 `request_input` 返回值处理

4. **窗口反复最小化干扰操作**
   - 问题：窗口反复最小化/恢复会取消其他应用焦点
   - 修复：任务执行期间全程保持主窗口隐藏，通过控制条监控

5. **控制条交互问题**
   - 问题：边缘自动隐藏导致难点击、悬停闪烁、日志方向错误
   - 修复：取消边缘自动隐藏，移除悬停自动展开（改为点击展开），日志面板向上展开，添加按钮悬停提示

6. **文本输入问题（Bug3）**
   - 问题：click_paste 未修改剪贴板直接粘贴，导致粘贴的是旧内容
   - 修复：click_paste 改为先 copy_to_clipboard 写入剪贴板，再执行粘贴
   - 问题：click_paste_enter 的回车导致写文档时多出一堆换行
   - 修复：拆分为 click_paste + 独立的 enter 操作，提升灵活性
   - 问题：修改已有文本时直接粘贴会追加而非替换
   - 修复：引入 select_text 连招（点击+ctrl+a），先全选再粘贴
   - 问题：type_text 被误用于直接输入，不激活输入框导致失败
   - 修复：prompt 中明确 type_text 必须与 select_text 绑定使用，仅用于替换已有文本

7. **控制条宽度不足**
   - 问题：按钮拥挤难以点击
   - 修复：宽度从 280px → 330px → 380px 逐步增加

### 改进优化
1. **任务理解确认机制**
   - 每次任务开始前，AI 先分析任务需求、识别缺失信息、展示理解
   - 用户可确认直接执行，或补充信息后执行
   - 避免 AI 自行猜测导致操作偏差

2. **文本资料处理规则**
   - 新增规则指导 AI 如何处理用户提供的文本资料
   - 资料可见时：select_text + ctrl+c → show_cua_window → left_click 输入栏 → ctrl+v → request_input
   - 资料不可见时：先尝试 open_folder 打开文件夹，找不到再 request_input 询问路径

3. **窗口控制指令**
   - 新增 `show_cua_window` / `hide_cua_window` 指令
   - AI 可通过命令行调出 CUA 主窗口，解决迷你控制条无法输入的问题
   - 新增 window_controller.py 信号机制，gui_app.py 每 500ms 检查信号

### 代码重构
- **feishu_cua.py**：全程窗口最小化，多处暂停检查点，暂停时丢弃AI JSON，添加 request_input 处理，新增任务理解确认逻辑
- **gui_app.py**：新增 MiniControlBar 类，重构窗口管理逻辑，新增窗口控制信号监听
- **command_parser.py**：新增 show_cua_window / hide_cua_window 指令处理，新增 _send_window_command 函数
- **config.py**：补充 click_paste 需要先写入剪贴板的说明，新增窗口控制指令格式，新增文本资料处理规则
- **window_controller.py**：新增窗口控制信号文件

### 修改文件
- `gui_app.py` - 核心GUI重构，迷你控制条，窗口控制信号监听
- `feishu_cua.py` - 执行流程重构，任务理解确认
- `command_parser.py` - 密码输入添加坐标参数，新增窗口控制指令
- `desktop_automation.py` - 密码输入添加点击激活，click_paste 修改剪贴板
- `config.py` - 提示词更新，文本资料处理规则，窗口控制指令
- `window_controller.py` - 新增窗口控制信号机制

---

## 版本：v3.4

### 更新目标
添加友好的 API 配置界面，优化窗口体验，解决 API 限流问题。

### 新增功能
1. 🔧 API 配置窗口 - 图形化配置界面，支持输入 API 地址、API Key、接入点 ID
2. 📋 预设 API 地址 - 下拉菜单选择常用 API（火山引擎、自定义）
3. 🔐 配置安全 - 配置保存到单独的 config_api.json，避免提交到公开仓库
4. 👋 首次使用引导 - 程序启动时自动检查配置，首次使用弹出配置窗口
5. ⏸️ 指数退避重试 - 解决 429 限流问题，自动重试最多5次
6. 🛑 AI智能停止 - AI遇到卡住/失败时自动调用 request_input 请求用户帮助
7. 🛡️ 程序化安全网 - 连续3次相同操作自动强制 request_input，防止无限循环

### 改进优化
1. 📁 配置文件分离 - 新增 config_manager.py，专门管理 API 配置
2. 🚀 动态加载配置 - ai_communicator.py 优先从配置文件加载，回退到 config.py
3. 🎨 配置按钮 - GUI 中新增蓝色 API 配置按钮，随时打开配置
4. 🖥️ 窗口优化 - 主窗口不再置顶，宽度增加到1400，以展示所有按键
5. 🔒 配置窗口改进 - 保持在最上层；修复窗口实例被GC回收导致按钮失效；messagebox添加parent确保置顶
6. 🔒 网址输入锁定 - 选择火山引擎等预设选项时，自动锁定网址输入框
7. 🐛 终止逻辑修复 - 修复终止任务后再次发送被误终止的bug
8. 💬 对话历史修复 - 修复两次任务间对话历史被清空的问题
9. 📝 Prompt增强 - 丰富 request_input 使用场景，强化 win+D 备用策略，明确AI自行停止规则
10. 🎯 任务规划修复 - 修复GUI中任务规划功能被绕过的问题，现在正确调用 plan_task
11. 📷 截图优化 - 截图前用 iconify() 最小化窗口而非 withdraw() 隐藏，既不遮挡屏幕又不影响任务栏其他图标位置；执行命令阶段也最小化窗口防止AI误操作CUA界面
12. 🏗️ 架构重构 - 任务执行逻辑从gui_app.py迁移至feishu_cua.run_task()，GUI层仅保留UI桥接；规划改为预览模式，迭代上限250，移除分步策略
13. 🚫 Prompt防误操作 - 新增禁止AI点击/关闭CUA界面的指令
14. ⏱️ 时序优化 - 截图前最小化后等待0.5s、执行命令后恢复窗口前等待2.0s，确保窗口状态稳定
15. 💬 历史记录修复 - 修复用户回复request_input时未写入conversation_history的bug，解决AI重复发送相同求助的问题
16. ⌨️ 输入操作规则 - 新增prompt指令：click_paste自带激活功能严禁预点击；type_text/ctrl+a需先点击激活
17. 📋 飞书业务指引 - 新增预约会议详细操作流程（主题/联系人/时间/附件）和云文档新建方式指引
18. 🗑️ 删除任务规划功能 - 功能不稳定bug多，回归基本功确保CUA基础功能稳定
19. ⏸️ 暂停逻辑重构 - AI通信环节支持暂停（JSON不处理直接跳过），暂停后返回PAUSED标记进入request_input等待而非直接终止
20. 📢 暂停反馈优化 - 暂停时输出醒目分隔线+状态提示，让用户明确知道已暂停
21. ⌨️ click_paste_enter改名 - 改为click_paste，删除回车步骤，提升通用性

### 配置更新
- 新增 `config_api.json` - 用户个人 API 配置文件（独立存储）
- config.py 保持为模板文件，用于代码提交

### 新增文件
- `config_manager.py` - API 配置管理模块

### 更新文件
- `ai_communicator.py` - 支持动态加载配置，添加指数退避重试机制
- `gui_app.py` - 新增 API 配置窗口和按钮，启动时检查配置，优化窗口，修复终止/历史/规划/GC等bug
- `command_parser.py` - 回归简洁，移除快照对比功能
- `config.py` - 模板化，移除真实 API 信息，大幅增强 prompt 指令
- `CHANGELOG.md` - 添加 v3.4 更新说明
- `README.md` - 更新文档，说明新的配置方式

---

## 版本：v3.3

### 更新目标
优化GUI界面，支持AI请求用户补充信息，改进用户体验。

### 新增功能
1. 🪟 全新GUI设计 - 更大的窗口（1000x1100），居中显示
2. ⌨️ Shift+Enter换行 - 输入框支持多行输入，Shift+Enter换行
3. 🔝 当前步骤置顶 - 顶部深色信息栏显示当前执行步骤
4. ⚡ 当前操作显示 - 实时显示正在进行的操作（截图/思考/执行）
5. 📖 右侧说明书 - 右侧面板显示完整的使用说明
6. 🎨 终止按钮优化 - 使用#c0392b深红色，白色文字，对比度更高
7. 🙋 请求用户输入 - AI可以暂停任务，请求用户补充信息

### 改进优化
1. 📰 更大的字体 - 日志字体从10改为11，更易读
2. 📝 多行输入框 - 输入框从Entry改为ScrolledText，支持4行
3. ⏸️ 智能暂停 - 当AI返回request_input时，暂停执行等待用户
4. 🔄 任务动态修改 - 用户可以补充信息，动态修改任务继续执行
5. 🧹 清空日志按钮 - 新增按钮一键清空日志区域
6. 📊 状态实时更新 - 步骤和操作状态随时变化，一目了然

### 配置更新
- config.py 新增 request_input 操作说明
- config.py 更新有效操作列表

### 更新文件
- `gui_app.py` - 完全重写，全新界面设计
- `command_parser.py` - 添加 request_input 处理逻辑
- `feishu_cua.py` - 支持 request_input 暂停和返回
- `config.py` - 更新prompt，添加请求用户输入说明
- `CHANGELOG.md` - 添加v3.3更新说明
- `README.md` - 更新v3.3文档

---

## 版本：v3.2

### 更新目标
添加文本编辑功能，支持任务规划机制，解决长任务超出迭代次数的问题。

### 新增功能
1. ✅ 文本编辑功能 - 删除文本、删除选中、全选、删除全部、删除左右词
2. ✅ 任务规划机制 - AI先分析任务拆分成步骤，分步执行，避免超出迭代次数
3. ✅ 任务规划选项 - GUI中可选择是否启用任务规划
4. ✅ 智能界面隐藏 - 截图和操作阶段自动隐藏界面，避免干扰

### 改进优化
1. 📝 完善文本编辑 - 6个新的文本操作，支持修改已有文档
2. 🧩 智能任务拆分 - 长任务自动拆分成子步骤，每步独立执行
3. 📊 灵活迭代控制 - 总迭代次数 + 每步最大迭代次数双重保护
4. 🎯 步骤间等待 - 每步完成后短暂等待，更稳定
5. 🪟 智能界面控制 - 截图前和执行操作前自动隐藏界面，结束后显示

### 配置更新
- config.py 新增文本编辑操作说明
- config.py 新增 TASK_PLANNING_PROMPT 用于任务规划

### 更新文件
- `desktop_automation.py` - 新增 delete_text, delete_selected, select_all, delete_all, delete_word_left, delete_word_right
- `command_parser.py` - 新增文本编辑操作处理逻辑
- `feishu_cua.py` - 集成任务规划机制，支持分步执行，添加智能界面隐藏
- `ai_communicator.py` - 新增 plan_task() 函数
- `gui_app.py` - 添加任务规划选项，智能窗口控制
- `config.py` - 更新prompt，添加文本编辑和任务规划

---

## 版本：v3.1

### 更新目标
优化AI交互体验，提高操作效率，改进JSON稳定性。

### 新增功能
1. 🎯 点击粘贴回车连招 - `click_paste_enter` 操作，一步完成点击输入框、粘贴、回车
2. 🖱️ 改进的滚轮操作 - 支持先移动到指定位置再滚动，优化滚动策略
3. 🛡️ 更稳定的JSON解析 - 增强JSON格式规范提示，减少解析错误
4. ⏹️ 即时任务终止 - 在关键节点检测停止信号，点击终止按钮后快速响应

### 改进优化
1. 📋 连招优先级提升 - 将快捷连招放在操作列表首位，引导AI优先使用
2. 🎮 滚轮使用策略 - 首次滚动6格，错过后3格3格调整，提高效率
3. ✏️ 修复输入框干扰 - 优化窗口激活逻辑，避免打断用户输入
4. 📝 完善JSON格式规范 - 严格要求JSON格式，避免注释和语法错误
5. ⏱️ 调整初始化等待 - 从5秒改为3秒，截图后添加2秒缓冲
6. 🪟 无窗口启动选项 - 添加 pythonw.exe 启动方式和 bat 文件
7. 🛣️ 坐标归一化 - AI只需要返回0-1比例，系统自动计算最终坐标
8. ⚡ 终止响应优化 - 在截图、等待、AI通信等关键节点都检查停止信号，实现即时终止

### 配置更新
- config.py 中调整操作顺序，快捷连招优先
- 增强滚轮操作说明和使用策略
- 更新JSON格式规范，增加验证提示
- 补充飞书界面详细说明

### 新增文件
- `启动CUA-Lark.bat` - 带控制台窗口启动
- `启动CUA-Lark(无窗口).bat` - 无控制台窗口启动（推荐）
- `setup_shortcut.py` - 自动创建桌面快捷方式

### 更新文件
- `gui_app.py` - 优化窗口激活逻辑，避免干扰输入
- `command_parser.py` - 支持归一化坐标，添加连招处理
- `desktop_automation.py` - 新增 click_paste_enter 连招
- `feishu_cua.py` - 添加2秒缓冲，调整等待策略
- `config.py` - 更新prompt，调整操作优先级
- `README.md` - 更新v3.1说明

---

## 版本：v3.0

### 更新目标
打造飞书专属AI桌面助手，支持图形界面、连续对话。

### 新增功能
1. 🎨 图形界面 - gui_app.py，窗口固定在右上角
2. 💬 连续对话 - 支持多轮对话，AI记住对话历史
3. 📂 路径打开 - open_folder操作，通过路径直接打开文件夹
4. 💭 纯聊天模式 - 只聊天不操作电脑，任务自动结束
5. 📘 飞书专属优化 - 完整飞书界面说明
6. ⏹️ 任务终止功能 - 可随时停止当前执行的任务

### 核心功能
- 🤖 AI智能控制 - 基于豆包2.0 Pro（火山方舟）
- 🖱️ 完整鼠标操作 - 点击、拖拽、滚轮等
- ⌨️ 全功能键盘 - 文本输入、热键、密码输入
- 🔄 闭环执行 - 截图→分析→操作→再截图检查
- 🛡️ 安全机制 - 故障安全、最大迭代次数限制

---

## 版本：v2.6 (2026-04-24)

### 更新目标
解决 AI 返回坐标与实际点击位置偏差的问题。

### 新增功能
1. 📐 豆包坐标线性修正 - 在 command_parser.py 中加入坐标修正系数
   - x_scale = 2.55
   - y_scale = 1.44
2. 🎯 全鼠标操作修正 - 对所有鼠标操作坐标进行修正
3. 🖨️ 修正提示 - 打印时显示 `[修正: x*2.55, y*1.44]` 提示

### 更新文件
- `command_parser.py` - 加入坐标修正逻辑

---

## 版本：v2.5 (2026-04-24)

### 更新目标
添加鼠标坐标打印，方便调试定位。

### 新增功能
1. 📍 鼠标坐标打印 - command_parser.py 中加入鼠标操作坐标打印
2. 🖨️ 统一打印格式 - `📍 左键点击位置: (x, y)`
3. 🎯 全操作覆盖 - 支持所有鼠标操作（left_click, right_click, double_click, drag, hover, select_area, scroll）

### 更新文件
- `command_parser.py` - 添加坐标打印

---

## 版本：v2.4 (2026-04-24)

### 更新目标
增强 AI 交互体验，添加思考过程描述和返回桌面策略。

### 改进优化
1. 💭 AI 思考显示 - SYSTEM_PROMPT 中加入 thought 字段，让 AI 写下思考过程
2. 📝 AI 描述显示 - SYSTEM_PROMPT 中加入 description 字段，让 AI 描述看到了什么、要做什么
3. 🏠 返回桌面策略 - SYSTEM_PROMPT 中加入【特殊提示】：对于"打开软件"操作，优先尝试返回桌面（Win+D）
4. 🖨️ 思考输出 - feishu_cua.py 中打印 💭 AI思考 和 📝 AI描述
5. ✅ 顶层完成标记 - command_parser 支持 task_completed 字段在顶层

### 更新文件
- `config.py` - SYSTEM_PROMPT 增强
- `feishu_cua.py` - 打印 AI 思考和描述
- `command_parser.py` - 支持顶层 task_completed

---

## 版本：v2.3 (2026-04-24)

### 修复问题
火山方舟 API 不兼容 `response_format: {"type": "json_object"}` 参数
- 删除 payload 中的 `response_format` 参数
- 保留 JSON 解析逻辑（从 AI 回复中提取 JSON）

### 更新文件
- `ai_communicator.py` - 移除 response_format 参数

---

## 版本：v2.2 (2026-04-24)

### 更新目标
让 AI 使用屏幕尺寸比例计算坐标，提高跨分辨率兼容性。

### 新增功能
1. 📐 屏幕尺寸比例 - SYSTEM_PROMPT 中加入屏幕尺寸说明
2. 🧮 比例计算坐标 - 告诉 AI 使用比例计算坐标（比例×屏幕尺寸）
3. 🖥️ 尺寸信息传递 - feishu_cua.py 中获取屏幕尺寸，在发送给 AI 的消息中加入【屏幕尺寸：宽x高】信息

### 更新文件
- `config.py` - SYSTEM_PROMPT 添加屏幕尺寸说明
- `feishu_cua.py` - 获取并传递屏幕尺寸

---

## 版本：v2.1 (2026-04-24)

### 更新目标
配置文件适配火山方舟（豆包 2.0 Pro）。

### 配置更新
1. 🔑 使用 endpoint_id 代替 model 参数
2. 🌡️ temperature 调至 0.1，更稳定输出 JSON
3. 🔐 填入真实 API Key 和接入点 ID

### 更新文件
- `config.py` - 适配火山方舟 API 配置

---

## 版本：v2.0 (2026-04-23) - 飞书 CUA 完全体

### 项目设计目标
构建完整的 AI 驱动桌面自动化系统：
1. 截图全屏 + 用户任务输入
2. 发送 prompt+截图 给 AI
3. AI 返回 JSON 指令，系统执行
4. 循环直到任务完成

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

### 系统提示词设计 - config.py
**SYSTEM_PROMPT** 包含：
1. AI 能力说明（告诉 AI 能做什么）
2. 所有操作的 JSON 格式示例
3. 坐标系统说明
4. 工作流程说明

### 新增依赖
- ✅ `requests` - HTTP 请求库，用于调用 AI API

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

### 安全机制
- ✅ **故障安全**：鼠标移到屏幕左上角紧急停止
- ✅ **最大迭代次数**：默认 10 次，防止无限循环
- ✅ **操作间隔**：每个操作后暂停 0.5 秒

---

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

**最后更新**: 2026-05-03
