"""
对话记录工具
保存 Tutor 模式的问答历史为 Markdown 格式
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json


class ConversationLogger:
    """对话记录器"""
    
    def __init__(self, session_id: Optional[str] = None, output_dir: str = "conversations"):
        """
        初始化对话记录器
        
        Args:
            session_id: 会话 ID，如果为 None 则自动生成
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 生成会话 ID
        if session_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = f"session_{timestamp}"
        
        self.session_id = session_id
        self.session_dir = self.output_dir / session_id
        self.session_dir.mkdir(exist_ok=True)
        
        # 图片目录
        self.images_dir = self.session_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        # 对话历史
        self.conversation_history: List[Dict] = []
        
        # Markdown 文件路径
        self.markdown_file = self.session_dir / "conversation.md"
        
        # 初始化 Markdown 文件
        self._init_markdown_file()
    
    def _init_markdown_file(self):
        """初始化 Markdown 文件"""
        header = f"""# Math Tutor Conversation

**Session ID:** {self.session_id}  
**Start Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""
        with open(self.markdown_file, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def log_question(self, question: str):
        """
        记录学生问题
        
        Args:
            question: 学生的问题
        """
        entry = {
            "role": "student",
            "content": question,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(entry)
        
        # 追加到 Markdown
        with open(self.markdown_file, 'a', encoding='utf-8') as f:
            f.write(f"## 🎓 Student Question\n\n")
            f.write(f"{question}\n\n")
            f.write(f"*Time: {datetime.now().strftime('%H:%M:%S')}*\n\n")
    
    def log_answer(self, answer: str, images: Optional[List[str]] = None):
        """
        记录 Tutor 回答
        
        Args:
            answer: Tutor 的回答（Markdown 格式）
            images: 生成的图片路径列表
        """
        entry = {
            "role": "tutor",
            "content": answer,
            "images": images or [],
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(entry)
        
        # 追加到 Markdown
        with open(self.markdown_file, 'a', encoding='utf-8') as f:
            f.write(f"## 📚 Tutor Answer\n\n")
            f.write(f"{answer}\n\n")
            
            # 添加图片引用
            if images:
                f.write(f"### Generated Images\n\n")
                for img_path in images:
                    # 使用相对路径
                    rel_path = Path(img_path).relative_to(self.session_dir)
                    f.write(f"![Generated Image]({rel_path})\n\n")
            
            f.write(f"*Time: {datetime.now().strftime('%H:%M:%S')}*\n\n")
            f.write("---\n\n")
    
    def save_image(self, image, description: str = "") -> str:
        """
        保存生成的图片
        
        Args:
            image: PIL Image 对象
            description: 图片描述（用于文件名）
        
        Returns:
            保存的图片路径
        """
        from PIL import Image
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_desc = "".join(c if c.isalnum() else "_" for c in description)[:50]
        filename = f"{timestamp}_{safe_desc}.png" if safe_desc else f"{timestamp}.png"
        
        image_path = self.images_dir / filename
        
        # 保存图片
        if isinstance(image, Image.Image):
            image.save(image_path, format='PNG')
        else:
            raise ValueError("Image must be a PIL Image object")
        
        return str(image_path)
    
    def get_session_summary(self) -> Dict:
        """
        获取会话摘要
        
        Returns:
            包含会话统计信息的字典
        """
        return {
            "session_id": self.session_id,
            "total_exchanges": len([e for e in self.conversation_history if e["role"] == "student"]),
            "total_images": sum(len(e.get("images", [])) for e in self.conversation_history),
            "markdown_file": str(self.markdown_file),
            "session_dir": str(self.session_dir)
        }
    
    def export_json(self):
        """导出对话历史为 JSON"""
        json_file = self.session_dir / "conversation.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": self.session_id,
                "conversation": self.conversation_history
            }, f, ensure_ascii=False, indent=2)
        
        return str(json_file)


# 全局会话记录器
_current_logger: Optional[ConversationLogger] = None


def get_conversation_logger(session_id: Optional[str] = None) -> ConversationLogger:
    """
    获取当前会话的对话记录器
    
    Args:
        session_id: 会话 ID，如果为 None 则使用当前记录器或创建新的
    
    Returns:
        ConversationLogger 实例
    """
    global _current_logger
    
    if session_id is not None or _current_logger is None:
        _current_logger = ConversationLogger(session_id=session_id)
    
    return _current_logger


def reset_conversation_logger():
    """重置对话记录器（开始新会话）"""
    global _current_logger
    _current_logger = None
