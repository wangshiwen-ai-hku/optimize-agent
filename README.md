# Math Agent - 数学导师与优化求解器

一个基于 LangGraph 和 Gemini 的智能数学助手，支持两种核心模式：

## 🎯 核心功能

### 1. Tutor 模式 - 智能数学导师
- 基于提供的学习材料（文本、PDF、图片等）进行问答
- **智能检索**：支持关键词搜索和语义搜索
- **PDF 处理**：自动分块和索引，支持大型 PDF 文档
- **工具调用**：Agent 自动选择合适的检索工具查找信息
- **连续工作模式** ⭐：自动调用多个工具直到完整回答问题，无需用户中断
- **专业引用** ⭐：使用 "第 X 页" 而不是技术性标识，易于读者理解
- **对话记录** 🆕：自动保存问答历史为 Markdown 格式，支持 LaTeX 数学公式
- **图片生成** 🆕：可生成流程图、概念图等示意图辅助理解
- **材料缓存** 🆕：智能缓存机制，后续问题响应速度提升数百倍
- 支持交互式探索和深度学习
- 提供清晰的步骤解释和示例
- 引用材料中的相关内容

### 2. Solver 模式 - 自动优化求解器
- 自动识别优化问题类型（LP、IP、NLP 等）
- 生成数学模型和 Python 求解代码
- 自动执行代码并返回结果
- 支持代码错误自动修复（最多 3 次反思）

## 🚀 快速开始

> 💡 **新手？** 查看 [快速开始指南](QUICKSTART.md) 5 分钟上手！

### 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：
```bash
pip install langgraph langchain google-generativeai scipy cvxpy pulp python-dotenv pillow PyPDF2 numpy pydantic pyyaml
```

### 配置环境变量

创建 `.env` 文件：

```bash
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_PROVIDER=google_genai
```

### 测试安装

```bash
# 运行演示（推荐）
python demo.py

# 测试 PDF 工具（不需要 API key）
python test_pdf_tools.py

# 测试完整功能（需要 API key）
python test_agent.py
```

### 使用方式

#### 1. Tutor 模式 - 交互式学习

支持文本和 PDF 材料：

```bash
# 使用文本材料
python -m src.agent.main tutor examples/materials/linear_programming.txt

# 使用 PDF 材料
python -m src.agent.main tutor examples/materials/optimization_guide.pdf
```

Tutor 会自动：
1. 加载并分块处理材料
2. 根据问题选择合适的检索工具（关键词搜索或语义搜索）
3. 查找相关内容
4. 基于检索结果生成回答

然后可以提问：
- "什么是线性规划？"
- "单纯形法的基本思想是什么？"
- "如何用 Python 求解线性规划问题？"
- "第二章讲了什么内容？"（针对 PDF）

#### 2. Solver 模式 - 自动求解

```bash
python -m src.agent.main solver
```

然后输入优化问题，例如：
```
一个工厂生产两种产品 A 和 B。
产品 A 每件利润 40 元，需要 2 小时加工，3 小时装配
产品 B 每件利润 30 元，需要 1 小时加工，2 小时装配
每天有 100 小时加工时间，120 小时装配时间
求如何安排生产使利润最大？
```

#### 3. 编程方式使用

```python
import asyncio
from src.agent.main import run_tutor, run_solver

# Tutor 模式
async def tutor_example():
    answer = await run_tutor(
        question="什么是线性规划？",
        materials=["examples/materials/linear_programming.txt"]
    )
    print(answer)

# Solver 模式
async def solver_example():
    result = await run_solver(
        problem="最小化 (x-2)^2 + (y-3)^2，约束 x+y<=5, x>=0, y>=0"
    )
    print(result["solution"])
    print(result["code"])

asyncio.run(tutor_example())
asyncio.run(solver_example())
```

## 📁 项目结构

```
.
├── src/
│   ├── agent/
│   │   ├── config.yaml      # Agent 配置
│   │   ├── schema.py        # 状态定义
│   │   ├── graph.py         # LangGraph 工作流
│   │   └── main.py          # 主入口
│   ├── config/              # 配置管理
│   └── utils/               # 工具函数
├── examples/
│   ├── tutor_example.py     # Tutor 示例
│   ├── solver_example.py    # Solver 示例
│   └── materials/           # 学习材料
└── README.md
```

## 🔧 支持的优化问题类型

- **线性规划 (LP)**：目标函数和约束都是线性的
- **整数规划 (IP/MIP)**：部分或全部变量要求为整数
- **非线性规划 (NLP)**：目标函数或约束包含非线性项
- **凸优化**：目标函数为凸函数的优化问题
- **约束满足问题 (CSP)**：寻找满足所有约束的解

## 🛠️ 技术栈

- **LangGraph**：工作流编排
- **Gemini 2.5 Flash**：大语言模型
- **SciPy/CVXPY/PuLP**：优化求解库
- **Python 3.10+**

## 📝 示例

查看 `examples/` 目录获取更多示例：
- `tutor_example.py`：Tutor 模式使用示例
- `solver_example.py`：Solver 模式使用示例
- `test_pdf_tutor.py`：PDF 检索测试
- `create_sample_pdf.py`：创建示例 PDF
- `materials/`：示例学习材料

## 📚 文档

- [快速开始指南](QUICKSTART.md) - 5 分钟上手
- [Tutor 使用指南](docs/TUTOR_GUIDE.md) - 详细使用说明
- [PDF 检索设计](docs/PDF_RETRIEVAL.md) - 架构和实现细节
- [连续工作模式](docs/CONTINUOUS_MODE.md) - 自动化工作流程 ⭐
- [引用格式指南](docs/CITATION_GUIDE.md) - 专业引用规范 ⭐
- [对话记录功能](docs/CONVERSATION_LOGGING.md) - Markdown 格式记录和图片生成 🆕
- [材料缓存机制](docs/MATERIAL_CACHE.md) - 智能缓存提升性能 🆕

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT