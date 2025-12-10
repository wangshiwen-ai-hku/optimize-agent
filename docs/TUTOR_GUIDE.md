# Tutor 模式使用指南

## 概述

Tutor 模式是一个智能数学导师，能够基于提供的学习材料回答问题。它支持：

- 📄 文本文件（.txt, .md）
- 📕 PDF 文档
- 🔍 智能检索（关键词 + 语义搜索）
- 🤖 自动工具调用

## 工作原理

### 1. 材料加载

当你提供材料时，系统会：

1. **解析文件**：提取文本内容
2. **分块处理**：将长文档分成 1000 字符的块（带 200 字符重叠）
3. **创建索引**：
   - 关键词索引（用于精确匹配）
   - 向量索引（用于语义搜索）

### 2. 问答流程

```
用户提问
    ↓
Agent 分析问题
    ↓
选择检索工具
    ↓
查找相关内容
    ↓
生成回答
```

### 3. 可用工具

Agent 可以调用以下工具：

#### keyword_search
- **用途**：查找包含特定关键词的内容
- **适用场景**：
  - 查找定义："什么是线性规划？"
  - 查找特定概念："单纯形法"
  - 查找代码示例："Python 实现"

#### semantic_search
- **用途**：查找语义相关的内容
- **适用场景**：
  - 概念性问题："如何优化生产计划？"
  - 相关主题："运筹学的应用"
  - 即使不包含完全相同的词也能找到

#### get_page_content
- **用途**：获取指定页面的完整内容
- **适用场景**：
  - "第二章讲了什么？"
  - "第 5 页的内容是什么？"

#### get_chunk_by_id
- **用途**：获取特定文本块的完整内容
- **适用场景**：
  - 当搜索结果中有感兴趣的块时
  - 需要查看更多上下文时

## 使用示例

### 基础用法

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

### 交互式模式

```bash
python -m src.agent.main tutor examples/materials/linear_programming.txt
```

然后输入问题：
```
Your question: 什么是线性规划？
```

### 使用 PDF

```python
answer = await run_tutor(
    question="单纯形法的步骤是什么？",
    materials=["textbook.pdf"]
)
```

### 多个材料

```python
answer = await run_tutor(
    question="比较线性规划和整数规划",
    materials=[
        "linear_programming.pdf",
        "integer_programming.pdf"
    ]
)
```

## 最佳实践

### 1. 问题设计

✅ **好的问题**：
- "什么是线性规划的标准形式？"
- "单纯形法的基本步骤是什么？"
- "如何用 Python 求解线性规划？请给出代码示例。"

❌ **不好的问题**：
- "告诉我所有内容"（太宽泛）
- "这个"（缺少上下文）

### 2. 材料准备

✅ **好的材料**：
- 结构清晰的文档
- 有章节标题
- 内容相关且完整

❌ **避免**：
- 扫描版 PDF（文字无法提取）
- 纯图片内容
- 格式混乱的文档

### 3. 性能优化

- **文件大小**：PDF 建议 < 50MB
- **分块大小**：默认 1000 字符，可调整
- **检索数量**：默认返回 3 个结果，可增加到 5-10

## 配置选项

### 调整分块大小

```python
from src.utils.pdf_processor import PDFProcessor

processor = PDFProcessor(
    chunk_size=1500,      # 增加块大小
    chunk_overlap=300     # 增加重叠
)
```

### 调整检索数量

```python
# 返回更多结果
results = material_manager.keyword_search(
    query="线性规划",
    top_k=10  # 默认是 3
)
```

### 自定义 Embedding 模型

```python
from src.utils.vector_store import VectorStore

vector_store = VectorStore(
    embedding_model="models/text-embedding-004"  # Gemini embedding
)
```

## 故障排除

### 问题：找不到相关内容

**解决方案**：
1. 尝试不同的关键词
2. 使用语义搜索而不是关键词搜索
3. 增加 top_k 参数
4. 检查材料是否包含相关内容

### 问题：PDF 无法加载

**解决方案**：
1. 确保安装了 PyPDF2：`pip install PyPDF2`
2. 检查 PDF 是否损坏
3. 确保 PDF 包含可提取的文本（不是纯图片）

### 问题：响应太慢

**解决方案**：
1. 减少材料数量
2. 使用更小的 PDF
3. 减少 top_k 参数
4. 考虑预处理材料并缓存

## 高级用法

### 直接使用材料管理器

```python
from src.utils.material_tools import get_material_manager

manager = get_material_manager()

# 加载材料
info = manager.load_material("textbook.pdf")
print(f"Loaded {info['total_chunks']} chunks")

# 关键词搜索
results = manager.keyword_search("线性规划", top_k=5)
for result in results:
    print(f"Page {result['page_num']}: {result['preview']}")

# 语义搜索
results = manager.semantic_search("如何优化", top_k=5)
for result in results:
    print(f"Chunk {result['chunk_id']}: {result['preview']}")
```

### 自定义工具

你可以在 `src/agent/tools.py` 中添加新的工具：

```python
def create_custom_tool():
    return FunctionDeclaration(
        name="my_custom_tool",
        description="My custom tool description",
        parameters={
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            }
        }
    )
```

## 限制

1. **PDF 大小**：建议 < 50MB
2. **文本提取**：仅支持文本 PDF，不支持扫描版
3. **语言**：主要支持中英文
4. **并发**：同时处理多个材料可能较慢

## 未来改进

- [ ] 支持图片内容理解
- [ ] 支持表格提取
- [ ] 支持公式识别
- [ ] 缓存机制
- [ ] 批量处理
- [ ] Web UI

## 参考

- [Gemini API 文档](https://ai.google.dev/docs)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [PyPDF2 文档](https://pypdf2.readthedocs.io/)
