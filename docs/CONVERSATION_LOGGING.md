# 对话记录功能

## 概述

Tutor 模式现在支持自动记录对话历史，包括：
- 学生的问题
- Tutor 的回答（Markdown 格式，支持 LaTeX 数学公式）
- 生成的图片和示意图
- 完整的会话元数据

## 功能特性

### 1. 自动对话记录

每次启动 Tutor 模式时，系统会自动创建一个新的会话，并记录所有问答内容。

### 2. Markdown 格式输出

Tutor 的回答使用标准 Markdown 格式，包括：
- 标题和章节结构
- 列表和强调
- 数学公式（LaTeX 语法）
  - 行内公式：`$x^2 + y^2 = r^2$`
  - 独立公式：`$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$`

### 3. 图片生成和保存

Tutor 可以使用 `generate_diagram` 工具生成：
- 流程图
- 概念图
- 算法示意图
- 数学可视化
- 对比图

生成的图片会自动保存到会话目录，并在 Markdown 中引用。

### 4. 会话管理

每个会话包含：
- `conversation.md` - Markdown 格式的对话记录
- `conversation.json` - JSON 格式的结构化数据
- `images/` - 生成的图片目录

## 使用方法

### 基本使用

```bash
./run_tutor.sh examples/materials/linear_programming.txt
```

启动后，系统会显示：
```
Math Tutor - Interactive Mode
============================================================
Loaded 1 material(s)
Session ID: session_20231210_143022
Conversation will be saved to: conversations/session_20231210_143022/conversation.md
Type 'exit' to quit
```

### 提问示例

```
Your question: 什么是原始-对偶方法？请用数学公式说明。

🤔 Thinking...

📚 Tutor: ## 原始-对偶方法

根据第 3 页的内容，原始-对偶（primal-dual）方法是一种优化算法...

[详细回答，包含 LaTeX 公式]
```

### 生成图表

```
Your question: 请生成一个流程图，展示原始-对偶方法的迭代过程。

🤔 Thinking...

📚 Tutor: 我已经生成了一个流程图来展示原始-对偶方法的迭代过程...

[图片会自动保存并在 Markdown 中引用]
```

### 退出会话

输入 `exit`、`quit` 或 `q` 退出，系统会显示会话摘要：

```
============================================================
Session Summary
============================================================
Total Q&A exchanges: 5
Total images generated: 2
Conversation saved to: conversations/session_20231210_143022/conversation.md
Session directory: conversations/session_20231210_143022
JSON export: conversations/session_20231210_143022/conversation.json

Goodbye!
```

## 会话目录结构

```
conversations/
└── session_20231210_143022/
    ├── conversation.md      # Markdown 格式的对话记录
    ├── conversation.json    # JSON 格式的结构化数据
    └── images/              # 生成的图片
        ├── 20231210_143022_000000_flowchart.png
        └── 20231210_143022_000001_concept_map.png
```

## Markdown 示例

生成的 `conversation.md` 文件格式：

```markdown
# Math Tutor Conversation

**Session ID:** session_20231210_143022  
**Start Time:** 2023-12-10 14:30:22

---

## 🎓 Student Question

什么是原始-对偶方法？请用数学公式说明。

*Time: 14:30:25*

## 📚 Tutor Answer

## 原始-对偶方法

根据第 3 页的内容，原始-对偶（primal-dual）问题表述可以通过 Fenchel 对偶性引入辅助变量 $p$ 来得到。

对于一个形如 (1.5) 的问题，其原始-对偶表述为：

$$
\min_{u\in L^2(\Omega)} \max_{p\in L^2(Q)} \{g(u) + (p, Su)_{L^2(Q)} - f^*(p)\}
$$

其中：
- $(·,·)_{L^2(Q)}$ 表示 $L^2$ 内积
- $f^*(p) := \sup_{y\in L^2(Q)}\{(y, p)_{L^2(Q)} - f(y)\}$ 是 $f(y)$ 的凸共轭

...

*Time: 14:30:35*

---
```

## 配置选项

### 环境变量

在 `.env` 文件中配置：

```bash
# 图片生成模型
IMAGE_GEN_MODEL=gemini-2.5-flash-image

# 图片生成温度
IMAGE_GEN_TEMPERATURE=0.7

# 最大重试次数
IMAGE_GEN_MAX_RETRIES=3
```

### 支持的图片生成模型

- `gemini-2.5-flash-image` (默认)
- `qwen-image-edit`
- `doubao-seedream-4-0-250828`
- `gpt-image` (Azure OpenAI)

## API 使用

### Python API

```python
from src.agent.main import run_tutor
from src.utils.conversation_logger import get_conversation_logger, reset_conversation_logger

# 创建新会话
reset_conversation_logger()
logger = get_conversation_logger()

# 运行 Tutor
materials = ["examples/materials/linear_programming.txt"]
answer = await run_tutor("什么是线性规划？", materials)

# 获取会话摘要
summary = logger.get_session_summary()
print(f"Conversation saved to: {summary['markdown_file']}")
```

### 自定义会话 ID

```python
from src.utils.conversation_logger import ConversationLogger

# 使用自定义会话 ID
logger = ConversationLogger(session_id="my_custom_session")

# 手动记录
logger.log_question("我的问题")
logger.log_answer("回答内容", images=["path/to/image.png"])
```

## 注意事项

1. **数学公式渲染**：生成的 Markdown 文件使用标准 LaTeX 语法，需要支持 LaTeX 的 Markdown 查看器才能正确显示公式。

2. **图片路径**：Markdown 中的图片使用相对路径引用，确保在同一目录下查看。

3. **会话持久化**：所有会话数据保存在 `conversations/` 目录，不会自动清理，请定期管理。

4. **并发会话**：每次启动 Tutor 会创建新会话，多个实例可以同时运行而不会冲突。

## 故障排除

### 图片生成失败

如果图片生成失败，检查：
1. API 密钥是否正确配置（`.env` 文件）
2. 网络连接是否正常
3. 模型是否可用

系统会在工具调用结果中显示错误信息。

### Markdown 公式不显示

确保使用支持 LaTeX 的 Markdown 查看器，如：
- VS Code + Markdown Preview Enhanced
- Typora
- GitHub（在线查看）
- Obsidian

## 示例脚本

运行测试脚本：

```bash
python examples/test_conversation_logging.py
```

这会创建一个测试会话，演示对话记录和图片生成功能。
