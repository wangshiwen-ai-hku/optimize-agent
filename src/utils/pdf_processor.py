"""
PDF 处理工具
支持 PDF 文本提取、分块和索引
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    """文本块"""
    content: str
    page_num: int
    chunk_id: int
    metadata: Dict = None


class PDFProcessor:
    """PDF 处理器"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        初始化 PDF 处理器
        
        Args:
            chunk_size: 每个文本块的字符数
            chunk_overlap: 文本块之间的重叠字符数
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: List[TextChunk] = []
        self.full_text: str = ""
        
    def load_pdf(self, pdf_path: str | Path) -> str:
        """
        加载 PDF 文件并提取文本
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            提取的全文
        """
        try:
            import PyPDF2
            
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            text_by_page = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()
                    if text.strip():
                        text_by_page.append((page_num, text))
            
            # 创建文本块
            self.chunks = self._create_chunks(text_by_page)
            self.full_text = "\n\n".join([text for _, text in text_by_page])
            
            return self.full_text
            
        except ImportError:
            raise ImportError("PyPDF2 is required. Install it with: pip install PyPDF2")
    
    def _create_chunks(self, text_by_page: List[Tuple[int, str]]) -> List[TextChunk]:
        """
        将文本分块
        
        Args:
            text_by_page: (页码, 文本) 列表
            
        Returns:
            文本块列表
        """
        chunks = []
        chunk_id = 0
        
        for page_num, page_text in text_by_page:
            # 按段落分割
            paragraphs = page_text.split('\n\n')
            
            current_chunk = ""
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # 如果当前块加上新段落超过大小限制
                if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                    # 保存当前块
                    chunks.append(TextChunk(
                        content=current_chunk.strip(),
                        page_num=page_num,
                        chunk_id=chunk_id,
                        metadata={"source": "pdf"}
                    ))
                    chunk_id += 1
                    
                    # 保留重叠部分
                    if self.chunk_overlap > 0:
                        overlap_text = current_chunk[-self.chunk_overlap:]
                        current_chunk = overlap_text + "\n\n" + para
                    else:
                        current_chunk = para
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
            
            # 保存页面最后的块
            if current_chunk.strip():
                chunks.append(TextChunk(
                    content=current_chunk.strip(),
                    page_num=page_num,
                    chunk_id=chunk_id,
                    metadata={"source": "pdf"}
                ))
                chunk_id += 1
        
        return chunks
    
    def keyword_search(self, query: str, top_k: int = 5) -> List[TextChunk]:
        """
        关键词搜索
        
        Args:
            query: 搜索查询
            top_k: 返回前 k 个结果
            
        Returns:
            匹配的文本块列表
        """
        query_lower = query.lower()
        query_terms = set(re.findall(r'\w+', query_lower))
        
        # 计算每个块的相关性分数
        scored_chunks = []
        for chunk in self.chunks:
            content_lower = chunk.content.lower()
            
            # 计算匹配的关键词数量
            chunk_terms = set(re.findall(r'\w+', content_lower))
            matching_terms = query_terms & chunk_terms
            
            # 计算分数：匹配词数 + 完整查询出现次数 * 10
            score = len(matching_terms)
            score += content_lower.count(query_lower) * 10
            
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # 按分数排序
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        return [chunk for _, chunk in scored_chunks[:top_k]]
    
    def get_page_content(self, page_num: int) -> str:
        """
        获取指定页面的内容
        
        Args:
            page_num: 页码
            
        Returns:
            页面内容
        """
        page_chunks = [chunk for chunk in self.chunks if chunk.page_num == page_num]
        return "\n\n".join([chunk.content for chunk in page_chunks])
    
    def get_chunk_by_id(self, chunk_id: int) -> Optional[TextChunk]:
        """
        根据 ID 获取文本块
        
        Args:
            chunk_id: 块 ID
            
        Returns:
            文本块
        """
        for chunk in self.chunks:
            if chunk.chunk_id == chunk_id:
                return chunk
        return None
    
    def get_summary(self) -> Dict:
        """
        获取 PDF 摘要信息
        
        Returns:
            摘要信息字典
        """
        pages = set(chunk.page_num for chunk in self.chunks)
        
        return {
            "total_chunks": len(self.chunks),
            "total_pages": len(pages),
            "total_characters": len(self.full_text),
            "avg_chunk_size": sum(len(c.content) for c in self.chunks) // len(self.chunks) if self.chunks else 0
        }
