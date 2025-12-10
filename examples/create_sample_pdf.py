"""
创建示例 PDF 文件用于测试
需要安装: pip install reportlab
"""

def create_sample_pdf():
    """创建一个包含数学内容的示例 PDF"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from pathlib import Path
        
        output_path = Path("examples/materials/optimization_guide.pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter
        
        # 第一页
        c.setFont("Helvetica-Bold", 16)
        c.drawString(inch, height - inch, "优化问题求解指南")
        
        c.setFont("Helvetica", 12)
        y = height - 1.5 * inch
        
        content_page1 = [
            "第一章：线性规划基础",
            "",
            "线性规划（Linear Programming, LP）是运筹学中的一个重要分支，",
            "用于在线性约束条件下优化线性目标函数。",
            "",
            "1.1 基本概念",
            "- 决策变量：需要确定的未知量",
            "- 目标函数：需要最大化或最小化的函数",
            "- 约束条件：决策变量必须满足的限制",
            "",
            "1.2 标准形式",
            "max/min z = c1*x1 + c2*x2 + ... + cn*xn",
            "s.t. a11*x1 + a12*x2 + ... + a1n*xn <= b1",
            "     a21*x1 + a22*x2 + ... + a2n*xn <= b2",
            "     ...",
            "     x1, x2, ..., xn >= 0",
        ]
        
        for line in content_page1:
            c.drawString(inch, y, line)
            y -= 0.25 * inch
        
        c.showPage()
        
        # 第二页
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, height - inch, "第二章：求解方法")
        
        c.setFont("Helvetica", 12)
        y = height - 1.5 * inch
        
        content_page2 = [
            "2.1 单纯形法",
            "单纯形法是求解线性规划的经典算法，由 George Dantzig 提出。",
            "",
            "算法步骤：",
            "1. 将问题转化为标准形式",
            "2. 找到初始基可行解",
            "3. 检验最优性",
            "4. 确定进基变量和出基变量",
            "5. 进行基变换",
            "6. 重复步骤 3-5 直到找到最优解",
            "",
            "2.2 Python 实现",
            "可以使用 scipy.optimize.linprog 函数：",
            "",
            "from scipy.optimize import linprog",
            "c = [-1, -2]  # 目标函数系数（最大化需要取负）",
            "A_ub = [[1, 1], [2, 1]]  # 不等式约束",
            "b_ub = [4, 5]",
            "result = linprog(c, A_ub=A_ub, b_ub=b_ub)",
        ]
        
        for line in content_page2:
            c.drawString(inch, y, line)
            y -= 0.25 * inch
        
        c.showPage()
        
        # 第三页
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, height - inch, "第三章：应用实例")
        
        c.setFont("Helvetica", 12)
        y = height - 1.5 * inch
        
        content_page3 = [
            "3.1 生产计划问题",
            "某工厂生产两种产品 A 和 B：",
            "- 产品 A：利润 40 元/件，需要 2 小时加工，3 小时装配",
            "- 产品 B：利润 30 元/件，需要 1 小时加工，2 小时装配",
            "- 每天有 100 小时加工时间，120 小时装配时间",
            "",
            "问题：如何安排生产使利润最大？",
            "",
            "建模：",
            "设 x1, x2 分别为产品 A 和 B 的产量",
            "max z = 40*x1 + 30*x2",
            "s.t. 2*x1 + x2 <= 100  (加工时间)",
            "     3*x1 + 2*x2 <= 120  (装配时间)",
            "     x1, x2 >= 0",
            "",
            "3.2 运输问题",
            "运输问题是线性规划的经典应用，目标是最小化运输成本。",
        ]
        
        for line in content_page3:
            c.drawString(inch, y, line)
            y -= 0.25 * inch
        
        c.save()
        
        print(f"✅ Sample PDF created: {output_path}")
        print(f"   File size: {output_path.stat().st_size} bytes")
        
    except ImportError:
        print("❌ reportlab is required. Install it with: pip install reportlab")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")


if __name__ == "__main__":
    create_sample_pdf()
