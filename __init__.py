from .volcano_api import VolcanoLLMLoader, VolcanoLLMPrompt

NODE_CLASS_MAPPINGS = {
    "VolcanoLLMLoader": VolcanoLLMLoader,
    "VolcanoLLMPrompt": VolcanoLLMPrompt
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VolcanoLLMLoader": "Volcano LLM Loader",
    "VolcanoLLMPrompt": "Volcano LLM Prompt"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']