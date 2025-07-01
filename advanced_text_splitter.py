import re
import json
from typing import List, Dict, Any, Tuple

class AdvancedTextSplitter:
    """
    高级文本分割器节点
    支持动态输出和自动显示功能
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
    
    RETURN_TYPES = tuple(["STRING"] * 50 + ["INT", "STRING"])  # 50个字符串输出 + 分割数量 + 预览
    RETURN_NAMES = tuple([f"segment_{i+1}" for i in range(50)] + ["segment_count", "preview"])
    
    FUNCTION = "split_text"
    CATEGORY = "🌋 Volcano Advanced"
    
    def split_text(self, text_input: str, split_method: str, max_segments: int, 
                   custom_separator: str = "\n\n", chars_per_segment: int = 500,
                   remove_empty: bool = True, auto_display: bool = True) -> Tuple:
        """
        执行文本分割操作
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
            
            # 生成预览信息
            preview = self._generate_preview(segments, auto_display)
            
            # 创建返回结果
            return self._create_result(segments, preview)
            
        except Exception as e:
            error_msg = f"文本分割过程中发生错误: {str(e)}"
            return self._create_empty_result(error_msg)
    
    def _perform_split(self, text: str, method: str, separator: str, chars_per_segment: int) -> List[str]:
        """
        根据指定方法执行文本分割
        """
        if method == "按段落分割":
            # 按段落分割（双换行符）
            segments = re.split(r'\n\s*\n', text)
        elif method == "按句子分割":
            # 按句子分割（句号、问号、感叹号）
            segments = re.split(r'[。！？.!?]+', text)
        elif method == "按自定义分隔符分割":
            # 按自定义分隔符分割
            segments = text.split(separator)
        elif method == "按字符数分割":
            # 按字符数分割
            segments = []
            for i in range(0, len(text), chars_per_segment):
                segments.append(text[i:i + chars_per_segment])
        else:
            # 默认按段落分割
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
            # 显示前100个字符作为预览
            preview_text = segment[:100] + "..." if len(segment) > 100 else segment
            preview_lines.append(preview_text)
            preview_lines.append(f"字符数: {len(segment)}")
            preview_lines.append("-" * 40)
        
        if auto_display:
            preview_lines.append("\n💡 提示: 已启用自动显示功能，各片段内容已输出到对应端口")
        
        return "\n".join(preview_lines)
    
    def _create_result(self, segments: List[str], preview: str) -> Tuple:
        """
        创建返回结果元组
        """
        # 创建50个输出槽位
        result = []
        
        # 填充实际的分割结果
        for i in range(50):
            if i < len(segments):
                result.append(segments[i])
            else:
                result.append("")  # 空字符串填充未使用的槽位
        
        # 添加分割数量和预览
        result.append(len(segments))  # segment_count
        result.append(preview)        # preview
        
        return tuple(result)
    
    def _create_empty_result(self, error_msg: str) -> Tuple:
        """
        创建空结果（用于错误情况）
        """
        result = [""] * 50  # 50个空字符串
        result.append(0)       # segment_count = 0
        result.append(error_msg)  # preview = error message
        return tuple(result)


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
    "TextSegmentDisplay": TextSegmentDisplay,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedTextSplitter": "🌋 高级文本分割器",
    "TextSegmentDisplay": "🌋 文本片段显示器",
}
