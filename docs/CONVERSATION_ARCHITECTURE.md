# 对话记录架构设计

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        User Input                            │
│                    (Question/Command)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   interactive_tutor()                        │
│  - 初始化 ConversationLogger                                 │
│  - 显示会话信息                                              │
│  - 处理用户输入                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      tutor_node()                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. 获取 ConversationLogger                            │  │
│  │ 2. 记录问题: logger.log_question()                    │  │
│  │ 3. 加载材料和创建工具                                 │  │
│  │ 4. 调用 Gemini with tools                             │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Tool Execution Loop                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ execute_tool_call(tool_name, args, material_manager,  │  │
│  │                   conversation_logger)                │  │
│  │                                                        │  │
│  │ 支持的工具:                                            │  │
│  │ - keyword_search                                      │  │
│  │ - semantic_search                                     │  │
│  │ - get_page_content                                    │  │
│  │ - get_chunk_by_id                                     │  │
│  │ - generate_diagram ⭐ NEW                             │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              generate_diagram Tool Flow                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. 接收描述和图表类型                                 │  │
│  │ 2. 构建详细提示                                       │  │
│  │ 3. 调用 image_generation_tool()                       │  │
│  │ 4. 保存图片: logger.save_image()                      │  │
│  │ 5. 返回图片路径                                       │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Final Answer Generation                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. Gemini 生成 Markdown 格式回答                      │  │
│  │ 2. 包含 LaTeX 数学公式                                │  │
│  │ 3. 使用专业引用格式                                   │  │
│  │ 4. 收集生成的图片路径                                 │  │
│  │ 5. 记录回答: logger.log_answer(answer, images)        │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ConversationLogger                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 写入文件:                                             │  │
│  │ - conversation.md (Markdown 格式)                     │  │
│  │ - conversation.json (JSON 格式)                       │  │
│  │ - images/*.png (生成的图片)                           │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    File System Output                        │
│  conversations/                                              │
│  └── session_YYYYMMDD_HHMMSS/                               │
│      ├── conversation.md                                     │
│      ├── conversation.json                                   │
│      └── images/                                             │
│          ├── timestamp_description.png                       │
│          └── ...                                             │
└─────────────────────────────────────────────────────────────┘
```

## 数据流

### 1. 问题记录流程

```
User Question
    │
    ▼
interactive_tutor()
    │
    ▼
tutor_node()
    │
    ▼
ConversationLogger.log_question()
    │
    ▼
Append to conversation.md:
    ## 🎓 Student Question
    {question}
    *Time: HH:MM:SS*
```

### 2. 工具调用流程

```
Gemini Function Call
    │
    ▼
execute_tool_call()
    │
    ├─→ keyword_search/semantic_search
    │   └─→ MaterialManager
    │       └─→ Return search results
    │
    ├─→ get_page_content/get_chunk_by_id
    │   └─→ MaterialManager
    │       └─→ Return content
    │
    └─→ generate_diagram
        └─→ image_generation_tool()
            └─→ Gemini/Qwen/Doubao/OpenAI API
                └─→ PIL Image
                    └─→ ConversationLogger.save_image()
                        └─→ images/timestamp_desc.png
```

### 3. 回答记录流程

```
Gemini Final Response (Markdown + LaTeX)
    │
    ▼
Collect generated image paths
    │
    ▼
ConversationLogger.log_answer(answer, images)
    │
    ▼
Append to conversation.md:
    ## 📚 Tutor Answer
    {markdown_content}
    
    ### Generated Images
    ![Image](images/xxx.png)
    
    *Time: HH:MM:SS*
    ---
```

## 核心组件

### ConversationLogger

**职责：**
- 管理会话生命周期
- 格式化和写入 Markdown
- 保存图片文件
- 导出 JSON 数据
- 生成会话摘要

**关键方法：**
```python
class ConversationLogger:
    def __init__(session_id, output_dir)
    def log_question(question)
    def log_answer(answer, images)
    def save_image(image, description) -> str
    def get_session_summary() -> dict
    def export_json() -> str
```

### Tool Integration

**generate_diagram 工具：**
```python
FunctionDeclaration(
    name="generate_diagram",
    description="生成示意图、流程图或可视化图表",
    parameters={
        "description": "图表描述",
        "diagram_type": "图表类型"
    }
)
```

**执行流程：**
1. 接收工具调用参数
2. 构建详细的图片生成提示
3. 调用 `image_generation_tool()`
4. 保存图片到会话目录
5. 返回成功状态和图片路径

### Markdown Formatting

**Tutor 提示中的格式化指令：**
```
OUTPUT FORMAT (CRITICAL):
- Your FINAL ANSWER must be in MARKDOWN format
- Mathematical formulas MUST use LaTeX syntax:
  * Inline math: $formula$
  * Display math: $$formula$$
- Use Markdown headers (##, ###)
- Use lists, bold, italic appropriately
```

## 会话生命周期

```
1. Session Start
   ├─→ reset_conversation_logger()
   ├─→ get_conversation_logger()
   └─→ Create session directory

2. Question-Answer Loop
   ├─→ log_question()
   ├─→ Tool calls (0-N times)
   │   └─→ Optional: generate_diagram
   │       └─→ save_image()
   └─→ log_answer()

3. Session End
   ├─→ get_session_summary()
   ├─→ export_json()
   └─→ Display summary
```

## 文件格式

### conversation.md 结构

```markdown
# Math Tutor Conversation

**Session ID:** session_YYYYMMDD_HHMMSS
**Start Time:** YYYY-MM-DD HH:MM:SS

---

## 🎓 Student Question

{question_text}

*Time: HH:MM:SS*

## 📚 Tutor Answer

{markdown_content_with_latex}

### Generated Images

![Image](images/xxx.png)

*Time: HH:MM:SS*

---

[Repeat for each Q&A pair]
```

### conversation.json 结构

```json
{
  "session_id": "session_YYYYMMDD_HHMMSS",
  "conversation": [
    {
      "role": "student",
      "content": "question text",
      "timestamp": "ISO8601"
    },
    {
      "role": "tutor",
      "content": "answer text",
      "images": ["path1", "path2"],
      "timestamp": "ISO8601"
    }
  ]
}
```

## 扩展性设计

### 1. 支持新的图表类型

在 `generate_diagram` 工具中添加新的 `diagram_type`：

```python
diagram_types = [
    "flowchart",
    "concept_map",
    "algorithm",
    "mathematical_visualization",
    "comparison",
    "timeline",  # NEW
    "tree_diagram",  # NEW
]
```

### 2. 支持新的输出格式

扩展 `ConversationLogger`：

```python
def export_html(self) -> str:
    """导出为 HTML 格式"""
    pass

def export_pdf(self) -> str:
    """导出为 PDF 格式"""
    pass
```

### 3. 支持会话恢复

```python
def load_session(session_id: str) -> ConversationLogger:
    """加载已有会话"""
    pass

def continue_session(self):
    """继续已有会话"""
    pass
```

## 性能考虑

### 1. 异步写入
- Markdown 写入是同步的（文件很小）
- 图片保存是同步的（必须等待完成）
- 可以考虑异步队列优化

### 2. 存储优化
- 图片压缩（PNG 优化）
- 定期清理旧会话
- 可选的云存储集成

### 3. 内存管理
- 对话历史存储在内存中
- 长会话可能需要分页
- 考虑流式写入大型会话

## 安全考虑

### 1. 路径安全
- 使用 `Path` 对象避免路径注入
- 文件名清理（移除特殊字符）
- 限制会话目录深度

### 2. 内容过滤
- 可选的敏感信息过滤
- 图片内容审核
- 用户隐私保护

### 3. 访问控制
- 会话目录权限设置
- 可选的加密存储
- 多用户隔离
