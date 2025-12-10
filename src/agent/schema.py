from webbrowser import BackgroundBrowser
from mcp.types import TextResourceContents
from pydantic import BaseModel, Field
from typing import List, Dict, NotRequired, TypedDict, Optional, Annotated
from enum import Enum
from pathlib import Path

class AgentMode(str, Enum):
    TUTOR = "tutor"
    SOLVER = "solver"

class State(TypedDict):
    mode: AgentMode  # 运行模式：tutor 或 solver
    materials: NotRequired[List[str|Path]]  # tutor 模式的学习材料
    question: str  # 用户问题
    context: NotRequired[str]  # 从材料中提取的相关上下文
    solution_steps: NotRequired[List[str]]  # solver 模式的求解步骤
    code: NotRequired[str]  # 生成的求解代码
    result: NotRequired[str]  # 最终结果
    messages: NotRequired[List[Dict]]  # 对话历史
    reflection_count: NotRequired[int]  # 反思次数




    