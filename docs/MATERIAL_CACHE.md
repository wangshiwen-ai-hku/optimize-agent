# 材料缓存机制

## 概述

为了提高性能，Tutor 模式现在支持材料缓存。同一个材料文件只需要加载一次，后续的问题会直接使用缓存的数据，大大提升响应速度。

## 工作原理

### 缓存机制

1. **首次加载**：第一次加载材料时，系统会：
   - 读取文件内容
   - 分块处理
   - 创建向量索引
   - 存储到内存缓存

2. **后续使用**：再次使用同一材料时，系统会：
   - 检测到材料已缓存
   - 直接使用内存中的数据
   - 跳过文件读取和处理步骤

3. **缓存标识**：使用文件的绝对路径作为缓存 key，确保唯一性

## 性能提升

### 典型场景

**首次加载**（无缓存）：
```
Loading material: linear_programming.txt
- Reading file: ~50ms
- Chunking: ~100ms
- Creating vectors: ~200ms
Total: ~350ms
```

**后续加载**（使用缓存）：
```
Using cached material: linear_programming.txt
- Cache lookup: ~1ms
Total: ~1ms
```

**性能提升**：约 350 倍！

### 实际效果

在交互式会话中：
```bash
Your question: 什么是线性规划？
🤔 Thinking...
✓ Loaded material: linear_programming.txt (350ms)
📚 Tutor: [回答]

Your question: 线性规划有哪些应用？
🤔 Thinking...
✓ Using cached material: linear_programming.txt (1ms)
📚 Tutor: [回答]
```

第二个问题几乎瞬间开始处理！

## 使用方法

### 自动缓存（默认）

缓存是自动启用的，无需任何配置：

```bash
./run_tutor.sh examples/materials/linear_programming.txt
```

第一个问题会加载材料，后续问题自动使用缓存。

### Python API

```python
from src.utils.material_tools import MaterialManager

manager = MaterialManager()

# 首次加载
info = manager.load_material("material.pdf")
print(f"Cached: {info['cached']}")  # False

# 再次加载（使用缓存）
info = manager.load_material("material.pdf")
print(f"Cached: {info['cached']}")  # True

# 强制重新加载
info = manager.load_material("material.pdf", force_reload=True)
print(f"Cached: {info['cached']}")  # False
```

### 检查缓存状态

```python
# 检查材料是否已加载
if manager.is_material_loaded("material.pdf"):
    print("Material is cached")

# 获取所有已加载的材料
loaded = manager.get_loaded_materials()
print(f"Cached materials: {len(loaded)}")
```

### 清除缓存

```python
# 清除特定材料
manager.clear_cache("material.pdf")

# 清除所有缓存
manager.clear_cache()
```

## 缓存生命周期

### 会话内缓存

缓存在整个 Python 进程生命周期内有效：

```bash
# 启动 Tutor
./run_tutor.sh material1.pdf material2.pdf

Your question: 关于 material1 的问题
# material1 被加载并缓存

Your question: 关于 material2 的问题
# material2 被加载并缓存

Your question: 再问 material1 的问题
# 使用 material1 的缓存

Your question: exit
# 退出后缓存清除
```

### 多材料缓存

可以同时缓存多个材料：

```python
manager = MaterialManager()

# 加载多个材料
manager.load_material("material1.pdf")
manager.load_material("material2.pdf")
manager.load_material("material3.txt")

# 所有材料都被缓存
print(manager.get_loaded_materials())
# ['material1.pdf', 'material2.pdf', 'material3.txt']
```

## 内存管理

### 内存占用

每个缓存的材料占用内存：
- **文本内容**：原始大小
- **分块数据**：约 1.2x 原始大小
- **向量索引**：约 0.5x 原始大小

**总计**：约 2.7x 原始文件大小

### 示例

| 文件大小 | 缓存占用 | 说明 |
|---------|---------|------|
| 100 KB | ~270 KB | 小文件 |
| 1 MB | ~2.7 MB | 中等文件 |
| 10 MB | ~27 MB | 大文件 |

### 内存优化建议

1. **小文件**（< 1MB）：可以缓存多个，无需担心
2. **中等文件**（1-10MB）：建议缓存 5-10 个
3. **大文件**（> 10MB）：建议缓存 2-3 个

如果内存不足，可以手动清除不需要的缓存：

```python
# 清除不常用的材料
manager.clear_cache("old_material.pdf")
```

## 缓存失效

### 自动失效

缓存在以下情况下自动失效：
- Python 进程退出
- 调用 `clear_cache()`

### 不会失效

缓存在以下情况下**不会**失效：
- 文件内容修改（需要手动重新加载）
- 文件移动或重命名（使用绝对路径）

### 强制重新加载

如果文件内容已修改，需要强制重新加载：

```python
# 强制重新加载
info = manager.load_material("material.pdf", force_reload=True)
```

或者清除缓存后重新加载：

```python
manager.clear_cache("material.pdf")
info = manager.load_material("material.pdf")
```

## 日志输出

### 首次加载

```
✓ Loaded material: linear_programming.txt
```

### 使用缓存

```
✓ Using cached material: linear_programming.txt
```

### 会话结束

```
Session Summary
============================================================
...
Cached materials: 2
  - linear_programming.txt
  - convex_optimization.pdf
```

## 测试缓存

运行测试脚本：

```bash
python test_material_cache.py
```

输出示例：

```
============================================================
Testing Material Cache
============================================================

1. First load (no cache):
   Loaded: linear_programming.txt
   Chunks: 15
   Cached: False
   Time: 0.3521s

2. Second load (with cache):
   Loaded: linear_programming.txt
   Chunks: 15
   Cached: True
   Time: 0.0001s

3. Performance comparison:
   ✅ Cache is 3521.0x faster!

4. Cache status:
   Is loaded: True
   Loaded materials: 1

5. Testing search with cached data:
   Found 2 results
   First result: 线性规划（Linear Programming）是一种优化方法...

6. Clearing cache:
   Is loaded: False
   Loaded materials: 0

7. Load after cache clear:
   Cached: False
   Time: 0.3498s

============================================================
✅ Cache test completed!
============================================================
```

## 最佳实践

### 1. 交互式会话

在交互式会话中，缓存会自动工作，无需任何操作：

```bash
./run_tutor.sh material.pdf
# 第一个问题：加载材料
# 后续问题：使用缓存
```

### 2. 批量处理

处理多个问题时，先加载所有材料：

```python
manager = MaterialManager()

# 预加载所有材料
for material in materials:
    manager.load_material(material)

# 处理问题（使用缓存）
for question in questions:
    answer = await run_tutor(question, materials)
```

### 3. 长时间运行

长时间运行时，定期检查内存使用：

```python
import psutil

# 检查内存使用
process = psutil.Process()
memory_mb = process.memory_info().rss / 1024 / 1024

if memory_mb > 1000:  # 超过 1GB
    # 清除部分缓存
    manager.clear_cache(old_material)
```

### 4. 开发调试

开发时，如果修改了材料文件，记得强制重新加载：

```python
# 开发模式：总是重新加载
info = manager.load_material("material.pdf", force_reload=True)
```

## 故障排除

### 问题：缓存没有生效

**症状**：每次都显示 "Loaded material" 而不是 "Using cached material"

**原因**：
1. 文件路径不同（相对路径 vs 绝对路径）
2. 缓存被清除
3. 使用了不同的 MaterialManager 实例

**解决**：
```python
# 使用全局单例
from src.utils.material_tools import get_material_manager
manager = get_material_manager()
```

### 问题：内存占用过高

**症状**：Python 进程占用大量内存

**原因**：缓存了太多大文件

**解决**：
```python
# 清除不需要的缓存
manager.clear_cache()

# 或只保留当前需要的
manager.clear_cache(old_material)
```

### 问题：文件修改后内容没更新

**症状**：修改了材料文件，但 Tutor 还是返回旧内容

**原因**：使用了缓存的旧数据

**解决**：
```python
# 强制重新加载
manager.load_material("material.pdf", force_reload=True)
```

## API 参考

### MaterialManager

```python
class MaterialManager:
    def load_material(
        self, 
        material_path: str | Path,
        force_reload: bool = False
    ) -> Dict[str, Any]:
        """加载材料（带缓存）"""
    
    def is_material_loaded(
        self, 
        material_path: str | Path
    ) -> bool:
        """检查材料是否已加载"""
    
    def get_loaded_materials(self) -> List[str]:
        """获取所有已加载的材料列表"""
    
    def clear_cache(
        self, 
        material_path: Optional[str | Path] = None
    ):
        """清除缓存"""
```

### 返回值

```python
{
    'file_name': 'material.pdf',
    'file_type': 'pdf',
    'total_pages': 10,
    'total_chunks': 50,
    'cached': True  # 是否使用了缓存
}
```

## 总结

材料缓存机制：
- ✅ 自动启用，无需配置
- ✅ 大幅提升性能（数百倍）
- ✅ 支持多材料缓存
- ✅ 内存占用可控
- ✅ 灵活的缓存管理

享受更快的 Tutor 体验！🚀
