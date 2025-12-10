# 项目结构

```
optimize-agent/
│
├── src/                          # 源代码
│   ├── agent/                    # Agent 核心
│   │   ├── config.yaml          # Agent 配置（tutor, solver, executor）
│   │   ├── schema.py            # 状态定义
│   │   ├── graph.py             # LangGraph 工作流
│   │   ├── tools.py             # 工具定义（NEW）
│   │   └── main.py              # 主入口
│   │
│   ├── config/                   # 配置管理
│   │   ├── manager.py           # 配置管理器
│   │   ├── model.py             # 模型配置
│   │   ├── mem.py               # 内存配置
│   │   └── schema.py            # 配置 schema
│   │
│   └── utils/                    # 工具函数
│       ├── colored_logger.py    # 彩色日志
│       ├── pdf_processor.py     # PDF 处理（NEW）
│       ├── material_tools.py    # 材料管理（NEW）
│       ├── vector_store.py      # 向量存储（NEW）
│       ├── llm_helper.py        # LLM 辅助
│       ├── json_utils.py        # JSON 工具
│       └── ...                  # 其他工具
│
├── examples/                     # 示例代码
│   ├── tutor_example.py         # Tutor 示例
│   ├── solver_example.py        # Solver 示例
│   ├── test_pdf_tutor.py        # PDF Tutor 测试（NEW）
│   ├── create_sample_pdf.py     # 创建示例 PDF（NEW）
│   └── materials/               # 学习材料
│       ├── linear_programming.txt
│       └── optimization_guide.pdf (生成)
│
├── docs/                         # 文档（NEW）
│   ├── TUTOR_GUIDE.md           # Tutor 使用指南
│   └── PDF_RETRIEVAL.md         # PDF 检索设计文档
│
├── test_agent.py                 # Agent 测试脚本
├── test_pdf_tools.py             # PDF 工具测试（NEW）
├── check_config.py               # 配置检查脚本
│
├── run_tutor.sh                  # Tutor 快速启动
├── run_solver.sh                 # Solver 快速启动
│
├── requirements.txt              # 依赖列表
├── README.md                     # 项目说明
├── QUICKSTART.md                 # 快速开始（NEW）
├── PROJECT_STRUCTURE.md          # 本文件（NEW）
│
├── .env                          # 环境变量
├── .gitignore                    # Git 忽略
└── private*.json                 # 私有配置
```

## 核心模块说明

### Agent 模块 (`src/agent/`)

**config.yaml**
- 定义 3 个 agent：tutor, solver, code_executor
- 配置模型参数和提示词

**schema.py**
- `AgentMode`: 运行模式枚举（TUTOR, SOLVER）
- `State`: 状态定义（问题、材料、结果等）

**graph.py**
- LangGraph 工作流定义
- 节点：init_context, tutor_node, solver_node
- 支持工具调用和多轮对话

**tools.py** ⭐ NEW
- 定义 4 个材料检索工具
- 工具执行逻辑
- 结果格式化

**main.py**
- 主入口函数
- `run_tutor()`: 运行 tutor 模式
- `run_solver()`: 运行 solver 模式
- 交互式界面

### Utils 模块 (`src/utils/`)

**pdf_processor.py** ⭐ NEW
- `PDFProcessor`: PDF 解析和分块
- `TextChunk`: 文本块数据结构
- 关键词搜索
- 页面内容管理

**material_tools.py** ⭐ NEW
- `MaterialManager`: 材料管理器
- 统一的检索接口
- 支持多种文件格式

**vector_store.py** ⭐ NEW
- `VectorStore`: 向量存储
- Gemini Embedding 集成
- 语义搜索

**colored_logger.py**
- 彩色日志输出
- 不同类型的日志（agent, tool, state, error）

### 示例模块 (`examples/`)

**tutor_example.py**
- 基础 tutor 使用示例
- 文本材料问答

**solver_example.py**
- 3 个优化问题示例
- LP, IP, NLP

**test_pdf_tutor.py** ⭐ NEW
- PDF 检索完整测试
- 多个问题测试

**create_sample_pdf.py** ⭐ NEW
- 创建示例 PDF
- 包含数学内容

## 数据流

### Tutor 模式数据流

```
用户问题
    ↓
main.py (run_tutor)
    ↓
graph.py (tutor_node)
    ↓
material_tools.py (MaterialManager)
    ├→ pdf_processor.py (关键词搜索)
    └→ vector_store.py (语义搜索)
    ↓
tools.py (execute_tool_call)
    ↓
Gemini API (生成回答)
    ↓
返回结果
```

### Solver 模式数据流

```
优化问题
    ↓
main.py (run_solver)
    ↓
graph.py (solver_node)
    ↓
Gemini API (分析问题 + 生成代码)
    ↓
graph.py (execute_code_node)
    ↓
subprocess (执行 Python 代码)
    ↓
成功 → 返回结果
失败 → reflect_and_fix_node → 重试
```

## 配置文件

### .env
```bash
GOOGLE_API_KEY=xxx
GOOGLE_PROVIDER=google_genai
```

### src/agent/config.yaml
```yaml
default_model:
  model_provider: ${GOOGLE_PROVIDER}
  model: gemini-2.5-flash
  api_key: ${GOOGLE_API_KEY}
  temperature: 0.7

agents:
  core:
    tutor: {...}
    solver: {...}
    code_executor: {...}
```

## 依赖关系

```
graph.py
  ├─ schema.py (State, AgentMode)
  ├─ tools.py (create_material_tools, execute_tool_call)
  ├─ material_tools.py (get_material_manager)
  └─ config/manager.py (ConfigManager)

tools.py
  └─ material_tools.py (MaterialManager)

material_tools.py
  ├─ pdf_processor.py (PDFProcessor)
  └─ vector_store.py (VectorStore)

pdf_processor.py
  └─ PyPDF2

vector_store.py
  ├─ numpy
  └─ google.genai (Embedding API)
```

## 扩展点

### 添加新的 Agent

1. 在 `config.yaml` 中添加配置
2. 在 `graph.py` 中添加节点
3. 在 `schema.py` 中添加模式（如需要）

### 添加新的工具

1. 在 `tools.py` 中定义工具
2. 在 `execute_tool_call()` 中添加执行逻辑
3. 在 `material_tools.py` 中实现功能（如需要）

### 支持新的文件格式

1. 在 `material_tools.py` 的 `load_material()` 中添加处理逻辑
2. 创建新的处理器（如 `docx_processor.py`）
3. 更新文档

## 测试

### 单元测试
- `test_pdf_tools.py`: PDF 工具测试（不需要 API）

### 集成测试
- `test_agent.py`: 完整 agent 测试（需要 API）
- `examples/test_pdf_tutor.py`: PDF tutor 测试

### 配置测试
- `check_config.py`: 配置加载测试

## 文档

- `README.md`: 项目概览
- `QUICKSTART.md`: 快速开始
- `docs/TUTOR_GUIDE.md`: Tutor 详细指南
- `docs/PDF_RETRIEVAL.md`: PDF 检索设计
- `PROJECT_STRUCTURE.md`: 本文件

## 版本历史

### v1.0 (初始版本)
- 基础 tutor 和 solver 功能
- 文本材料支持

### v2.0 (当前版本) ⭐
- PDF 支持
- 智能检索（关键词 + 语义）
- 工具调用
- 向量存储
- 完整文档
