# PDF 检索功能设计文档

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    Tutor Agent                          │
│  (基于 Gemini 的智能导师，支持工具调用)                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ 调用工具
                 ↓
┌─────────────────────────────────────────────────────────┐
│              Material Tools (工具层)                     │
│  - keyword_search: 关键词搜索                            │
│  - semantic_search: 语义搜索                             │
│  - get_page_content: 获取页面内容                        │
│  - get_chunk_by_id: 获取文本块                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ 使用
                 ↓
┌─────────────────────────────────────────────────────────┐
│           Material Manager (管理层)                      │
│  - 材料加载和管理                                         │
│  - 多材料支持                                            │
│  - 统一接口                                              │
└────────┬───────────────────────────┬────────────────────┘
         │                           │
         │                           │
         ↓                           ↓
┌──────────────────┐      ┌──────────────────────┐
│  PDF Processor   │      │   Vector Store       │
│  - PDF 解析      │      │   - Embedding 生成   │
│  - 文本分块      │      │   - 语义搜索         │
│  - 关键词索引    │      │   - 相似度计算       │
└──────────────────┘      └──────────────────────┘
```

## 核心组件

### 1. PDF Processor (`src/utils/pdf_processor.py`)

**职责**：
- PDF 文本提取
- 智能分块（带重叠）
- 关键词搜索
- 页面内容管理

**关键类**：

```python
class TextChunk:
    content: str        # 文本内容
    page_num: int       # 页码
    chunk_id: int       # 块 ID
    metadata: Dict      # 元数据

class PDFProcessor:
    def load_pdf(pdf_path) -> str
    def keyword_search(query, top_k) -> List[TextChunk]
    def get_page_content(page_num) -> str
    def get_chunk_by_id(chunk_id) -> TextChunk
```

**分块策略**：
- 默认块大小：1000 字符
- 重叠大小：200 字符
- 按段落分割，保持语义完整性

### 2. Vector Store (`src/utils/vector_store.py`)

**职责**：
- 使用 Gemini Embedding API 生成向量
- 存储文本块和对应的向量
- 语义搜索（余弦相似度）

**关键类**：

```python
class VectorStore:
    def add_chunks(chunks: List[TextChunk])
    def semantic_search(query, top_k) -> List[TextChunk]
```

**Embedding 模型**：
- 默认：`models/text-embedding-004`
- 维度：768
- 支持中英文

### 3. Material Manager (`src/utils/material_tools.py`)

**职责**：
- 统一管理多个材料
- 提供高层次的检索接口
- 支持多种文件格式

**关键类**：

```python
class MaterialManager:
    def load_material(path) -> Dict
    def keyword_search(query, top_k) -> List[Dict]
    def semantic_search(query, top_k) -> List[Dict]
    def get_page_content(page_num) -> str
    def get_chunk_by_id(chunk_id) -> Dict
```

### 4. Agent Tools (`src/agent/tools.py`)

**职责**：
- 定义 Gemini Function Calling 工具
- 执行工具调用
- 格式化结果

**工具定义**：

```python
def create_material_tools() -> List[Tool]:
    # 返回 4 个工具的定义
    - keyword_search
    - semantic_search
    - get_page_content
    - get_chunk_by_id

def execute_tool_call(tool_name, args, manager) -> Any:
    # 执行具体的工具调用
```

## 工作流程

### 材料加载流程

```
1. 用户提供材料路径
   ↓
2. MaterialManager.load_material()
   ↓
3. 根据文件类型选择处理器
   ↓
4. PDFProcessor 提取文本并分块
   ↓
5. VectorStore 生成 embeddings
   ↓
6. 返回材料摘要信息
```

### 问答流程

```
1. 用户提问
   ↓
2. Tutor Agent 接收问题
   ↓
3. Agent 分析问题，决定使用哪个工具
   ↓
4. 调用工具（如 semantic_search）
   ↓
5. MaterialManager 执行搜索
   ↓
6. 返回相关文本块
   ↓
7. Agent 基于检索结果生成回答
   ↓
8. 如需更多信息，重复步骤 3-7
   ↓
9. 返回最终答案
```

## 检索策略

### 关键词搜索 (Keyword Search)

**算法**：
```python
score = matching_terms_count + exact_phrase_count * 10
```

**适用场景**：
- 查找特定术语
- 精确匹配
- 定义查询

**示例**：
- "什么是线性规划？" → 搜索 "线性规划"
- "单纯形法" → 精确匹配

### 语义搜索 (Semantic Search)

**算法**：
```python
similarity = cosine_similarity(query_embedding, chunk_embedding)
```

**适用场景**：
- 概念性问题
- 相关主题查找
- 不确定关键词时

**示例**：
- "如何优化生产计划？" → 找到线性规划相关内容
- "求解方法" → 找到单纯形法、内点法等

## 性能优化

### 1. 分块策略

**当前实现**：
- 块大小：1000 字符
- 重叠：200 字符

**优化建议**：
- 根据文档类型调整块大小
- 教材：1500-2000 字符
- 论文：800-1000 字符
- 代码文档：500-800 字符

### 2. 缓存机制

**建议实现**：
```python
# 缓存 embeddings
cache = {
    "material_path": {
        "chunks": [...],
        "embeddings": [...],
        "timestamp": ...
    }
}
```

### 3. 批量处理

**当前**：逐个生成 embedding
**优化**：批量生成（Gemini 支持批量）

```python
# 批量生成 embeddings
embeddings = client.models.embed_content(
    model="text-embedding-004",
    content=[chunk1, chunk2, chunk3, ...]
)
```

## 扩展性

### 支持新文件类型

```python
# 在 MaterialManager.load_material() 中添加
elif material_path.suffix.lower() == '.docx':
    # 处理 Word 文档
    processor = DocxProcessor()
    ...
```

### 添加新工具

```python
# 在 tools.py 中添加
def create_custom_tool():
    return FunctionDeclaration(
        name="find_equations",
        description="查找文档中的数学公式",
        parameters={...}
    )
```

### 多语言支持

```python
# 使用不同的 embedding 模型
vector_store = VectorStore(
    embedding_model="models/text-multilingual-embedding-002"
)
```

## 限制和注意事项

### 当前限制

1. **PDF 大小**：建议 < 50MB
2. **文本提取**：仅支持文本 PDF
3. **Embedding 成本**：每个块需要一次 API 调用
4. **内存使用**：所有向量存储在内存中

### 注意事项

1. **API 限流**：Gemini API 有速率限制
2. **文本质量**：扫描版 PDF 需要 OCR
3. **语言混合**：中英混合文档可能影响检索效果
4. **公式处理**：数学公式可能无法正确提取

## 测试

### 单元测试

```bash
# 测试 PDF 工具（不需要 API key）
python test_pdf_tools.py
```

### 集成测试

```bash
# 测试完整流程（需要 API key）
python examples/test_pdf_tutor.py
```

### 性能测试

```python
import time

start = time.time()
manager.load_material("large_textbook.pdf")
print(f"Loading time: {time.time() - start:.2f}s")

start = time.time()
results = manager.semantic_search("optimization", top_k=10)
print(f"Search time: {time.time() - start:.2f}s")
```

## 未来改进

### 短期（1-2 周）

- [ ] 添加缓存机制
- [ ] 批量 embedding 生成
- [ ] 支持 Word 文档
- [ ] 添加更多测试

### 中期（1-2 月）

- [ ] 支持图片内容理解
- [ ] 支持表格提取
- [ ] 支持公式识别
- [ ] Web UI

### 长期（3-6 月）

- [ ] 分布式向量存储（如 Pinecone）
- [ ] 增量更新机制
- [ ] 多模态检索
- [ ] 知识图谱集成

## 参考资料

- [Gemini Function Calling](https://ai.google.dev/docs/function_calling)
- [Gemini Embedding API](https://ai.google.dev/docs/embeddings)
- [PyPDF2 文档](https://pypdf2.readthedocs.io/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
