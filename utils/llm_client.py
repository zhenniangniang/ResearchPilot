from openai import OpenAI
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL


def get_client() -> OpenAI:
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)


def chat(system_prompt: str, user_prompt: str, model: str = None, stream: bool = False):
    """
    调用 LLM，返回字符串结果（或 stream generator）。
    """
    client = get_client()
    model = model or LLM_MODEL
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
        temperature=0.3,
    )
    if stream:
        return response  # 返回 generator，供调用方迭代
    return response.choices[0].message.content
