from .volcano_api import VolcanoLLMLoader, VolcanoLLMPrompt, VolcanoMultiModalInput

NODE_CLASS_MAPPINGS = {
    "VolcanoLLMLoader": VolcanoLLMLoader,
    "VolcanoLLMPrompt": VolcanoLLMPrompt,
    "VolcanoMultiModalInput": VolcanoMultiModalInput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VolcanoLLMLoader": "🌋 Volcano LLM Loader",
    "VolcanoLLMPrompt": "🌋 Volcano Text Prompt",
    "VolcanoMultiModalInput": "🌋 Volcano MultiModal",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
