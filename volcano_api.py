import os
import json
import logging
from typing import Dict, Any, List, Tuple, Optional

import openai
import requests

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('VolcanoAPI')

class VolcanoChat:
    """
    火山引擎 LLM API 客户端类
    用于处理与火山引擎 API 的通信
    """
    def __init__(self, endpoint_id: str, api_key: str, base_url: str):
        self.endpoint_id = endpoint_id
        self.api_key = api_key
        self.base_url = base_url
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        logger.info(f"初始化 VolcanoChat 客户端: endpoint_id={endpoint_id}, base_url={base_url}")

    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 1024, 
                temperature: float = 0.7, top_p: float = 0.9, 
                stop: Optional[List[str]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        生成文本响应
        
        Args:
            prompt: 用户提示文本
            system_prompt: 系统提示文本
            max_tokens: 最大生成令牌数
            temperature: 温度参数
            top_p: 采样参数
            stop: 停止序列
            
        Returns:
            生成的文本和完整的响应信息
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            logger.info(f"发送请求到火山引擎 API: endpoint_id={self.endpoint_id}")
            
            response = self.client.chat.completions.create(
                model=self.endpoint_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop
            )
            
            # 提取生成的文本
            generated_text = response.choices[0].message.content
            
            # 构建响应信息
            response_info = {
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            return generated_text, response_info
            
        except Exception as e:
            logger.error(f"生成文本时出错: {str(e)}")
            raise RuntimeError(f"火山引擎 API 调用失败: {str(e)}")

    def generate_stream(self, prompt: str, system_prompt: str = "", max_tokens: int = 1024, 
                       temperature: float = 0.7, top_p: float = 0.9, 
                       stop: Optional[List[str]] = None):
        """
        流式生成文本响应
        
        Args:
            prompt: 用户提示文本
            system_prompt: 系统提示文本
            max_tokens: 最大生成令牌数
            temperature: 温度参数
            top_p: 采样参数
            stop: 停止序列
            
        Returns:
            生成的文本流
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            logger.info(f"发送流式请求到火山引擎 API: endpoint_id={self.endpoint_id}")
            
            response = self.client.chat.completions.create(
                model=self.endpoint_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                stream=True
            )
            
            return response
            
        except Exception as e:
            logger.error(f"流式生成文本时出错: {str(e)}")
            raise RuntimeError(f"火山引擎 API 流式调用失败: {str(e)}")


class VolcanoLLMLoader:
    """
    ComfyUI 火山引擎 LLM 加载器节点
    用于在 ComfyUI 中加载火山引擎 LLM 模型
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "endpoint_id": ("STRING", {"default": "ep-xxxxxxxx"}),
                "api_key": ("STRING", {"default": ""}),
            },
            "optional": {
                "region": ("STRING", {"default": "cn-beijing"}),
                "custom_base_url": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("VOLCANO_CHAT",)
    RETURN_NAMES = ("chat",)
    FUNCTION = "load_model"
    CATEGORY = "🌋火山引擎/LLM"
    
    def load_model(self, endpoint_id: str, api_key: str, region: str = "cn-beijing", custom_base_url: str = ""):
        """
        加载火山引擎 LLM 模型
        
        Args:
            endpoint_id: 火山引擎端点 ID
            api_key: API 密钥
            region: 区域，默认为 cn-beijing
            custom_base_url: 自定义基础 URL，如果提供则优先使用
            
        Returns:
            VolcanoChat 实例
        """
        try:
            # 构建基础 URL
            if custom_base_url:
                base_url = custom_base_url
            else:
                base_url = f"https://ark.{region}.volcengine.com/v1"
            
            # 确保 URL 格式正确
            if not base_url.endswith("/"):
                base_url += "/"
            
            logger.info(f"加载火山引擎 LLM 模型: endpoint_id={endpoint_id}, region={region}")
            
            # 创建 VolcanoChat 实例
            chat = VolcanoChat(endpoint_id, api_key, base_url)
            
            # 测试连接
            self._test_connection(chat)
            
            return (chat,)
            
        except Exception as e:
            logger.error(f"加载火山引擎 LLM 模型时出错: {str(e)}")
            raise RuntimeError(f"无法加载火山引擎 LLM 模型: {str(e)}")
    
    def _test_connection(self, chat: VolcanoChat):
        """
        测试与火山引擎 API 的连接
        
        Args:
            chat: VolcanoChat 实例
        """
        try:
            # 发送一个简单的请求以测试连接
            logger.info("测试与火山引擎 API 的连接...")
            response = requests.get(
                f"{chat.base_url}models",
                headers={"Authorization": f"Bearer {chat.api_key}"}
            )
            
            if response.status_code != 200:
                logger.warning(f"API 连接测试返回状态码: {response.status_code}")
                logger.warning(f"响应内容: {response.text}")
                if response.status_code == 401:
                    raise RuntimeError("API 密钥无效或权限不足")
                elif response.status_code == 404:
                    raise RuntimeError(f"API 端点不存在，请检查 region 和 endpoint_id 是否正确")
                else:
                    raise RuntimeError(f"API 连接测试失败: HTTP {response.status_code}")
            
            logger.info("成功连接到火山引擎 API")
            
        except requests.RequestException as e:
            logger.error(f"测试连接时出错: {str(e)}")
            raise RuntimeError(f"无法连接到火山引擎 API: {str(e)}")


class VolcanoLLMPrompt:
    """
    火山引擎 LLM 提示节点
    用于向火山引擎 LLM 发送提示并获取响应
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
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "top_p": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 1.0, "step": 0.05}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "info")
    FUNCTION = "generate"
    CATEGORY = "🌋火山引擎/LLM"
    
    def generate(self, chat, prompt, system_prompt="", max_tokens=1024, temperature=0.7, top_p=0.9):
        """
        生成文本响应
        
        Args:
            chat: VolcanoChat 实例
            prompt: 用户提示文本
            system_prompt: 系统提示文本
            max_tokens: 最大生成令牌数
            temperature: 温度参数
            top_p: 采样参数
            
        Returns:
            生成的文本和响应信息的 JSON 字符串
        """
        try:
            response_text, response_info = chat.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            
            # 将响应信息转换为 JSON 字符串
            info_json = json.dumps(response_info, ensure_ascii=False, indent=2)
            
            return (response_text, info_json)
            
        except Exception as e:
            logger.error(f"生成文本时出错: {str(e)}")
            raise RuntimeError(f"生成文本失败: {str(e)}")


# 导出节点类，供 __init__.py 使用
__all__ = ["VolcanoLLMLoader", "VolcanoLLMPrompt", "VolcanoChat"]
