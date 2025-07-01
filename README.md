# ComfyUI 火山引擎 API 插件

这是一个专门为 ComfyUI 设计的插件，用于连接火山引擎（Volcano Engine）的大语言模型 API。支持多模态输入输出（文本、图片、视频），提供高度自定义的配置选项，兼容多个 ComfyUI 版本。

## 功能特点

- **多模态支持**：支持文本、图片、视频的输入和输出
- **简化配置**：移除复杂的区域参数，直接使用完整的 base_url
- **双API模式**：支持 OpenAPI 和 REST API 两种调用方式
- **高度自定义**：灵活的参数配置，适应不同模型需求
- **兼容性优化**：兼容多个 ComfyUI 版本，避免依赖冲突
- **智能参数显示**：根据 API 模式动态显示相关参数
- **详细错误处理**：提供清晰的错误信息和调试支持

## 安装方法

### 方法一：通过 Git 克隆

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/yourusername/comfyui_volcano_api.git
cd comfyui_volcano_api
pip install -r requirements.txt
```

### 方法二：手动下载

1. 下载此仓库的 ZIP 文件
2. 解压到 `ComfyUI/custom_nodes/` 目录
3. 进入解压后的目录，运行 `pip install -r requirements.txt`

## 节点说明

### Volcano LLM Loader

加载火山引擎 LLM 模型并创建连接。

#### 参数

- **必需参数**：
  - `endpoint_id`：火山引擎端点 ID，形如 `ep-xxxxxxxx`
  - `api_key`：火山引擎 API 密钥

- **可选参数**：
  - `region`：区域，默认为 `cn-beijing`
  - `custom_base_url`：自定义基础 URL，如果需要使用非标准 URL

#### 输出

- `chat`：火山引擎 LLM 聊天对象，可连接到 Volcano LLM Prompt 节点

### Volcano LLM Prompt

向火山引擎 LLM 发送提示并获取响应。

#### 参数

- **必需参数**：
  - `chat`：来自 Volcano LLM Loader 的聊天对象
  - `prompt`：用户提示文本

- **可选参数**：
  - `system_prompt`：系统提示文本
  - `max_tokens`：最大生成令牌数，默认为 1024
  - `temperature`：温度参数，控制随机性，默认为 0.7
  - `top_p`：采样参数，默认为 0.9

#### 输出

- `response`：模型生成的文本响应
- `info`：包含令牌使用情况等信息的 JSON 字符串

## 使用示例

### 基本使用流程

1. 添加 `Volcano LLM Loader` 节点
2. 配置您的 `endpoint_id` 和 `api_key`
3. 连接 `Volcano LLM Loader` 的输出到 `Volcano LLM Prompt` 节点
4. 在 `Volcano LLM Prompt` 节点中输入您的提示
5. 运行工作流获取 LLM 响应

### 示例工作流

```
[Volcano LLM Loader] -> [Volcano LLM Prompt] -> [Text Display]
```

## 获取火山引擎 API 参数

1. 登录火山引擎控制台：https://console.volcengine.com/
2. 进入 ARK（人工智能与机器学习）服务
3. 创建或选择现有的端点
4. 获取端点 ID（形如 `ep-xxxxxxxx`）
5. 在 API 访问管理中创建并获取 API 密钥

## 常见问题

### 连接错误

如果遇到连接错误，请检查：

1. `endpoint_id` 是否正确
2. `api_key` 是否有效且完整
3. 网络连接是否正常
4. 控制台日志中的详细错误信息

### API 调用失败

如果 API 调用失败，可能的原因包括：

1. API 密钥权限不足
2. 端点不存在或已被删除
3. 请求参数格式错误
4. 超出 API 调用限制

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 致谢

- 感谢 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 提供的优秀框架
- 感谢 [ComfyUI LLM Party](https://github.com/heshengtao/comfyui_LLM_party) 项目的启发

## 联系方式

如有问题或建议，请通过 GitHub Issues 与我们联系。
