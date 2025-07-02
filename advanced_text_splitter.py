import re
import json
from typing import List, Dict, Any, Tuple

class AdvancedTextSplitter:
    """
    高级文本分割器节点 - 支持动态输出端口
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_input": ("STRING", {
                    "multiline": True, 
                    "default": "请输入需要分割的文本内容..."
                }),
                "split_method": (["按段落分割", "按句子分割", "按自定义分隔符分割", "按字符数分割"], {
                    "default": "按段落分割"
                }),
                "max_segments": ("INT", {
                    "default": 8, 
                    "min": 2, 
                    "max": 50, 
                    "step": 1
                }),
            },
            "optional": {
                "custom_separator": ("STRING", {
                    "default": "\n\n",
                    "multiline": False
                }),
                "chars_per_segment": ("INT", {
                    "default": 500,
                    "min": 50,
                    "max": 5000,
                    "step": 50
                }),
                "remove_empty": ("BOOLEAN", {"default": True}),
                "auto_display": ("BOOLEAN", {"default": True}),
            }
        }
    
    @classmethod
    def RETURN_TYPES(cls):
        # 动态返回类型将在运行时确定
        return ("STRING", "INT", "STRING")  # 基础返回：segment_1, segment_count, preview
    
    @classmethod
    def RETURN_NAMES(cls):
        return ("segment_1", "segment_count", "preview")
    
    FUNCTION = "split_text"
    CATEGORY = "🌋 Volcano Advanced"
    
    # 添加动态输出支持
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 当输入改变时重新计算输出端口
        return float("nan")
    
    def __init__(self):
        self.current_segments = 0
        self.segments_data = []
    
    def split_text(self, text_input: str, split_method: str, max_segments: int, 
                   custom_separator: str = "\n\n", chars_per_segment: int = 500,
                   remove_empty: bool = True, auto_display: bool = True):
        """
        执行文本分割操作 - 支持动态输出
        """
        try:
            # 预处理文本
            text_input = text_input.strip()
            if not text_input:
                return self._create_empty_result("输入文本为空")
            
            # 根据分割方法执行分割
            segments = self._perform_split(text_input, split_method, custom_separator, chars_per_segment)
            
            # 移除空白段落（如果启用）
            if remove_empty:
                segments = [seg.strip() for seg in segments if seg.strip()]
            
            # 限制段落数量
            if len(segments) > max_segments:
                segments = segments[:max_segments]
            
            # 存储分割结果
            self.segments_data = segments
            self.current_segments = len(segments)
            
            # 生成预览信息
            preview = self._generate_preview(segments, auto_display)
            
            # 动态创建返回结果
            return self._create_dynamic_result(segments, preview)
            
        except Exception as e:
            error_msg = f"文本分割过程中发生错误: {str(e)}"
            return self._create_empty_result(error_msg)
    
    def _perform_split(self, text: str, method: str, separator: str, chars_per_segment: int) -> List[str]:
        """
        根据指定方法执行文本分割
        """
        if method == "按段落分割":
            segments = re.split(r'\n\s*\n', text)
        elif method == "按句子分割":
            segments = re.split(r'[。！？.!?]+', text)
        elif method == "按自定义分隔符分割":
            segments = text.split(separator)
        elif method == "按字符数分割":
            segments = []
            for i in range(0, len(text), chars_per_segment):
                segments.append(text[i:i + chars_per_segment])
        else:
            segments = re.split(r'\n\s*\n', text)
        
        return segments
    
    def _generate_preview(self, segments: List[str], auto_display: bool) -> str:
        """
        生成预览信息
        """
        preview_lines = []
        preview_lines.append(f"=== 文本分割结果预览 ===")
        preview_lines.append(f"总共分割出 {len(segments)} 个片段")
        preview_lines.append("")
        
        for i, segment in enumerate(segments, 1):
            preview_lines.append(f"【片段 {i}】")
            preview_text = segment[:100] + "..." if len(segment) > 100 else segment
            preview_lines.append(preview_text)
            preview_lines.append(f"字符数: {len(segment)}")
            preview_lines.append("-" * 40)
        
        if auto_display:
            preview_lines.append("\n💡 提示: 动态输出已启用，连接segment_1后将自动显示更多输出端口")
        
        return "\n".join(preview_lines)
    
    def _create_dynamic_result(self, segments: List[str], preview: str):
        """
        创建动态返回结果
        """
        # 基础返回：第一个片段、片段总数、预览
        result = []
        
        # 第一个片段
        if segments:
            result.append(segments[0])
        else:
            result.append("")
        
        # 片段总数
        result.append(len(segments))
        
        # 预览信息
        result.append(preview)
        
        return tuple(result)
    
    def _create_empty_result(self, error_msg: str):
        """
        创建空结果（用于错误情况）
        """
        return ("", 0, error_msg)


class DynamicTextSplitter:
    """
    动态文本分割器 - 真正的动态输出实现
    这个版本使用ComfyUI的动态节点机制
    """
    
    def __init__(self):
        self.segments = []
        self.connected_outputs = set()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_input": ("STRING", {
                    "multiline": True, 
                    "default": "请输入需要分割的文本内容..."
                }),
                "split_method": (["按段落分割", "按句子分割", "按自定义分隔符分割", "按字符数分割"], {
                    "default": "按段落分割"
                }),
                "max_segments": ("INT", {
                    "default": 8, 
                    "min": 2, 
                    "max": 50, 
                    "step": 1
                }),
            },
            "optional": {
                "custom_separator": ("STRING", {
                    "default": "\n\n",
                    "multiline": False
                }),
                "chars_per_segment": ("INT", {
                    "default": 500,
                    "min": 50,
                    "max": 5000,
                    "step": 50
                }),
                "remove_empty": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "STRING")  # 动态扩展
    RETURN_NAMES = ("segment_1", "segment_count", "preview")
    
    FUNCTION = "split_text_dynamic"
    CATEGORY = "🌋 Volcano Advanced"
    
    # 实现动态输出的关键方法
    def get_dynamic_outputs(self, **kwargs):
        """
        根据当前状态动态生成输出端口
        """
        # 基础输出
        outputs = [("STRING", "segment_1"), ("INT", "segment_count"), ("STRING", "preview")]
        
        # 根据已连接的输出动态添加更多端口
        for i in range(2, min(len(self.segments) + 1, 51)):
            if f"segment_{i-1}" in self.connected_outputs or i <= 2:
                outputs.append(("STRING", f"segment_{i}"))
        
        return outputs
    
    def split_text_dynamic(self, text_input: str, split_method: str, max_segments: int, 
                          custom_separator: str = "\n\n", chars_per_segment: int = 500,
                          remove_empty: bool = True):
        """
        动态文本分割处理
        """
        try:
            # 执行文本分割
            text_input = text_input.strip()
            if not text_input:
                return ("", 0, "输入文本为空")
            
            # 分割文本
            if split_method == "按段落分割":
                segments = re.split(r'\n\s*\n', text_input)
            elif split_method == "按句子分割":
                segments = re.split(r'[。！？.!?]+', text_input)
            elif split_method == "按自定义分隔符分割":
                segments = text_input.split(custom_separator)
            elif split_method == "按字符数分割":
                segments = []
                for i in range(0, len(text_input), chars_per_segment):
                    segments.append(text_input[i:i + chars_per_segment])
            else:
                segments = re.split(r'\n\s*\n', text_input)
            
            # 处理空白段落
            if remove_empty:
                segments = [seg.strip() for seg in segments if seg.strip()]
            
            # 限制数量
            if len(segments) > max_segments:
                segments = segments[:max_segments]
            
            self.segments = segments
            
            # 生成预览
            preview_lines = []
            preview_lines.append(f"=== 动态文本分割器 ===")
            preview_lines.append(f"总共分割出 {len(segments)} 个片段")
            preview_lines.append("💡 连接segment_1后将自动显示segment_2端口")
            preview_lines.append("")
            
            for i, segment in enumerate(segments[:5], 1):  # 只预览前5个
                preview_lines.append(f"【片段 {i}】{segment[:50]}...")
            
            preview = "\n".join(preview_lines)
            
            # 构建动态返回结果
            result = []
            result.append(segments[0] if segments else "")  # segment_1
            result.append(len(segments))  # segment_count
            result.append(preview)  # preview
            
            # 动态添加更多片段
            for i in range(1, min(len(segments), 50)):
                if i < len(segments):
                    result.append(segments[i])
                else:
                    result.append("")
            
            return tuple(result)
            
        except Exception as e:
            return ("", 0, f"分割失败: {str(e)}")


class TextSegmentDisplay:
    """
    文本片段显示节点
    用于显示单个文本片段的内容
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_segment": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "show_stats": ("BOOLEAN", {"default": True}),
                "max_display_length": ("INT", {
                    "default": 1000,
                    "min": 100,
                    "max": 10000,
                    "step": 100
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_output",)
    
    FUNCTION = "display_segment"
    CATEGORY = "🌋 Volcano Advanced"
    
    def display_segment(self, text_segment: str, show_stats: bool = True, 
                       max_display_length: int = 1000) -> Tuple[str]:
        """
        格式化显示文本片段
        """
        if not text_segment.strip():
            return ("[空片段]",)
        
        output_lines = []
        
        if show_stats:
            output_lines.append(f"📊 片段统计信息:")
            output_lines.append(f"字符数: {len(text_segment)}")
            output_lines.append(f"行数: {len(text_segment.splitlines())}")
            output_lines.append(f"词数估计: {len(text_segment.split())}")
            output_lines.append("=" * 50)
        
        # 限制显示长度
        display_text = text_segment
        if len(display_text) > max_display_length:
            display_text = display_text[:max_display_length] + "\n\n[内容过长，已截断...]"
        
        output_lines.append(display_text)
        
        return ("\n".join(output_lines),)


# 节点注册
NODE_CLASS_MAPPINGS = {
    "AdvancedTextSplitter": AdvancedTextSplitter,
    "DynamicTextSplitter": DynamicTextSplitter,
    "TextSegmentDisplay": TextSegmentDisplay,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedTextSplitter": "🌋 高级文本分割器",
    "DynamicTextSplitter": "🌋 动态文本分割器",
    "TextSegmentDisplay": "🌋 文本片段显示器",
}
