"""
common - 工具函数模块

函数：封装功能上相对独立而且会被重复使用的代码。

Author: 骆昊
Version: 0.1
Date: 2025/6/17
"""


# from functools import lru_cache
#
#
# @lru_cache(maxsize=64)
def get_llm_response(client, *, system_prompt='', few_shot_prompt=None,
                     user_prompt='', model='deepseek-chat', temperature=0.2,
                     top_p=0.1, frequency_penalty=0, presence_penalty=0,
                     max_tokens=1024, stream=False):
    """获取大模型响应"""
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    if few_shot_prompt and isinstance(few_shot_prompt, list):
        messages += few_shot_prompt
    if user_prompt:
        messages.append({'role': 'user', 'content': user_prompt})
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_tokens=max_tokens,
        messages=messages,
        stream=stream,
    )
    if not stream:
        return resp.choices[0].message.content
    return resp