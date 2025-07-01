
import requests

class VolcanoLLMLoader:
    def __init__(self, api_key: str, endpoint_id: str):
        self.api_key = api_key
        self.endpoint_id = endpoint_id
        self.base_url = f"https://api.volcengine.com/llm/v1/{self.endpoint_id}"

    def load_model(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(f"{self.base_url}/model", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to load model: {response.text}")

class VolcanoLLMPrompt:
    def __init__(self, loader: VolcanoLLMLoader):
        self.loader = loader

    def generate_prompt(self, input_data: dict):
        headers = {"Authorization": f"Bearer {self.loader.api_key}"}
        response = requests.post(f"{self.loader.base_url}/prompt", json=input_data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to generate prompt: {response.text}")
