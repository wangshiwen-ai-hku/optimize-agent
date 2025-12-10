"""
Tutor 模式示例
演示如何使用 tutor 模式进行基于材料的问答
"""

import asyncio
from pathlib import Path
from src.agent.main import run_tutor


async def main():
    # 示例 1: 基于文本材料的问答
    print("=" * 60)
    print("Example 1: Linear Programming Tutorial")
    print("=" * 60)
    
    # 假设有一个线性规划的教材
    materials = ["examples/materials/linear_programming.txt"]
    
    questions = [
        "什么是线性规划？",
        "线性规划的标准形式是什么？",
        "单纯形法的基本思想是什么？"
    ]
    
    for question in questions:
        print(f"\n❓ Question: {question}")
        answer = await run_tutor(question, materials)
        print(f"📚 Answer:\n{answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
