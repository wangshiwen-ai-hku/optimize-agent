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
    
    generate_diagram_tool = FunctionDeclaration(
        name="generate_diagram",
        description="生成示意图、流程图或可视化图表。用于帮助学生理解概念、算法流程、数学关系等。支持生成各种类型的图表。",
        parameters={
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "图表描述，详细说明要生成什么样的图表，包括内容、风格、标注等"
                },
                "diagram_type": {
                    "type": "string",
                    "description": "图表类型，如：flowchart（流程图）、concept_map（概念图）、algorithm（算法示意图）、mathematical_visualization（数学可视化）、comparison（对比图）等",
                    "default": "diagram"
                }
            },
            "required": ["description"]
        }
    )
    
    return [
        Tool(function_declarations=[
            keyword_search_tool,
            semantic_search_tool,
            get_page_content_tool,
            get_chunk_tool,
            generate_diagram_tool
        ])
    ]


def execute_tool_call(tool_name: str, args: Dict[str, Any], material_manager, conversation_logger=None) -> Any:
    """
    执行工具调用
    
    Args:
        tool_name: 工具名称
        args: 工具参数
        material_manager: 材料管理器实例
        conversation_logger: 对话记录器实例（可选）
        
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
    
    elif tool_name == "generate_diagram":
        from src.utils.image_generation import image_generation_tool
        import os
        
        description = args.get("description", "")
        diagram_type = args.get("diagram_type", "diagram")
        
        # 构建详细的图表生成提示
        prompt = f"Create a clear and educational {diagram_type} that illustrates: {description}. "
        prompt += "Use clear labels, annotations, and visual elements. Make it suitable for teaching and learning."
        
        try:
            # 使用配置的模型生成图片
            model = os.getenv("IMAGE_GEN_MODEL", "gemini-2.5-flash-image")
            image = image_generation_tool(
                text_prompt=prompt,
                image_paths=[],
                model=model
            )
            
            # 保存图片
            if conversation_logger:
                image_path = conversation_logger.save_image(image, description=diagram_type)
                return {
                    "success": True,
                    "message": f"图表已生成并保存",
                    "image_path": image_path,
                    "description": description
                }
            else:
                return {
                    "success": True,
                    "message": "图表已生成（未保存，因为没有会话记录器）",
                    "description": description
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"图表生成失败: {str(e)}",
                "description": description
            }
    
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
