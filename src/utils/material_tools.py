"""
材料检索工具
为 LLM agent 提供可调用的工具函数
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .pdf_processor import PDFProcessor, TextChunk
from .vector_store import VectorStore


class MaterialManager:
    """材料管理器"""
    
    def __init__(self):
        self.pdf_processors: Dict[str, PDFProcessor] = {}
        self.vector_stores: Dict[str, VectorStore] = {}
        self.current_material: Optional[str] = None
    
    def load_material(self, material_path: str | Path, force_reload: bool = False) -> Dict[str, Any]:
        """
        加载材料文件（带缓存）
        
        Args:
            material_path: 材料文件路径
            force_reload: 是否强制重新加载（默认 False，使用缓存）
            
        Returns:
            加载结果信息
        """
        material_path = Path(material_path)
        material_key = str(material_path.absolute())  # 使用绝对路径作为 key
        
        # 检查缓存
        if not force_reload and material_key in self.pdf_processors:
            # 材料已加载，返回缓存的摘要信息
            self.current_material = material_key
            processor = self.pdf_processors[material_key]
            
            if material_path.suffix.lower() == '.pdf':
                summary = processor.get_summary()
                summary['file_name'] = material_path.name
                summary['file_type'] = 'pdf'
                summary['cached'] = True
                return summary
            else:
                return {
                    'file_name': material_path.name,
                    'file_type': material_path.suffix[1:],
                    'total_chunks': len(processor.chunks),
                    'total_characters': len(processor.full_text),
                    'cached': True
                }
        
        # 未缓存，需要加载
        if material_path.suffix.lower() == '.pdf':
            # 加载 PDF
            processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
            full_text = processor.load_pdf(material_path)
            
            # 创建向量存储
            vector_store = VectorStore()
            vector_store.add_chunks(processor.chunks)
            
            self.pdf_processors[material_key] = processor
            self.vector_stores[material_key] = vector_store
            self.current_material = material_key
            
            summary = processor.get_summary()
            summary['file_name'] = material_path.name
            summary['file_type'] = 'pdf'
            summary['cached'] = False
            
            return summary
        
        elif material_path.suffix.lower() in ['.txt', '.md']:
            # 加载文本文件
            with open(material_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单分块
            processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
            # 模拟单页 PDF
            processor.chunks = processor._create_chunks([(1, content)])
            processor.full_text = content
            
            # 创建向量存储
            vector_store = VectorStore()
            vector_store.add_chunks(processor.chunks)
            
            self.pdf_processors[material_key] = processor
            self.vector_stores[material_key] = vector_store
            self.current_material = material_key
            
            return {
                'file_name': material_path.name,
                'file_type': material_path.suffix[1:],
                'total_chunks': len(processor.chunks),
                'total_characters': len(content),
                'cached': False
            }
        
        else:
            raise ValueError(f"Unsupported file type: {material_path.suffix}")
    
    def keyword_search(self, query: str, top_k: int = 3, material_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        关键词搜索工具
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            material_key: 材料标识（None 则使用当前材料）
            
        Returns:
            搜索结果列表
        """
        material_key = material_key or self.current_material
        
        if not material_key or material_key not in self.pdf_processors:
            return []
        
        processor = self.pdf_processors[material_key]
        chunks = processor.keyword_search(query, top_k)
        
        return [self._chunk_to_dict(chunk) for chunk in chunks]
    
    def semantic_search(self, query: str, top_k: int = 3, material_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        语义搜索工具
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            material_key: 材料标识（None 则使用当前材料）
            
        Returns:
            搜索结果列表
        """
        material_key = material_key or self.current_material
        
        if not material_key or material_key not in self.vector_stores:
            return []
        
        vector_store = self.vector_stores[material_key]
        chunks = vector_store.semantic_search(query, top_k)
        
        return [self._chunk_to_dict(chunk) for chunk in chunks]
    
    def get_page_content(self, page_num: int, material_key: Optional[str] = None) -> str:
        """
        获取指定页面内容
        
        Args:
            page_num: 页码
            material_key: 材料标识（None 则使用当前材料）
            
        Returns:
            页面内容
        """
        material_key = material_key or self.current_material
        
        if not material_key or material_key not in self.pdf_processors:
            return ""
        
        processor = self.pdf_processors[material_key]
        return processor.get_page_content(page_num)
    
    def get_chunk_by_id(self, chunk_id: int, material_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取文本块
        
        Args:
            chunk_id: 块 ID
            material_key: 材料标识（None 则使用当前材料）
            
        Returns:
            文本块信息
        """
        material_key = material_key or self.current_material
        
        if not material_key or material_key not in self.pdf_processors:
            return None
        
        processor = self.pdf_processors[material_key]
        chunk = processor.get_chunk_by_id(chunk_id)
        
        return self._chunk_to_dict(chunk) if chunk else None
    
    def is_material_loaded(self, material_path: str | Path) -> bool:
        """
        检查材料是否已加载
        
        Args:
            material_path: 材料文件路径
            
        Returns:
            是否已加载
        """
        material_path = Path(material_path)
        material_key = str(material_path.absolute())
        return material_key in self.pdf_processors
    
    def get_loaded_materials(self) -> List[str]:
        """
        获取所有已加载的材料列表
        
        Returns:
            材料路径列表
        """
        return list(self.pdf_processors.keys())
    
    def clear_cache(self, material_path: Optional[str | Path] = None):
        """
        清除缓存
        
        Args:
            material_path: 要清除的材料路径（None 则清除所有）
        """
        if material_path is None:
            # 清除所有缓存
            self.pdf_processors.clear()
            self.vector_stores.clear()
            self.current_material = None
        else:
            # 清除指定材料
            material_path = Path(material_path)
            material_key = str(material_path.absolute())
            
            if material_key in self.pdf_processors:
                del self.pdf_processors[material_key]
            if material_key in self.vector_stores:
                del self.vector_stores[material_key]
            
            if self.current_material == material_key:
                # 如果清除的是当前材料，切换到其他材料或 None
                self.current_material = next(iter(self.pdf_processors.keys()), None)
    
    @staticmethod
    def _chunk_to_dict(chunk: TextChunk) -> Dict[str, Any]:
        """将 TextChunk 转换为字典"""
        return {
            'chunk_id': chunk.chunk_id,
            'page_num': chunk.page_num,
            'content': chunk.content,
            'preview': chunk.content[:200] + '...' if len(chunk.content) > 200 else chunk.content
        }


# 全局材料管理器实例
_material_manager: Optional[MaterialManager] = None


def get_material_manager() -> MaterialManager:
    """获取全局材料管理器实例"""
    global _material_manager
    if _material_manager is None:
        _material_manager = MaterialManager()
    return _material_manager
