"""
向量存储和检索工具
使用 Gemini Embedding 进行语义搜索
"""

from typing import List, Dict, Optional
import numpy as np
from dataclasses import dataclass
from .pdf_processor import TextChunk


@dataclass
class VectorChunk:
    """带向量的文本块"""
    chunk: TextChunk
    embedding: np.ndarray


class VectorStore:
    """向量存储"""
    
    def __init__(self, embedding_model: str = "models/text-embedding-004"):
        """
        初始化向量存储
        
        Args:
            embedding_model: Gemini embedding 模型名称
        """
        self.embedding_model = embedding_model
        self.vector_chunks: List[VectorChunk] = []
        self._client = None
    
    def _get_client(self):
        """延迟初始化 Gemini client"""
        if self._client is None:
            import os
            from google import genai
            self._client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        return self._client
    
    def add_chunks(self, chunks: List[TextChunk]) -> None:
        """
        添加文本块并生成 embedding
        
        Args:
            chunks: 文本块列表
        """
        client = self._get_client()
        
        for chunk in chunks:
            try:
                # 生成 embedding - 使用正确的 API 格式
                result = client.models.embed_content(
                    model=self.embedding_model,
                    contents=chunk.content  # 注意：是 contents 不是 content
                )
                
                embedding = np.array(result.embeddings[0].values)
                
                self.vector_chunks.append(VectorChunk(
                    chunk=chunk,
                    embedding=embedding
                ))
                
            except Exception as e:
                print(f"Warning: Failed to embed chunk {chunk.chunk_id}: {e}")
                continue
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[TextChunk]:
        """
        语义搜索
        
        Args:
            query: 搜索查询
            top_k: 返回前 k 个结果
            
        Returns:
            最相关的文本块列表
        """
        if not self.vector_chunks:
            return []
        
        client = self._get_client()
        
        try:
            # 生成查询的 embedding - 使用正确的 API 格式
            result = client.models.embed_content(
                model=self.embedding_model,
                contents=query  # 注意：是 contents 不是 content
            )
            query_embedding = np.array(result.embeddings[0].values)
            
            # 计算余弦相似度
            similarities = []
            for vec_chunk in self.vector_chunks:
                similarity = self._cosine_similarity(query_embedding, vec_chunk.embedding)
                similarities.append((similarity, vec_chunk.chunk))
            
            # 排序并返回 top_k
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            return [chunk for _, chunk in similarities[:top_k]]
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """
        计算余弦相似度
        
        Args:
            a: 向量 a
            b: 向量 b
            
        Returns:
            余弦相似度
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def clear(self) -> None:
        """清空向量存储"""
        self.vector_chunks = []
