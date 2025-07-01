from .volcano_api import VolcanoLLMLoader, VolcanoLLMPrompt, VolcanoMultiModalInput
from .advanced_text_splitter import AdvancedTextSplitter, TextSegmentDisplay

NODE_CLASS_MAPPINGS = {
    "VolcanoLLMLoader": VolcanoLLMLoader,
    "VolcanoLLMPrompt": VolcanoLLMPrompt,
    "VolcanoMultiModalInput": VolcanoMultiModalInput,
    "AdvancedTextSplitter": AdvancedTextSplitter,
    "TextSegmentDisplay": TextSegmentDisplay,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VolcanoLLMLoader": "🌋 Volcano LLM Loader",
    "VolcanoLLMPrompt": "🌋 Volcano Text Prompt",
    "VolcanoMultiModalInput": "🌋 Volcano MultiModal",
    "AdvancedTextSplitter": "🌋 高级文本分割器",
    "TextSegmentDisplay": "🌋 文本片段显示器",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
