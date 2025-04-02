import os

from openai import OpenAI
import time
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# for gpt
def get_llm_responses(model, messages, temperature, retry_times):

    qwen_api_key = os.environ.get("QWEN_API_KEY")
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
    tencent_api_key = os.environ.get("TENCENT_API_KEY")
    baidu_api_key = os.environ.get("BAIDU_API_KEY")

    # 默认调用
    client = OpenAI(
        api_key=qwen_api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    if model == "qwen-plus":
        client = OpenAI(
            api_key=qwen_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    elif model == "deepseek-reasoner":
        client = OpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
    elif model == "hunyuan-turbos-latest":
        client = OpenAI(
            api_key=tencent_api_key,
            base_url="https://api.hunyuan.cloud.tencent.com/v1"
        )
    elif model == "ernie-4.5-8k-preview":
        client = OpenAI(
            api_key=baidu_api_key,
            base_url="https://qianfan.bj.baidubce.com/v2/chat/completions"
        )


    try:
        response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
    except Exception as e:
        print(e)
        for retry_time in range(retry_times):
            retry_time = retry_time + 1
            print(f"{model} Retry {retry_time}")
            time.sleep(1)
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                break
            except:
                continue

    model_output = response.choices[0].message.content.strip()
    time.sleep(1)

    return model_output

# for claude
def claudeCompletion(model, max_tokens, temperature, prompt, retry_times, round_sleep, fail_sleep, api_key, base_url=None):
    if base_url is None:
        client = Anthropic(
            api_key=api_key
            )
    else:
        client = Anthropic(
            base_url=base_url,
            auth_token=api_key
            )   
    try:
        completion = client.completions.create(
            model=model,
            max_tokens_to_sample=max_tokens,
            temperature=temperature,
            prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}"
            )
    except Exception as e:
        print(e)
        for retry_time in range(retry_times):
            retry_time = retry_time + 1
            print(f"{model} Retry {retry_time}")
            time.sleep(fail_sleep)
            try:
                completion = client.completions.create(
                model=model,
                max_tokens_to_sample=max_tokens,
                temperature=temperature,
                prompt=prompt
                )
                break
            except:
                continue

    model_output = completion.completion.strip()
    time.sleep(round_sleep)

    return model_output