"""
Math Agent 主入口
支持两种模式：
1. Tutor - 基于材料的问答和交互式学习
2. Solver - 自动求解数学优化问题
"""

import asyncio
from pathlib import Path
from .graph import app
from .schema import AgentMode, State
from src.utils.colored_logger import get_colored_logger, log_success, log_error

logger = get_colored_logger(__name__)


async def run_tutor(question: str, materials: list[str | Path]) -> str:
    """
    运行 Tutor 模式
    
    Args:
        question: 学生的问题
        materials: 学习材料路径列表
    
    Returns:
        回答结果
    """
    initial_state: State = {
        "mode": AgentMode.TUTOR,
        "question": question,
        "materials": materials
    }
    
    try:
        result = await app.ainvoke(initial_state)
        return result.get("result", "No response generated")
    except Exception as e:
        log_error(f"Error in tutor mode: {e}")
        return f"Error: {str(e)}"


async def run_solver(problem: str) -> dict:
    """
    运行 Solver 模式
    
    Args:
        problem: 优化问题描述
    
    Returns:
        包含解决方案、代码和结果的字典
    """
    initial_state: State = {
        "mode": AgentMode.SOLVER,
        "question": problem
    }
    
    try:
        result = await app.ainvoke(initial_state)
        return {
            "solution": result.get("result", "No solution generated"),
            "code": result.get("code", ""),
            "steps": result.get("solution_steps", [])
        }
    except Exception as e:
        log_error(f"Error in solver mode: {e}")
        return {
            "solution": f"Error: {str(e)}",
            "code": "",
            "steps": []
        }


async def interactive_tutor(materials: list[str | Path]):
    """交互式 Tutor 模式"""
    from src.utils.conversation_logger import get_conversation_logger, reset_conversation_logger
    
    # 重置并创建新的会话记录器
    reset_conversation_logger()
    logger_instance = get_conversation_logger()
    
    print("=" * 60)
    print("Math Tutor - Interactive Mode")
    print("=" * 60)
    print(f"Loaded {len(materials)} material(s)")
    print(f"Session ID: {logger_instance.session_id}")
    print(f"Conversation will be saved to: {logger_instance.markdown_file}")
    print("Type 'exit' to quit\n")
    
    while True:
        question = input("Your question: ").strip()
        
        if question.lower() in ['exit', 'quit', 'q']:
            # 显示会话摘要
            summary = logger_instance.get_session_summary()
            print("\n" + "=" * 60)
            print("Session Summary")
            print("=" * 60)
            print(f"Total Q&A exchanges: {summary['total_exchanges']}")
            print(f"Total images generated: {summary['total_images']}")
            print(f"Conversation saved to: {summary['markdown_file']}")
            print(f"Session directory: {summary['session_dir']}")
            
            # 显示缓存信息
            from src.utils.material_tools import get_material_manager
            manager = get_material_manager()
            loaded_materials = manager.get_loaded_materials()
            if loaded_materials:
                print(f"\nCached materials: {len(loaded_materials)}")
                for mat in loaded_materials:
                    print(f"  - {Path(mat).name}")
            
            # 导出 JSON
            json_file = logger_instance.export_json()
            print(f"JSON export: {json_file}")
            print("\nGoodbye!")
            break
        
        if not question:
            continue
        
        print("\n🤔 Thinking...\n")
        answer = await run_tutor(question, materials)
        print(f"📚 Tutor: {answer}\n")
        print("-" * 60 + "\n")


async def interactive_solver():
    """交互式 Solver 模式"""
    print("=" * 60)
    print("Math Solver - Interactive Mode")
    print("=" * 60)
    print("Describe your optimization problem")
    print("Type 'exit' to quit\n")
    
    while True:
        print("Enter your problem (or 'exit' to quit):")
        problem = input("> ").strip()
        
        if problem.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        
        if not problem:
            continue
        
        print("\n🔍 Analyzing problem...\n")
        result = await run_solver(problem)
        
        print("=" * 60)
        print(result["solution"])
        print("=" * 60 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m src.agent.main tutor [material_paths...]")
        print("  python -m src.agent.main solver")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "tutor":
        materials = sys.argv[2:] if len(sys.argv) > 2 else []
        if not materials:
            print("Please provide at least one material file")
            sys.exit(1)
        asyncio.run(interactive_tutor(materials))
    
    elif mode == "solver":
        asyncio.run(interactive_solver())
    
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes: tutor, solver")
        sys.exit(1)
