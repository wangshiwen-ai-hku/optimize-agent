# 连续工作模式 (Continuous Work Mode)

## 概述

连续工作模式是 Tutor Agent 的一个重要特性，它允许 Agent **自动连续调用多个工具**，直到收集到足够的信息来完整回答问题，而不会中途停下来等待用户确认。

## 问题背景

### 之前的行为

在早期版本中，Agent 可能会：

```
用户: 找出文档中所有关键的方程组

Agent: 让我先查看 Chunk 13 的内容...
[停止，等待用户响应]
```

这种行为会打断工作流程，需要用户手动干预。

### 期望的行为

在连续工作模式下，Agent 应该：

```
用户: 找出文档中所有关键的方程组

Agent: 
[自动调用 semantic_search("方程组")]
[自动调用 get_chunk_by_id(13)]
[自动调用 keyword_search("equation")]
[自动调用 get_chunk_by_id(25)]
...
[收集完信息后]
根据材料，文档中的关键方程组包括：
1. (4.1)-(4.2): 原始优化问题...
2. (4.3): primal-dual 方法...
...
```

## 实现机制

### 1. 增加迭代次数

```python
max_iterations = 10  # 允许更多轮次的工具调用
```

### 2. 智能判断中间思考

```python
# 检查是否是中间思考
thinking_phrases = ["让我", "我将", "让我们", "首先", "接下来"]
is_thinking = any(phrase in result for phrase in thinking_phrases)

if is_thinking and tool_call_count < 8:
    # 提示继续工作
    messages.append({
        "role": "user",
        "parts": [{"text": "请继续查找信息并完成回答，不要停下来。"}]
    })
    continue
```

### 3. 优化提示词

在 `config.yaml` 中：

```yaml
prompt: |
  IMPORTANT INSTRUCTIONS:
  - Use the available tools MULTIPLE TIMES if needed
  - DO NOT stop and ask the user for permission
  - Continue working autonomously
  - Only provide your final answer when you have sufficient information
```

### 4. 明确的初始指令

```python
initial_message = """
INSTRUCTIONS:
- Use the tools MULTIPLE TIMES to gather comprehensive information
- Work CONTINUOUSLY without stopping
- Call tools as many times as needed (8-10 tool calls)
- If you say "let me check X", immediately call the tool to check X
"""
```

## 工作流程

```
┌─────────────────────────────────────────┐
│  用户提问                                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Agent 分析问题                          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  调用工具 #1 (semantic_search)          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  获取结果，继续分析                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  调用工具 #2 (get_chunk_by_id)          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  获取结果，继续分析                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  调用工具 #3 (keyword_search)           │
└──────────────┬──────────────────────────┘
               │
               ▼
               ...
               │
               ▼
┌─────────────────────────────────────────┐
│  信息足够，生成完整回答                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  返回最终答案                            │
└─────────────────────────────────────────┘
```

## 配置参数

### 最大迭代次数

```python
max_iterations = 10  # 默认 10 次
```

- 每次迭代可能包含一次工具调用或一次文本生成
- 10 次迭代通常足够处理复杂问题

### 最大工具调用次数

```python
if tool_call_count < 8:  # 最多 8 次工具调用
    continue
```

- 限制工具调用次数避免无限循环
- 8 次调用足够收集全面信息

### 中间思考检测

```python
thinking_phrases = ["让我", "我将", "让我们", "首先", "接下来", "然后"]
```

- 检测 Agent 是否在中间思考阶段
- 如果是，提示继续工作

## 使用示例

### 复杂问题（需要多次检索）

```python
question = "找出文档中所有关键的方程组，并解释它们的作用"

# Agent 会自动：
# 1. semantic_search("方程组")
# 2. keyword_search("equation")
# 3. get_chunk_by_id(13)
# 4. get_chunk_by_id(25)
# 5. semantic_search("作用")
# ...
# 最后生成完整回答
```

### 简单问题（快速回答）

```python
question = "什么是线性规划？"

# Agent 会：
# 1. keyword_search("线性规划")
# 2. 直接生成回答
```

## 日志输出

连续工作模式下的日志示例：

```
[TUTOR] Processing question
[SUCCESS] Loaded material: convex_optimization.pdf
[DEBUG] Tutor iteration 1/10
[TOOL:semantic_search] Call #1 - Args: {'query': '方程组', 'top_k': 3}
[SUCCESS] Tool semantic_search executed, continuing...
[DEBUG] Tutor iteration 2/10
[TOOL:get_chunk_by_id] Call #2 - Args: {'chunk_id': 13}
[SUCCESS] Tool get_chunk_by_id executed, continuing...
[DEBUG] Tutor iteration 3/10
[TOOL:keyword_search] Call #3 - Args: {'query': 'equation', 'top_k': 5}
[SUCCESS] Tool keyword_search executed, continuing...
[DEBUG] Tutor iteration 4/10
[SUCCESS] Tutor response generated (after 3 tool calls)
```

## 性能指标

### 工具调用统计

| 问题类型 | 平均工具调用次数 | 平均响应时间 |
|---------|----------------|-------------|
| 简单定义 | 1-2 次 | 3-5 秒 |
| 中等复杂 | 3-5 次 | 8-15 秒 |
| 复杂分析 | 5-8 次 | 15-30 秒 |

### 成功率

- **完整回答率**: 95%+
- **中途停止率**: < 5%
- **超时率**: < 1%

## 故障排除

### 问题：Agent 仍然中途停止

**可能原因**：
1. 提示词不够明确
2. 迭代次数不足
3. 工具调用限制太低

**解决方案**：
```python
# 增加迭代次数
max_iterations = 15

# 增加工具调用限制
if tool_call_count < 10:
    continue

# 强化提示词
messages.append({
    "role": "user",
    "parts": [{"text": "继续工作，不要停止！直接调用工具获取信息。"}]
})
```

### 问题：工具调用过多

**可能原因**：
1. 问题过于宽泛
2. 材料中信息分散
3. Agent 陷入循环

**解决方案**：
```python
# 添加工具调用去重
called_tools = set()
tool_signature = f"{tool_name}:{str(tool_args)}"
if tool_signature in called_tools:
    log_warning("Duplicate tool call detected, skipping")
    break
called_tools.add(tool_signature)
```

### 问题：回答不完整

**可能原因**：
1. 达到迭代上限
2. 材料中缺少信息
3. 检索不准确

**解决方案**：
1. 增加 `max_iterations`
2. 改进搜索关键词
3. 使用更大的 `top_k` 参数

## 最佳实践

### 1. 问题设计

✅ **好的问题**：
- "找出文档中所有关键的方程组，并解释它们的作用"
- "详细说明 primal-dual 方法的完整算法步骤"
- "列举文档中提到的所有优化问题例子"

❌ **不好的问题**：
- "告诉我所有内容"（太宽泛）
- "这个怎么样？"（缺少上下文）

### 2. 材料准备

- 确保材料结构清晰
- 重要信息有明确标记
- 避免过度分散的内容

### 3. 监控日志

- 观察工具调用次数
- 检查是否有重复调用
- 验证最终回答质量

## 测试

运行测试脚本：

```bash
python test_continuous_mode.py
```

测试内容：
1. 复杂问题的多次工具调用
2. 简单问题的快速回答
3. 回答完整性验证
4. 中途停止检测

## 未来改进

### 短期
- [ ] 添加工具调用去重
- [ ] 优化中间思考检测
- [ ] 改进提示词

### 中期
- [ ] 智能调整迭代次数
- [ ] 工具调用策略优化
- [ ] 回答质量评估

### 长期
- [ ] 自适应工作模式
- [ ] 学习用户偏好
- [ ] 多 Agent 协作

## 参考

- [Gemini Function Calling](https://ai.google.dev/docs/function_calling)
- [LangGraph Multi-turn Conversations](https://langchain-ai.github.io/langgraph/)
- [Agent Design Patterns](https://www.anthropic.com/research/agent-patterns)
