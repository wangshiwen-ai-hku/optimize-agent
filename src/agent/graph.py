from langgraph.graph import StateGraph
from .schema import State, AgentMode
from src.config.manager import ConfigManager
from langchain.chat_models import init_chat_model
from dataclasses import asdict
from src.utils.multi_modal_utils import create_interleaved_multimodal_message, create_multimodal_message
from src.utils.colored_logger import get_colored_logger, init_default_logger, log_agent, log_state, log_tool, log_success, log_warning, log_error, log_debug
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import END
import base64
import os
from datetime import datetime
from google import genai
from google.genai.types import Part, GenerateContentConfig, ImageConfig, FinishReason
from dotenv import load_dotenv
from google.genai.types import HttpOptions
from PIL import Image
from src.utils.image_generation import image_generation_tool
import json
from pathlib import Path
import subprocess
import tempfile
from src.utils.material_tools import get_material_manager
from .tools import create_material_tools, execute_tool_call

MAX_REFLECTIONS = 3
config_path = Path(__file__).parent / "config.yaml"

config = ConfigManager(config_path)

load_dotenv()

# Initialize colored logger
init_default_logger(__name__)
logger = get_colored_logger(__name__)


# Initialize agents
tutor_config = config.get_agent_config("tutor")
solver_config = config.get_agent_config("solver")
executor_config = config.get_agent_config("code_executor")

# Initialize Gemini client
client = genai.Client()

graph = StateGraph(State)


async def init_context_node(state: State) -> State:
    """初始化上下文，设置默认值"""
    log_agent("INIT", "Initializing context")
    
    if "messages" not in state:
        state["messages"] = []
    if "reflection_count" not in state:
        state["reflection_count"] = 0
    
    log_state(f"Mode: {state.get('mode', 'unknown')}")
    return state


def route_by_mode(state: State) -> str:
    """根据模式路由到不同的节点"""
    mode = state.get("mode", AgentMode.TUTOR)
    log_debug(f"Routing to mode: {mode}")
    
    if mode == AgentMode.TUTOR:
        return "tutor_node"
    elif mode == AgentMode.SOLVER:
        return "solver_node"
    else:
        return END


async def tutor_node(state: State) -> State:
    """
    Tutor 模式：基于材料进行问答和交互式探索
    支持 PDF 检索和工具调用
    """
    log_agent("TUTOR", "Processing question")
    
    question = state.get("question", "")
    materials = state.get("materials", [])
    
    # 获取材料管理器
    material_manager = get_material_manager()
    
    # 加载材料
    material_info = []
    for material in materials:
        if isinstance(material, (str, Path)):
            path = Path(material)
            if path.exists():
                try:
                    info = material_manager.load_material(path)
                    material_info.append(f"- {info['file_name']}: {info.get('total_pages', 1)} pages, {info['total_chunks']} chunks")
                    log_success(f"Loaded material: {info['file_name']}")
                except Exception as e:
                    log_warning(f"Failed to load {path}: {e}")
    
    # 构建提示
    system_prompt = tutor_config.prompt or ""
    materials_summary = "\n".join(material_info)
    
    initial_message = f"""
Available Materials:
{materials_summary}

You have access to the following tools to search and retrieve information from the materials:
1. keyword_search: Search for specific keywords or terms
2. semantic_search: Search for semantically related content
3. get_page_content: Get full content of a specific page
4. get_chunk_by_id: Get full content of a specific chunk (use the chunk_id from search results)

Student Question:
{question}

INSTRUCTIONS:
- Use the tools MULTIPLE TIMES to gather comprehensive information
- Work CONTINUOUSLY without stopping to ask for permission
- Call tools as many times as needed (you can make 8-10 tool calls)
- Only provide your final answer when you have sufficient information
- If you say "let me check X", immediately call the appropriate tool to check X

CITATION FORMAT (CRITICAL):
- In your FINAL ANSWER, cite sources using "第 X 页" or "第 X 章"
- DO NOT use "Chunk X" or "chunk_id" in your final answer - these are internal identifiers
- The search results show page numbers - use those for citations
- Example: "根据第 5 页的内容..." NOT "根据 Chunk 13..."
- Make your answer readable and professional for students

Start by searching for relevant information, then continue gathering more details until you can provide a complete answer with proper page-based citations.
"""
    
    # 创建工具
    tools = create_material_tools()
    
    # 调用 Gemini with tools - 连续工作模式
    try:
        messages = [{"role": "user", "parts": [{"text": system_prompt + "\n\n" + initial_message}]}]
        
        max_iterations = 10  # 增加最大迭代次数，允许更多工具调用
        iteration = 0
        tool_call_count = 0
        
        while iteration < max_iterations:
            iteration += 1
            log_debug(f"Tutor iteration {iteration}/{max_iterations}")
            
            response = client.models.generate_content(
                model=tutor_config.model.model,
                contents=messages,
                config=GenerateContentConfig(
                    temperature=tutor_config.model.temperature,
                    tools=tools
                )
            )
            
            # 检查是否有工具调用
            if response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                
                # 如果有函数调用
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    tool_name = function_call.name
                    tool_args = dict(function_call.args)
                    tool_call_count += 1
                    
                    log_tool(tool_name, f"Call #{tool_call_count} - Args: {tool_args}")
                    
                    # 执行工具
                    tool_result = execute_tool_call(tool_name, tool_args, material_manager)
                    
                    # 添加助手的函数调用到消息历史
                    messages.append({
                        "role": "model",
                        "parts": [{"function_call": function_call}]
                    })
                    
                    # 添加函数响应，并提示继续工作
                    messages.append({
                        "role": "user",
                        "parts": [{
                            "function_response": {
                                "name": tool_name,
                                "response": {"result": str(tool_result)}
                            }
                        }]
                    })
                    
                    log_success(f"Tool {tool_name} executed, continuing...")
                    
                    # 继续下一轮，让 Agent 决定是否需要更多信息
                    continue
                
                # 如果有文本响应
                elif hasattr(part, 'text') and part.text:
                    result = part.text
                    
                    # 检查是否是中间思考（包含"让我"、"我将"等）
                    thinking_phrases = ["让我", "我将", "让我们", "首先", "接下来", "然后"]
                    is_thinking = any(phrase in result for phrase in thinking_phrases)
                    
                    # 如果是中间思考且还有工具调用次数，继续
                    if is_thinking and tool_call_count < 8 and iteration < max_iterations - 1:
                        log_debug(f"Agent is thinking, continuing... ({result[:50]}...)")
                        
                        # 将思考过程添加到消息历史
                        messages.append({
                            "role": "model",
                            "parts": [{"text": result}]
                        })
                        
                        # 提示继续工作
                        messages.append({
                            "role": "user",
                            "parts": [{"text": "请继续查找信息并完成回答，不要停下来。"}]
                        })
                        
                        continue
                    
                    # 否则，这是最终答案
                    state["result"] = result
                    state["messages"].append({"role": "assistant", "content": result})
                    log_success(f"Tutor response generated (after {tool_call_count} tool calls)")
                    break
            
            # 如果没有更多操作，退出
            log_warning("No more actions from agent")
            break
        
        if iteration >= max_iterations:
            log_warning(f"Max iterations reached after {tool_call_count} tool calls")
            if "result" not in state:
                state["result"] = "抱歉，处理超时。已调用工具 " + str(tool_call_count) + " 次，但未能完成回答。"
        
    except Exception as e:
        log_error(f"Error in tutor node: {e}")
        state["result"] = f"Error: {str(e)}"
    
    return state


async def solver_node(state: State) -> State:
    """
    Solver 模式：自动求解数学优化问题
    """
    log_agent("SOLVER", "Analyzing optimization problem")
    
    question = state.get("question", "")
    
    # 构建提示
    system_prompt = solver_config.prompt or ""
    
    user_message = f"""
Optimization Problem:
{question}

Please:
1. Identify the problem type
2. Formulate the mathematical model
3. Generate Python code to solve it
4. Provide the solution

Format your response as:
## Problem Analysis
[Your analysis]

## Mathematical Formulation
[Variables, objective, constraints]

## Python Code
```python
[Your code]
```

## Solution Approach
[Explanation]
"""
    
    # 调用 Gemini
    try:
        response = client.models.generate_content(
            model=solver_config.model.model,
            contents=[
                {"role": "user", "parts": [{"text": system_prompt + "\n\n" + user_message}]}
            ],
            config=GenerateContentConfig(
                temperature=solver_config.model.temperature
            )
        )
        
        result = response.text
        
        # 提取代码
        code = extract_code_from_response(result)
        
        state["solution_steps"] = [result]
        state["code"] = code
        state["messages"].append({"role": "assistant", "content": result})
        
        log_success("Solution generated")
        
        # 如果有代码，尝试执行
        if code:
            return await execute_code_node(state)
        else:
            state["result"] = result
            
    except Exception as e:
        log_error(f"Error in solver node: {e}")
        state["result"] = f"Error: {str(e)}"
    
    return state


async def execute_code_node(state: State) -> State:
    """执行生成的代码"""
    log_agent("EXECUTOR", "Executing generated code")
    
    code = state.get("code", "")
    
    if not code:
        log_warning("No code to execute")
        return state
    
    try:
        # 创建临时文件执行代码
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # 执行代码
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 清理临时文件
        os.unlink(temp_file)
        
        if result.returncode == 0:
            execution_result = result.stdout
            log_success("Code executed successfully")
            state["result"] = f"{state.get('solution_steps', [''])[0]}\n\n## Execution Result\n```\n{execution_result}\n```"
        else:
            error_msg = result.stderr
            log_error(f"Code execution failed: {error_msg}")
            
            # 如果执行失败且未超过反思次数，尝试修复
            if state.get("reflection_count", 0) < MAX_REFLECTIONS:
                state["reflection_count"] = state.get("reflection_count", 0) + 1
                return await reflect_and_fix_node(state, error_msg)
            else:
                state["result"] = f"Code execution failed after {MAX_REFLECTIONS} attempts:\n{error_msg}"
                
    except Exception as e:
        log_error(f"Error executing code: {e}")
        state["result"] = f"Execution error: {str(e)}"
    
    return state


async def reflect_and_fix_node(state: State, error_msg: str) -> State:
    """反思并修复代码错误"""
    log_agent("REFLECTOR", f"Reflecting on error (attempt {state['reflection_count']}/{MAX_REFLECTIONS})")
    
    code = state.get("code", "")
    
    fix_prompt = f"""
The following code produced an error:

```python
{code}
```

Error message:
```
{error_msg}
```

Please fix the code and provide only the corrected Python code without explanation.
"""
    
    try:
        response = client.models.generate_content(
            model=executor_config.model.model,
            contents=[
                {"role": "user", "parts": [{"text": fix_prompt}]}
            ],
            config=GenerateContentConfig(
                temperature=executor_config.model.temperature
            )
        )
        
        fixed_code = extract_code_from_response(response.text)
        
        if fixed_code:
            state["code"] = fixed_code
            log_success("Code fixed, retrying execution")
            return await execute_code_node(state)
        else:
            state["result"] = f"Failed to fix code: {error_msg}"
            
    except Exception as e:
        log_error(f"Error in reflection: {e}")
        state["result"] = f"Reflection error: {str(e)}"
    
    return state


def extract_code_from_response(text: str) -> str:
    """从响应中提取 Python 代码"""
    import re
    
    # 查找 ```python ... ``` 代码块
    pattern = r'```python\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # 如果没有找到，尝试查找 ``` ... ```
    pattern = r'```\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    return ""


# 构建图
graph.add_node("init_context", init_context_node)
graph.add_node("tutor_node", tutor_node)
graph.add_node("solver_node", solver_node)

graph.set_entry_point("init_context")
graph.add_conditional_edges("init_context", route_by_mode)
graph.add_edge("tutor_node", END)
graph.add_edge("solver_node", END)

# 编译图
app = graph.compile()

