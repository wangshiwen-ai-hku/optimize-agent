# 对话记录功能 - 快速参考

## 🚀 快速开始

### 启动 Tutor
```bash
./run_tutor.sh examples/materials/your_material.pdf
```

### 会话信息
```
Session ID: session_20231210_143022
Conversation will be saved to: conversations/session_20231210_143022/conversation.md
```

## 📝 提问技巧

### 普通问题
```
Your question: 什么是线性规划？
```

### 要求数学公式
```
Your question: 请用数学公式详细说明单纯形法的原理。
```

### 生成图表
```
Your question: 请生成一个流程图，展示梯度下降算法的步骤。
```

### 综合问题
```
Your question: 解释原始-对偶方法，包括数学公式和算法流程图。
```

## 🎨 图表类型

| 类型 | 关键词 | 示例 |
|------|--------|------|
| 流程图 | flowchart, 流程图 | "生成算法流程图" |
| 概念图 | concept_map, 概念图 | "生成知识点概念图" |
| 算法图 | algorithm, 算法示意图 | "展示算法执行过程" |
| 数学可视化 | mathematical_visualization | "可视化函数图像" |
| 对比图 | comparison, 对比 | "对比两种方法的差异" |

## 📐 数学公式语法

### 行内公式
```markdown
根据公式 $E = mc^2$，我们可以...
```

### 独立公式
```markdown
优化问题可以表示为：

$$
\min_{x \in \mathbb{R}^n} f(x) \quad \text{s.t.} \quad g(x) \leq 0
$$
```

### 常用符号

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 上标 | `x^2` | $x^2$ |
| 下标 | `x_i` | $x_i$ |
| 分数 | `\frac{a}{b}` | $\frac{a}{b}$ |
| 求和 | `\sum_{i=1}^n` | $\sum_{i=1}^n$ |
| 积分 | `\int_0^\infty` | $\int_0^\infty$ |
| 希腊字母 | `\alpha, \beta` | $\alpha, \beta$ |
| 向量 | `\vec{x}` | $\vec{x}$ |
| 矩阵 | `\mathbf{A}` | $\mathbf{A}$ |
| 范数 | `\|x\|` | $\|x\|$ |
| 偏导 | `\frac{\partial f}{\partial x}` | $\frac{\partial f}{\partial x}$ |

## 📂 会话文件

### 目录结构
```
conversations/
└── session_20231210_143022/
    ├── conversation.md      # Markdown 格式
    ├── conversation.json    # JSON 格式
    └── images/              # 生成的图片
        └── *.png
```

### 查看会话
```bash
# 查看 Markdown（推荐使用支持 LaTeX 的编辑器）
code conversations/session_20231210_143022/conversation.md

# 或使用 Typora、Obsidian 等
```

## 🔧 配置

### 环境变量（.env）
```bash
# 图片生成模型
IMAGE_GEN_MODEL=gemini-2.5-flash-image

# 可选模型：
# - gemini-2.5-flash-image (默认)
# - qwen-image-edit
# - doubao-seedream-4-0-250828
# - gpt-image

# 图片生成温度（0.0-1.0）
IMAGE_GEN_TEMPERATURE=0.7

# 最大重试次数
IMAGE_GEN_MAX_RETRIES=3
```

## 💡 使用技巧

### 1. 获取详细解释
```
Your question: 详细解释XXX，包括：
1. 基本概念
2. 数学公式
3. 算法步骤（用流程图展示）
4. 实际应用
```

### 2. 对比分析
```
Your question: 对比方法A和方法B，用表格和对比图说明它们的优缺点。
```

### 3. 可视化理解
```
Your question: 我不太理解XXX概念，能生成一个示意图帮助理解吗？
```

### 4. 引用材料
Tutor 会自动引用材料页码：
```
根据第 5 页的内容，原始-对偶方法...
```

## 🎯 最佳实践

### ✅ 推荐做法

1. **明确问题**：清楚地描述你想了解什么
2. **要求格式**：明确说明需要公式、图表等
3. **分步提问**：复杂问题可以分成多个小问题
4. **保存会话**：重要的学习内容记得保存会话目录

### ❌ 避免做法

1. **模糊问题**：避免过于宽泛的问题
2. **混合主题**：一次只问一个主题
3. **忽略引用**：注意 Tutor 提供的页码引用
4. **频繁中断**：让 Tutor 完成回答后再提问

## 🔍 查看会话摘要

### 退出时自动显示
```
Your question: exit

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

## 📱 Markdown 查看器推荐

### 桌面应用
- **Typora** - 所见即所得，完美支持 LaTeX
- **Obsidian** - 知识管理，支持 LaTeX
- **VS Code** + Markdown Preview Enhanced - 开发者友好

### 在线查看
- **GitHub** - 直接上传查看（支持 LaTeX）
- **HackMD** - 协作编辑
- **Notion** - 导入 Markdown

### 命令行
```bash
# 使用 glow（需要安装）
glow conversations/session_20231210_143022/conversation.md

# 使用 pandoc 转换为 HTML
pandoc conversation.md -o conversation.html --mathjax
```

## 🐛 常见问题

### Q: 数学公式不显示？
A: 确保使用支持 LaTeX 的 Markdown 查看器。

### Q: 图片生成失败？
A: 检查 API 密钥配置和网络连接。

### Q: 会话文件在哪里？
A: 默认在 `conversations/` 目录下。

### Q: 如何分享会话？
A: 直接分享整个会话目录，或将 Markdown 文件上传到 GitHub。

### Q: 可以恢复之前的会话吗？
A: 当前版本每次启动创建新会话，可以手动查看历史会话文件。

## 📚 更多资源

- [完整文档](CONVERSATION_LOGGING.md)
- [架构设计](CONVERSATION_ARCHITECTURE.md)
- [Tutor 使用指南](TUTOR_GUIDE.md)
- [快速开始](../QUICKSTART.md)

## 🆘 获取帮助

遇到问题？
1. 查看 [完整文档](CONVERSATION_LOGGING.md)
2. 查看 [常见问题](../README.md#常见问题)
3. 提交 Issue 到 GitHub

---

**提示**：这个功能会让你的学习过程更加系统化，所有的问答和图表都会被完整保存，方便日后复习！
