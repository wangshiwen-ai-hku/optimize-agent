# 对话记录功能 - 5 分钟快速开始

## 🚀 立即开始

### 1. 启动 Tutor（自动开启对话记录）

```bash
./run_tutor.sh examples/materials/linear_programming.txt
```

你会看到：
```
Session ID: session_20231210_143022
Conversation will be saved to: conversations/session_20231210_143022/conversation.md
```

### 2. 提问（自动记录）

```
Your question: 什么是线性规划？请用数学公式详细说明。
```

Tutor 会返回包含 LaTeX 公式的 Markdown 格式回答！

### 3. 生成图表（自动保存）

```
Your question: 请生成一个流程图，展示单纯形法的迭代步骤。
```

图表会自动生成并保存到会话目录！

### 4. 退出查看摘要

```
Your question: exit
```

会显示：
```
Total Q&A exchanges: 2
Total images generated: 1
Conversation saved to: conversations/session_20231210_143022/conversation.md
```

## 📂 查看保存的对话

### 使用 VS Code
```bash
code conversations/session_20231210_143022/conversation.md
```

### 使用 Typora（推荐）
```bash
open -a Typora conversations/session_20231210_143022/conversation.md
```

### 使用浏览器
将 Markdown 文件上传到 GitHub 或 HackMD 查看。

## 💡 提问技巧

### 获取数学公式
```
请用数学公式详细说明...
```

### 生成图表
```
请生成一个[流程图/概念图/示意图]，展示...
```

### 综合问题
```
解释XXX概念，包括：
1. 数学定义和公式
2. 算法流程图
3. 实际应用示例
```

## 🎨 Markdown 中的数学公式

生成的对话文件中，数学公式使用 LaTeX 语法：

**行内公式**：
```markdown
根据公式 $E = mc^2$，我们可以...
```

**独立公式**：
```markdown
优化问题可以表示为：

$$
\min_{x \in \mathbb{R}^n} f(x) \quad \text{s.t.} \quad g(x) \leq 0
$$
```

## 📊 会话文件结构

```
conversations/
└── session_20231210_143022/
    ├── conversation.md      # 👈 主要查看这个文件
    ├── conversation.json    # JSON 格式备份
    └── images/              # 生成的图片
        └── *.png
```

## ⚙️ 配置（可选）

在 `.env` 文件中：

```bash
# 使用不同的图片生成模型
IMAGE_GEN_MODEL=gemini-2.5-flash-image

# 调整生成温度（0.0-1.0）
IMAGE_GEN_TEMPERATURE=0.7
```

## 🎯 常见使用场景

### 场景 1：学习新概念
```
Your question: 详细解释原始-对偶方法，包括数学公式和算法流程图。
```

### 场景 2：理解算法
```
Your question: 单纯形法是如何工作的？请生成一个示意图帮助理解。
```

### 场景 3：对比分析
```
Your question: 对比内点法和单纯形法的优缺点，用表格和图表说明。
```

## 📚 更多资源

- **完整文档**: [docs/CONVERSATION_LOGGING.md](docs/CONVERSATION_LOGGING.md)
- **快速参考**: [docs/CONVERSATION_QUICK_REFERENCE.md](docs/CONVERSATION_QUICK_REFERENCE.md)
- **架构设计**: [docs/CONVERSATION_ARCHITECTURE.md](docs/CONVERSATION_ARCHITECTURE.md)

## 💬 示例对话

查看完整示例：
```bash
python examples/test_conversation_logging.py
```

## ❓ 常见问题

**Q: 数学公式不显示？**  
A: 使用支持 LaTeX 的 Markdown 查看器（VS Code、Typora、GitHub）

**Q: 图片生成失败？**  
A: 检查 `.env` 文件中的 API 密钥配置

**Q: 会话文件在哪里？**  
A: 在 `conversations/` 目录下，按会话 ID 组织

**Q: 可以分享会话吗？**  
A: 可以！直接分享整个会话目录，或将 Markdown 上传到 GitHub

---

**就这么简单！** 现在你的所有学习对话都会被完整记录，包括数学公式和图表！🎉
