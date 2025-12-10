"""
Agent 工具定义
为 Gemini 提供可调用的工具
"""

from typing import List, Dict, Any
from google.genai.types import Tool, FunctionDeclaration


# 定义材料检索工具
def create_material_tools() -> List[Tool]:
    """创建材料检索工具"""
    
    keyword_search_tool = FunctionDeclaration(
        name="keyword_search",
        description="在材料中进行关键词搜索。适用于查找包含特定术语或概念的内容。",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询，可以是关键词或短语"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回结果数量，默认为 3",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    )
    
    semantic_search_tool = FunctionDeclaration(
        name="semantic_search",
        description="在材料中进行语义搜索。适用于查找与问题语义相关的内容，即使不包含完全相同的关键词。",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询，描述你想找的内容"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回结果数量，默认为 3",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    )
    
    get_page_content_tool = FunctionDeclaration(
        name="get_page_content",
        description="获取材料中指定页面的完整内容。当你知道信息在哪一页时使用。",
        parameters={
            "type": "object",
            "properties": {
                "page_num": {
                    "type": "integer",
                    "description": "页码"
                }
            },
            "required": ["page_num"]
        }
    )
    
    get_chunk_tool = FunctionDeclaration(
        name="get_chunk_by_id",
        description="根据块 ID 获取文本块的完整内容。当搜索结果中有你感兴趣的块时使用。",
        parameters={
            "type": "object",
            "properties": {
                "chunk_id": {
                    "type": "integer",
                    "description": "文本块 ID"
                }
            },
            "required": ["chunk_id"]
        }
    )
    
    return [
        Tool(function_declarations=[
            keyword_search_tool,
            semantic_search_tool,
            get_page_content_tool,
            get_chunk_tool
        ])
    ]


def execute_tool_call(tool_name: str, args: Dict[str, Any], material_manager) -> Any:
    """
    执行工具调用
    
    Args:
        tool_name: 工具名称
        args: 工具参数
        material_manager: 材料管理器实例
        
    Returns:
        工具执行结果
    """
    if tool_name == "keyword_search":
        results = material_manager.keyword_search(
            query=args.get("query"),
            top_k=args.get("top_k", 3)
        )
        return format_search_results(results)
    
    elif tool_name == "semantic_search":
        results = material_manager.semantic_search(
            query=args.get("query"),
            top_k=args.get("top_k", 3)
        )
        return format_search_results(results)
    
    elif tool_name == "get_page_content":
        content = material_manager.get_page_content(
            page_num=args.get("page_num")
        )
        return content if content else "页面未找到或为空"
    
    elif tool_name == "get_chunk_by_id":
        chunk = material_manager.get_chunk_by_id(
            chunk_id=args.get("chunk_id")
        )
        if chunk:
            return f"第 {chunk['page_num']} 页的内容：\n{chunk['content']}"
        else:
            return "未找到指定的文本块"
    
    else:
        return f"未知工具: {tool_name}"


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """格式化搜索结果"""
    if not results:
        return "未找到相关内容"
    
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(
            f"[结果 {i}] 第 {result['page_num']} 页\n"
            f"{result['preview']}\n"
            f"(内部标识: chunk_{result['chunk_id']})\n"
        )
    
    return "\n".join(formatted)
