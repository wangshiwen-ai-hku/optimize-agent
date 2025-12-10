"""
演示脚本
展示 Math Agent 的核心功能
"""

import asyncio
from pathlib import Path
from src.agent.main import run_tutor, run_solver


async def demo_tutor():
    """演示 Tutor 模式"""
    print("\n" + "=" * 70)
    print("🎓 DEMO 1: Tutor 模式 - 智能数学导师")
    print("=" * 70)
    
    material_path = "examples/materials/linear_programming.txt"
    
    if not Path(material_path).exists():
        print("❌ 材料文件不存在，请先运行项目")
        return
    
    print("\n📚 加载材料: linear_programming.txt")
    print("💬 提问: 什么是线性规划？请简要说明。\n")
    
    try:
        answer = await run_tutor(
            question="什么是线性规划？请简要说明。",
            materials=[material_path]
        )
        
        print("🤖 Tutor 回答:")
        print("-" * 70)
        print(answer)
        print("-" * 70)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n💡 提示: 请确保设置了 GOOGLE_API_KEY 环境变量")


async def demo_solver():
    """演示 Solver 模式"""
    print("\n" + "=" * 70)
    print("🔍 DEMO 2: Solver 模式 - 自动优化求解器")
    print("=" * 70)
    
    problem = """
    简单的线性规划问题：
    
    最大化 z = 3x + 2y
    
    约束条件：
    - x + y <= 4
    - x >= 0
    - y >= 0
    
    求最优解。
    """
    
    print("\n📝 优化问题:")
    print(problem)
    
    try:
        result = await run_solver(problem)
        
        print("\n🤖 Solver 结果:")
        print("=" * 70)
        print(result["solution"])
        print("=" * 70)
        
        if result["code"]:
            print("\n💻 生成的代码:")
            print("-" * 70)
            print(result["code"])
            print("-" * 70)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n💡 提示: 请确保设置了 GOOGLE_API_KEY 环境变量")


async def demo_pdf_tools():
    """演示 PDF 工具"""
    print("\n" + "=" * 70)
    print("📄 DEMO 3: PDF 检索工具")
    print("=" * 70)
    
    from src.utils.material_tools import MaterialManager
    
    material_path = "examples/materials/linear_programming.txt"
    
    if not Path(material_path).exists():
        print("❌ 材料文件不存在")
        return
    
    try:
        manager = MaterialManager()
        
        print("\n1️⃣ 加载材料...")
        info = manager.load_material(material_path)
        print(f"   ✅ 已加载: {info['file_name']}")
        print(f"   - 文本块数: {info['total_chunks']}")
        print(f"   - 总字符数: {info['total_characters']}")
        
        print("\n2️⃣ 关键词搜索: '单纯形法'")
        results = manager.keyword_search("单纯形法", top_k=2)
        print(f"   ✅ 找到 {len(results)} 个结果")
        
        if results:
            print(f"\n   第一个结果预览:")
            print(f"   {results[0]['preview'][:150]}...")
        
        print("\n3️⃣ 语义搜索: '如何求解优化问题'")
        print("   ⏳ 正在生成 embeddings...")
        results = manager.semantic_search("如何求解优化问题", top_k=2)
        print(f"   ✅ 找到 {len(results)} 个结果")
        
        if results:
            print(f"\n   第一个结果预览:")
            print(f"   {results[0]['preview'][:150]}...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if "GOOGLE_API_KEY" in str(e) or "api_key" in str(e).lower():
            print("\n💡 提示: 语义搜索需要 GOOGLE_API_KEY")
        else:
            import traceback
            traceback.print_exc()


async def main():
    """运行所有演示"""
    print("\n" + "=" * 70)
    print("🚀 Math Agent 功能演示")
    print("=" * 70)
    print("\n本演示将展示:")
    print("1. Tutor 模式 - 基于材料的智能问答")
    print("2. Solver 模式 - 自动优化问题求解")
    print("3. PDF 工具 - 智能检索功能")
    
    # Demo 3: PDF 工具（不需要 API key）
    await demo_pdf_tools()
    
    # 检查是否有 API key
    import os
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n" + "=" * 70)
        print("⚠️  未检测到 GOOGLE_API_KEY")
        print("=" * 70)
        print("\n跳过需要 API 的演示（Demo 1 和 Demo 2）")
        print("\n要运行完整演示，请:")
        print("1. 在 .env 文件中设置 GOOGLE_API_KEY")
        print("2. 或运行: export GOOGLE_API_KEY=your_key")
        print("\n获取 API key: https://makersuite.google.com/app/apikey")
        return
    
    # Demo 1: Tutor
    await demo_tutor()
    
    # 暂停一下
    await asyncio.sleep(2)
    
    # Demo 2: Solver
    await demo_solver()
    
    # 总结
    print("\n" + "=" * 70)
    print("✅ 演示完成！")
    print("=" * 70)
    print("\n下一步:")
    print("- 查看 QUICKSTART.md 了解更多用法")
    print("- 运行 python -m src.agent.main tutor <材料路径> 开始使用")
    print("- 运行 python -m src.agent.main solver 求解优化问题")
    print("- 查看 examples/ 目录获取更多示例")


if __name__ == "__main__":
    asyncio.run(main())
