"""
Solver 模式示例
演示如何使用 solver 模式自动求解优化问题
"""

import asyncio
from src.agent.main import run_solver


async def main():
    # 示例 1: 线性规划问题
    print("=" * 60)
    print("Example 1: Linear Programming")
    print("=" * 60)
    
    problem1 = """
    一个工厂生产两种产品 A 和 B。
    - 产品 A 每件利润 40 元，需要 2 小时加工，3 小时装配
    - 产品 B 每件利润 30 元，需要 1 小时加工，2 小时装配
    - 每天有 100 小时加工时间，120 小时装配时间
    
    求如何安排生产使利润最大？
    """
    
    result = await run_solver(problem1)
    print(result["solution"])
    print("\n" + "=" * 60 + "\n")
    
    # 示例 2: 整数规划问题
    print("=" * 60)
    print("Example 2: Integer Programming")
    print("=" * 60)
    
    problem2 = """
    背包问题：
    有 5 个物品，重量分别为 [2, 3, 4, 5, 6]，价值分别为 [3, 4, 5, 6, 7]
    背包容量为 10
    
    求如何选择物品使总价值最大？
    """
    
    result = await run_solver(problem2)
    print(result["solution"])
    print("\n" + "=" * 60 + "\n")
    
    # 示例 3: 非线性优化问题
    print("=" * 60)
    print("Example 3: Nonlinear Optimization")
    print("=" * 60)
    
    problem3 = """
    最小化函数 f(x, y) = (x - 2)^2 + (y - 3)^2
    约束条件：
    - x + y <= 5
    - x >= 0
    - y >= 0
    """
    
    result = await run_solver(problem3)
    print(result["solution"])
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
