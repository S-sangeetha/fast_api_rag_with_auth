from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()


class HuggingFaceLLM:

    def __init__(self):
        self.client = InferenceClient(
            api_key=os.getenv("HF_TOKEN"),
            provider="auto"
        )

    async def generate(self, prompt: str):

        response =self.client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500
        )

        return response.choices[0].message.content


hf_llm = HuggingFaceLLM()