# 功能验证清单

## 📋 安装和配置

- [ ] 克隆项目
- [ ] 安装依赖: `pip install -r requirements.txt`
- [ ] 创建 `.env` 文件并设置 `GOOGLE_API_KEY`
- [ ] 运行配置检查: `python check_config.py`

## 🧪 基础测试

- [ ] 运行 PDF 工具测试（不需要 API）: `python test_pdf_tools.py`
- [ ] 运行演示脚本: `python demo.py`
- [ ] 运行完整测试（需要 API）: `python test_agent.py`

## 📚 Tutor 模式测试

### 文本材料
- [ ] 加载文本材料: `python -m src.agent.main tutor examples/materials/linear_programming.txt`
- [ ] 提问: "什么是线性规划？"
- [ ] 提问: "单纯形法的步骤是什么？"
- [ ] 提问: "如何用 Python 求解？"

### PDF 材料（如果有）
- [ ] 创建示例 PDF: `python examples/create_sample_pdf.py`
- [ ] 加载 PDF: `python -m src.agent.main tutor examples/materials/optimization_guide.pdf`
- [ ] 提问: "第二章讲了什么？"
- [ ] 提问: "如何实现单纯形法？"

### 工具调用验证
- [ ] 观察日志中的工具调用（绿色 [TOOL:xxx]）
- [ ] 验证 keyword_search 被调用
- [ ] 验证 semantic_search 被调用
- [ ] 验证返回了相关内容

## 🔍 Solver 模式测试

### 线性规划
- [ ] 启动 solver: `python -m src.agent.main solver`
- [ ] 输入问题: "最大化 z = 3x + 2y，约束：x + y <= 4, x >= 0, y >= 0"
- [ ] 验证生成了代码
- [ ] 验证代码执行成功
- [ ] 验证返回了结果

### 整数规划
- [ ] 输入背包问题
- [ ] 验证识别为整数规划
- [ ] 验证生成了正确的代码

### 非线性规划
- [ ] 输入非线性优化问题
- [ ] 验证使用了正确的求解器
- [ ] 验证返回了结果

## 🛠️ 工具功能测试

### PDF Processor
```python
from src.utils.pdf_processor import PDFProcessor

processor = PDFProcessor()
# [ ] 加载文本文件
# [ ] 验证分块正确
# [ ] 测试关键词搜索
# [ ] 测试页面内容获取
```

### Vector Store
```python
from src.utils.vector_store import VectorStore

store = VectorStore()
# [ ] 添加文本块
# [ ] 生成 embeddings
# [ ] 测试语义搜索
# [ ] 验证相似度计算
```

### Material Manager
```python
from src.utils.material_tools import get_material_manager

manager = get_material_manager()
# [ ] 加载材料
# [ ] 关键词搜索
# [ ] 语义搜索
# [ ] 获取页面内容
# [ ] 获取文本块
```

## 📖 文档验证

- [ ] README.md 清晰易懂
- [ ] QUICKSTART.md 可以快速上手
- [ ] docs/TUTOR_GUIDE.md 详细完整
- [ ] docs/PDF_RETRIEVAL.md 技术准确
- [ ] PROJECT_STRUCTURE.md 结构清晰
- [ ] 所有示例代码可运行

## 🎯 示例代码测试

- [ ] `examples/tutor_example.py` 运行成功
- [ ] `examples/solver_example.py` 运行成功
- [ ] `examples/test_pdf_tutor.py` 运行成功
- [ ] `examples/create_sample_pdf.py` 创建 PDF 成功

## 🚀 快速启动脚本

- [ ] `./run_tutor.sh examples/materials/linear_programming.txt` 工作正常
- [ ] `./run_solver.sh` 工作正常

## 🔧 配置验证

- [ ] `src/agent/config.yaml` 格式正确
- [ ] tutor agent 配置正确
- [ ] solver agent 配置正确
- [ ] code_executor agent 配置正确
- [ ] 环境变量正确展开

## 📊 性能测试

### 材料加载
- [ ] 小文本文件 (< 10KB): < 1 秒
- [ ] 大文本文件 (100KB): < 3 秒
- [ ] 小 PDF (< 10 页): < 5 秒
- [ ] 中 PDF (10-50 页): < 15 秒

### 检索性能
- [ ] 关键词搜索: < 0.1 秒
- [ ] 语义搜索: < 3 秒
- [ ] 多轮对话: < 5 秒/轮

### 求解性能
- [ ] 简单 LP: < 10 秒
- [ ] 复杂优化: < 30 秒

## 🐛 错误处理测试

### Tutor 模式
- [ ] 材料文件不存在 → 友好错误提示
- [ ] PDF 无法解析 → 错误提示
- [ ] 找不到相关内容 → 提示尝试其他关键词
- [ ] API 错误 → 显示错误信息

### Solver 模式
- [ ] 代码执行失败 → 自动修复
- [ ] 修复失败 → 显示错误信息
- [ ] 问题描述不清 → 提示补充信息

## 🔒 安全性检查

- [ ] `.env` 文件在 `.gitignore` 中
- [ ] API key 不在代码中硬编码
- [ ] 临时文件正确清理
- [ ] 代码执行有超时限制

## 📱 用户体验

- [ ] 日志输出清晰（彩色）
- [ ] 进度提示明确
- [ ] 错误信息友好
- [ ] 结果格式化良好

## 🌐 兼容性

- [ ] Python 3.10+ 运行正常
- [ ] macOS 测试通过
- [ ] Linux 测试通过（如适用）
- [ ] Windows 测试通过（如适用）

## 📦 依赖检查

- [ ] 所有依赖在 requirements.txt 中
- [ ] 版本号合理
- [ ] 没有冲突的依赖
- [ ] 可选依赖标注清楚

## 🎨 代码质量

- [ ] 没有语法错误
- [ ] 类型注解完整
- [ ] 文档字符串清晰
- [ ] 代码格式一致
- [ ] 没有未使用的导入

## 📈 扩展性验证

- [ ] 可以轻松添加新工具
- [ ] 可以支持新文件格式
- [ ] 可以添加新 agent
- [ ] 配置灵活可调

## ✅ 最终检查

- [ ] 所有测试通过
- [ ] 文档完整
- [ ] 示例可运行
- [ ] 性能可接受
- [ ] 用户体验良好

---

## 使用说明

### 快速验证（5 分钟）
```bash
# 1. 安装
pip install -r requirements.txt

# 2. 配置
echo "GOOGLE_API_KEY=your_key" > .env

# 3. 测试
python demo.py
```

### 完整验证（30 分钟）
按照上述清单逐项测试

### 问题报告
如果发现问题，请记录：
- 问题描述
- 复现步骤
- 错误信息
- 环境信息（Python 版本、OS 等）

---

**最后更新**: 2024-12-10
