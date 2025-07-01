import os
import json
import logging
import enum
import base64
from typing import Dict, Any, List, Tuple, Optional, Union
from io import BytesIO
from PIL import Image

import openai
import requests

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('VolcanoAPI')

# 定义 API 模式枚举
class APIMode(enum.Enum):
    OPENAPI = "OpenAPI"
    REST_API = "REST API"

# 定义内容类型枚举
class ContentType(enum.Enum):
    TEXT = "text"
    IMAGE = "image_url"
    VIDEO = "video_url"

class VolcanoChat:
    """
    火山引擎 LLM API 客户端类
    支持多模态输入输出
    """
    def __init__(self, api_mode: APIMode, base_url: str, api_key: str, endpoint_id: str = None):
        self.api_mode = api_mode
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.endpoint_id = endpoint_id
        
        # 如果是 OpenAPI 模式，初始化 OpenAI 客户端
        if api_mode == APIMode.OPENAPI:
            logger.info(f"初始化OpenAI客户端，使用base_url={self.base_url}")
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=self.base_url
            )
            logger.info("OpenAI客户端初始化完成")
        
        logger.info(f"初始化 VolcanoChat 客户端: base_url={base_url}, api_mode={api_mode.value}")

    def _encode_image(self, image_path_or_tensor):
        """将图片编码为base64格式"""
        try:
            if isinstance(image_path_or_tensor, str):
                # 文件路径
                with open(image_path_or_tensor, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            else:
                # ComfyUI tensor格式
                # 假设是PIL Image或numpy array
                if hasattr(image_path_or_tensor, 'save'):
                    # PIL Image
                    buffer = BytesIO()
                    image_path_or_tensor.save(buffer, format='PNG')
                    return base64.b64encode(buffer.getvalue()).decode('utf-8')
                else:
                    # numpy array或tensor，需要转换
                    import numpy as np
                    if hasattr(image_path_or_tensor, 'numpy'):
                        image_array = image_path_or_tensor.numpy()
                    else:
                        image_array = image_path_or_tensor
                    
                    # 确保数组在0-255范围内
                    if image_array.max() <= 1.0:
                        image_array = (image_array * 255).astype(np.uint8)
                    
                    # 转换为PIL Image
                    if len(image_array.shape) == 4:  # batch dimension
                        image_array = image_array[0]
                    if len(image_array.shape) == 3 and image_array.shape[0] in [1, 3, 4]:  # CHW format
                        image_array = np.transpose(image_array, (1, 2, 0))
                    
                    pil_image = Image.fromarray(image_array)
                    buffer = BytesIO()
                    pil_image.save(buffer, format='PNG')
                    return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"图片编码失败: {str(e)}")
            raise

    def _prepare_messages(self, content_list: List[Dict[str, Any]], system_prompt: str = ""):
        """准备多模态消息格式"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 构建用户消息内容
        user_content = []
        
        for content_item in content_list:
            content_type = content_item.get("type", "text")
            
            if content_type == "text":
                user_content.append({
                    "type": "text",
                    "text": content_item["content"]
                })
            elif content_type == "image":
                # 处理图片
                image_data = content_item["content"]
                if isinstance(image_data, str) and (image_data.startswith("http") or image_data.startswith("data:")):
                    # URL或base64格式
                    image_url = image_data
                else:
                    # 需要编码的图片
                    encoded_image = self._encode_image(image_data)
                    image_url = f"data:image/png;base64,{encoded_image}"
                
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })
            elif content_type == "video":
                # 处理视频（类似图片处理）
                video_data = content_item["content"]
                if isinstance(video_data, str) and video_data.startswith("http"):
                    video_url = video_data
                else:
                    # 对于本地视频文件，可能需要特殊处理
                    video_url = video_data  # 简化处理
                
                user_content.append({
                    "type": "video_url",
                    "video_url": {"url": video_url}
                })
        
        messages.append({"role": "user", "content": user_content})
        return messages

    def generate_multimodal(self, content_list: List[Dict[str, Any]], system_prompt: str = "", 
                           max_tokens: int = 1024, temperature: float = 0.7, top_p: float = 0.9,
                           model: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        多模态内容生成
        """
        try:
            messages = self._prepare_messages(content_list, system_prompt)
            
            if self.api_mode == APIMode.OPENAPI:
                # 使用OpenAI客户端
                model_name = self.endpoint_id or model
                if not model_name:
                    raise ValueError("OpenAPI模式需要在VolcanoLLMLoader中提供endpoint_id")
                
                logger.info(f"调用OpenAPI，模型: {model_name}")
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                
                generated_text = response.choices[0].message.content
                response_info = {
                    "finish_reason": response.choices[0].finish_reason,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            else:
                # REST API模式
                if not model:
                    raise ValueError("REST API模式需要提供model参数")
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                request_data = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p
                }
                
                url = f"{self.base_url}/chat/completions"
                logger.info(f"调用REST API: {url}")
                response = requests.post(url, headers=headers, json=request_data, timeout=30)
                response.raise_for_status()
                
                response_json = response.json()
                generated_text = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                response_info = {
                    "finish_reason": response_json.get("choices", [{}])[0].get("finish_reason", ""),
                    "usage": response_json.get("usage", {})
                }
            
            return generated_text, response_info
            
        except Exception as e:
            logger.error(f"多模态生成失败: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"HTTP状态码: {e.response.status_code}")
                logger.error(f"响应内容: {e.response.text}")
            raise RuntimeError(f"火山引擎API调用失败: {str(e)}")


class VolcanoLLMLoader:
    """
    火山引擎 LLM 加载器节点 - 简化版
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_mode": (["OpenAPI", "REST API"], {"default": "OpenAPI"}),
                "base_url": ("STRING", {"default": "https://ark.cn-beijing.volcengine.com/api/v3"}),
                "api_key": ("STRING", {"default": ""}),
            },
            "optional": {
                "endpoint_id": ("STRING", {"default": ""}),  # OpenAPI模式使用
            }
        }
    
    RETURN_TYPES = ("VOLCANO_CHAT",)
    RETURN_NAMES = ("chat",)
    FUNCTION = "load_model"
    CATEGORY = "🌋火山引擎/LLM"
    
    def load_model(self, api_mode: str, base_url: str, api_key: str, endpoint_id: str = ""):
        try:
            api_mode_enum = APIMode.OPENAPI if api_mode == "OpenAPI" else APIMode.REST_API
            
            # 验证必需参数
            if api_mode_enum == APIMode.OPENAPI and not endpoint_id:
                logger.warning("OpenAPI模式建议提供endpoint_id")
            
            # 创建客户端
            chat = VolcanoChat(
                api_mode=api_mode_enum,
                base_url=base_url,
                api_key=api_key,
                endpoint_id=endpoint_id if endpoint_id else None
            )
            
            logger.info(f"成功创建火山引擎客户端: {api_mode}, {base_url}")
            return (chat,)
            
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            raise RuntimeError(f"无法加载火山引擎模型: {str(e)}")


class VolcanoMultiModalInput:
    """
    多模态输入节点
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "chat": ("VOLCANO_CHAT",),
            },
            "optional": {
                "text_input": ("STRING", {"multiline": True, "default": ""}),
                "image_input": ("IMAGE",),
                "video_input": ("STRING", {"default": ""}),  # 视频路径或URL
                "system_prompt": ("STRING", {"multiline": True, "default": ""}),
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "top_p": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 1.0, "step": 0.05}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("text_output", "info", "image_output", "video_output")
    FUNCTION = "process"
    CATEGORY = "🌋火山引擎/多模态"
    
    def process(self, chat, text_input="", image_input=None, video_input="", 
                system_prompt="", max_tokens=1024, temperature=0.7, top_p=0.9):
        try:
            # 构建内容列表
            content_list = []
            
            if text_input:
                content_list.append({"type": "text", "content": text_input})
            
            if image_input is not None:
                content_list.append({"type": "image", "content": image_input})
            
            if video_input:
                content_list.append({"type": "video", "content": video_input})
            
            if not content_list:
                raise ValueError("至少需要提供一种输入内容")
            
            # 调用API - 移除model参数，让VolcanoChat使用endpoint_id
            response_text, response_info = chat.generate_multimodal(
                content_list=content_list,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            
            # 处理输出
            info_json = json.dumps(response_info, ensure_ascii=False, indent=2)
            
            # 目前主要返回文本，图片和视频输出需要根据API响应格式调整
            empty_image = None  # 需要创建空白图片tensor
            empty_video = ""
            
            return (response_text, info_json, empty_image, empty_video)
            
        except Exception as e:
            logger.error(f"多模态处理失败: {str(e)}")
            # 提供更详细的错误信息
            if "Connection error" in str(e):
                raise RuntimeError(f"连接失败: 请检查网络连接和API配置。详细错误: {str(e)}")
            elif "401" in str(e) or "Unauthorized" in str(e):
                raise RuntimeError(f"认证失败: 请检查API Key是否正确。详细错误: {str(e)}")
            elif "404" in str(e):
                raise RuntimeError(f"端点不存在: 请检查endpoint_id是否正确。详细错误: {str(e)}")
            else:
                raise RuntimeError(f"处理失败: {str(e)}")


# 简化的文本专用节点（向后兼容）
class VolcanoLLMPrompt:
    """
    火山引擎文本提示节点（简化版）
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "chat": ("VOLCANO_CHAT",),
                "prompt": ("STRING", {"multiline": True, "default": "你好，请介绍一下自己。"}),
            },
            "optional": {
                "system_prompt": ("STRING", {"multiline": True, "default": ""}),
                "model": ("STRING", {"default": ""}),  # REST API模式需要
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "top_p": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 1.0, "step": 0.05}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "info")
    FUNCTION = "generate"
    CATEGORY = "🌋火山引擎/LLM"
    
    def generate(self, chat, prompt, system_prompt="", model="", max_tokens=1024, temperature=0.7, top_p=0.9):
        try:
            content_list = [{"type": "text", "content": prompt}]
            
            response_text, response_info = chat.generate_multimodal(
                content_list=content_list,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                model=model
            )
            
            info_json = json.dumps(response_info, ensure_ascii=False, indent=2)
            return (response_text, info_json)
            
        except Exception as e:
            logger.error(f"文本生成失败: {str(e)}")
            raise RuntimeError(f"生成失败: {str(e)}")


# 导出节点类
__all__ = ["VolcanoLLMLoader", "VolcanoLLMPrompt", "VolcanoMultiModalInput", "VolcanoChat"]
