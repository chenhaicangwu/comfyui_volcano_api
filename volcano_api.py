import os
import json
import logging
import enum
from typing import Dict, Any, List, Tuple, Optional, Union

import openai
import requests

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('VolcanoAPI')

# 定义 API 模式枚举
class APIMode(enum.Enum):
    OPENAPI = "OpenAPI"
    REST_API = "REST API"

class VolcanoChat:
    """
    火山引擎 LLM API 客户端类
    用于处理与火山引擎 API 的通信
    """
    def __init__(self, endpoint_id: str, api_key: str, base_url: str, api_mode: APIMode = APIMode.OPENAPI):
        self.endpoint_id = endpoint_id
        self.api_key = api_key
        self.base_url = base_url
        self.api_mode = api_mode
        
        # 如果是 OpenAPI 模式，初始化 OpenAI 客户端
        if api_mode == APIMode.OPENAPI:
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        
        logger.info(f"初始化 VolcanoChat 客户端: endpoint_id={endpoint_id}, base_url={base_url}, api_mode={api_mode.value}")

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
            
            logger.info(f"发送请求到火山引擎 API: endpoint_id={self.endpoint_id}, api_mode={self.api_mode.value}")
            
            # 根据 API 模式选择不同的请求方式
            if self.api_mode == APIMode.OPENAPI:
                # 使用 OpenAI 客户端发送请求
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
            else:  # REST API 模式
                # 构建请求体
                request_data = {
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p
                }
                if stop:
                    request_data["stop"] = stop
                
                # 发送 REST API 请求
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # 构建完整的 URL
                url = f"{self.base_url}/v1/completions"
                if not url.startswith("http"):
                    url = f"https://{url}"
                
                response = requests.post(url, headers=headers, json=request_data)
                
                # 检查响应状态
                response.raise_for_status()
                
                # 解析响应
                response_json = response.json()
                
                # 提取生成的文本
                generated_text = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # 构建响应信息
                response_info = {
                    "finish_reason": response_json.get("choices", [{}])[0].get("finish_reason", ""),
                    "usage": response_json.get("usage", {})
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
            
            logger.info(f"发送流式请求到火山引擎 API: endpoint_id={self.endpoint_id}, api_mode={self.api_mode.value}")
            
            # 根据 API 模式选择不同的请求方式
            if self.api_mode == APIMode.OPENAPI:
                # 使用 OpenAI 客户端发送流式请求
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
            else:  # REST API 模式
                # 构建请求体
                request_data = {
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stream": True
                }
                if stop:
                    request_data["stop"] = stop
                
                # 发送 REST API 流式请求
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # 构建完整的 URL
                url = f"{self.base_url}/v1/completions"
                if not url.startswith("http"):
                    url = f"https://{url}"
                
                response = requests.post(url, headers=headers, json=request_data, stream=True)
                
                # 检查响应状态
                response.raise_for_status()
                
                # 返回响应流
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
                "api_mode": (["OpenAPI", "REST API"], {"default": "OpenAPI"}),
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
    
    def load_model(self, api_mode: str, endpoint_id: str, api_key: str, region: str = "cn-beijing", custom_base_url: str = ""):
        """
        加载火山引擎 LLM 模型
        
        Args:
            api_mode: API 模式，"OpenAPI" 或 "REST API"
            endpoint_id: 火山引擎端点 ID
            api_key: API 密钥
            region: 区域，默认为 cn-beijing
            custom_base_url: 自定义基础 URL，如果提供则优先使用
            
        Returns:
            VolcanoChat 实例
        """
        try:
            # 转换 API 模式为枚举值
            api_mode_enum = APIMode.OPENAPI if api_mode == "OpenAPI" else APIMode.REST_API
            
            # 构建基础 URL
            if custom_base_url and custom_base_url.strip():
                base_url = custom_base_url.strip()
                # 检查 URL 是否包含必要的域名部分
                if "volcengine.com" not in base_url:
                    logger.warning(f"自定义 URL 可能不正确: {base_url}")
                    if api_mode_enum == APIMode.OPENAPI:
                        logger.info("OpenAPI 模式下，正确的 URL 格式应为: https://ark.[region].volcengine.com/v1")
                    else:
                        logger.info("REST API 模式下，正确的 URL 格式应为: https://open.volcengineapi.com")
            else:
                # 根据 API 模式选择默认的基础 URL
                if api_mode_enum == APIMode.OPENAPI:
                    base_url = f"https://ark.{region}.volcengine.com/v1"
                else:
                    base_url = "https://open.volcengineapi.com"
            
            # 确保 URL 格式正确
            if not base_url.endswith("/"):
                base_url += "/"
                
            # 确保 URL 包含协议
            if not base_url.startswith("http"):
                base_url = "https://" + base_url
            
            logger.info(f"加载火山引擎 LLM 模型: endpoint_id={endpoint_id}, region={region}, api_mode={api_mode}")
            
            # 创建 VolcanoChat 实例
            chat = VolcanoChat(endpoint_id, api_key, base_url, api_mode_enum)
            
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
            logger.info(f"使用 base_url: {chat.base_url}")
            logger.info(f"使用 endpoint_id: {chat.endpoint_id}")
            logger.info(f"使用 api_mode: {chat.api_mode.value}")
            
            # 根据 API 模式选择不同的测试方式
            if chat.api_mode == APIMode.OPENAPI:
                # 尝试使用 chat.completions.create 进行测试
                try:
                    # 使用一个非常简短的提示进行测试，只是为了验证连接
                    test_response = chat.client.chat.completions.create(
                        model=chat.endpoint_id,
                        messages=[{"role": "user", "content": "测试连接"}],
                        max_tokens=5
                    )
                    logger.info("成功连接到火山引擎 OpenAPI 并获得响应")
                    return
                except openai.NotFoundError as e:
                    logger.warning(f"端点 ID 不存在: {str(e)}")
                    raise RuntimeError(f"API 端点不存在，请检查 endpoint_id 是否正确: {chat.endpoint_id}")
                except openai.AuthenticationError as e:
                    logger.warning(f"认证失败: {str(e)}")
                    raise RuntimeError(f"API 密钥无效或权限不足，请检查 api_key")
                except Exception as e:
                    # 如果上面的方法失败，尝试备用方法
                    logger.warning(f"使用 chat.completions.create 测试失败: {str(e)}")
                    logger.info("尝试备用方法测试连接...")
                
                # 备用测试方法：直接请求 models 端点
                response = requests.get(
                    f"{chat.base_url}models",
                    headers={"Authorization": f"Bearer {chat.api_key}"}
                )
            else:  # REST API 模式
                # 构建测试请求
                headers = {
                    "Authorization": f"Bearer {chat.api_key}",
                    "Content-Type": "application/json"
                }
                
                # 构建完整的 URL
                url = f"{chat.base_url}v1/completions"
                if not url.startswith("http"):
                    url = f"https://{url}"
                
                # 发送一个简单的测试请求
                test_data = {
                    "messages": [{"role": "user", "content": "测试连接"}],
                    "max_tokens": 5
                }
                
                response = requests.post(url, headers=headers, json=test_data)
            
            # 检查响应状态
            if response.status_code != 200:
                logger.warning(f"API 连接测试返回状态码: {response.status_code}")
                logger.warning(f"响应内容: {response.text}")
                if response.status_code == 401:
                    raise RuntimeError("API 密钥无效或权限不足，请检查 api_key")
                elif response.status_code == 404:
                    # 提供更详细的错误信息
                    error_msg = f"API 端点不存在，请检查以下配置:\n"
                    error_msg += f"1. API 模式是否正确: 当前模式为 '{chat.api_mode.value}'\n"
                    error_msg += f"2. base_url 是否完整: 当前值为 '{chat.base_url}'\n"
                    error_msg += f"3. endpoint_id 是否正确: 当前值为 '{chat.endpoint_id}'\n"
                    
                    if chat.api_mode == APIMode.OPENAPI:
                        error_msg += f"OpenAPI 模式下，正确的 base_url 格式应为: https://ark.cn-beijing.volcengine.com/v1/"
                    else:
                        error_msg += f"REST API 模式下，正确的 base_url 格式应为: https://open.volcengineapi.com/"
                    
                    raise RuntimeError(error_msg)
                else:
                    raise RuntimeError(f"API 连接测试失败: HTTP {response.status_code}，响应: {response.text[:200]}")
            
            logger.info(f"成功连接到火山引擎 {chat.api_mode.value}")
            
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
