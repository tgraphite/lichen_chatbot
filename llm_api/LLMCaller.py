import requests
import json
import os


class LLMCaller:
    """调用LLM的类"""

    def __init__(self, config_file: str = None):
        if not config_file:
            this_file_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(this_file_dir, "llm_config.json")
        with open(config_file, "r") as f:
            self.config = json.load(f)

    @property
    def available_llms(self):
        return list(self.config.keys())

    def call(
        self, llm_name: str, system_prompt: str, user_prompt: str, verbose: bool = False
    ):
        """调用指定的 LLM API"""
        if llm_name not in self.config:
            raise ValueError(f"LLM '{llm_name}' not found in configuration.")

        api_config = self.config[llm_name]
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        headers = {
            "Authorization": f"Bearer {api_config['key']}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": api_config["model"],
            "messages": messages,
            "temperature": api_config["temperature"],
            "max_tokens": api_config["max_tokens"],
            "stream": False,
            "top_p": 0.7,
            "response_format": {"type": "text"},
        }

        response = requests.post(api_config["chat_url"], json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        if verbose:
            return response_data
        else:
            return response_data["choices"][0]["message"]["content"]

    def completion(self, llm_name, messages):
        """调用指定的 LLM API"""
        if llm_name not in self.config:
            raise ValueError(f"LLM '{llm_name}' not found in configuration.")

        api_config = self.config[llm_name]

        headers = {
            "Authorization": f"Bearer {api_config['key']}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": api_config["model"],
            "messages": messages,
            "temperature": api_config["temperature"],
            "max_tokens": api_config["max_tokens"],
            "stream": False,
            "top_p": 0.7,
            "response_format": {"type": "text"},
        }

        response = requests.post(api_config["chat_url"], json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        return response_data["choices"][0]["message"]["content"]


# 使用示例
if __name__ == "__main__":
    llm_caller = LLMCaller()
    response = llm_caller.call(
        "qwen2.5-32b-instruct",
        "你是一个助手",
        "请告诉我关于量子力学的基本概念。",
        verbose=True,
    )
    print(response)
