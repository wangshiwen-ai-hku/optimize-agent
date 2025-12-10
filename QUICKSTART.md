# 快速开始指南

## 5 分钟上手

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件：

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_PROVIDER=google_genai
```

### 3. 测试基础功能

```bash
# 测试 PDF 工具（不需要 API key）
python test_pdf_tools.py
```

### 4. 运行 Tutor 模式

```bash
# 使用文本材料
python -m src.agent.main tutor examples/materials/linear_programming.txt
```

然后输入问题：
```
Your question: 什么是线性规划？
```

### 5. 运行 Solver 模式

```bash
python -m src.agent.main solver
```

然后输入优化问题：
```
> 最大化 z = 3x + 2y，约束条件：x + y <= 4, x >= 0, y >= 0
```

## 示例代码

### Tutor 示例

```python
import asyncio
from src.agent.main import run_tutor

async def main():
    answer = await run_tutor(
        question="什么是线性规划？",
        materials=["examples/materials/linear_programming.txt"]
    )
    print(answer)

asyncio.run(main())
```

### Solver 示例

```python
import asyncio
from src.agent.main import run_solver

async def main():
    result = await run_solver(
        problem="最大化 z = 3x + 2y，约束：x + y <= 4, x >= 0, y >= 0"
    )
    print(result["solution"])

asyncio.run(main())
```

## 使用 PDF 材料

### 创建示例 PDF

```bash
python examples/create_sample_pdf.py
```

### 使用 PDF

```bash
python -m src.agent.main tutor examples/materials/optimization_guide.pdf
```

## 运行示例

```bash
# Tutor 示例
python examples/tutor_example.py

# Solver 示例
python examples/solver_example.py

# PDF Tutor 测试
python examples/test_pdf_tutor.py
```

## 常见问题

### Q: 如何获取 Gemini API Key？

访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 创建 API key。

### Q: 支持哪些文件格式？

- 文本：`.txt`, `.md`
- PDF：`.pdf`（需要包含可提取的文本）

### Q: 如何处理大型 PDF？

系统会自动分块处理。建议 PDF < 50MB。

### Q: 检索速度慢怎么办？

1. 减少材料数量
2. 使用更小的文件
3. 调整 `top_k` 参数

### Q: 如何调试？

查看日志输出，系统会显示：
- 🟣 Agent 操作
- 🟢 工具调用
- 🔵 状态变化
- 🔴 错误信息

## 下一步

- 📖 阅读 [Tutor 使用指南](docs/TUTOR_GUIDE.md)
- 🏗️ 查看 [PDF 检索设计文档](docs/PDF_RETRIEVAL.md)
- 📚 浏览 [完整 README](README.md)

## 获取帮助

- 查看示例代码：`examples/`
- 阅读文档：`docs/`
- 检查配置：`src/agent/config.yaml`
