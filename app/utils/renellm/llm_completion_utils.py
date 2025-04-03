import os
import time
import requests

from openai import OpenAI
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# for gpt
def get_llm_responses(model, messages, temperature, retry_times):

    qwen_api_key = os.environ.get("QWEN_API_KEY")
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
    tencent_api_key = os.environ.get("TENCENT_API_KEY")

    # 默认调用
    client = OpenAI(
        api_key=qwen_api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    # 阿里 通义千问 api
    if model == "qwen-plus":
        client = OpenAI(
            api_key=qwen_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    # deepseek 深度求索 api
    elif model == "deepseek-reasoner":
        client = OpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
    # 腾讯 混元 api
    elif model == "hunyuan-turbos-latest":
        client = OpenAI(
            api_key=tencent_api_key,
            base_url="https://api.hunyuan.cloud.tencent.com/v1"
        )
    # # 科大讯飞 星火 api
    # elif model == "lite" :
    #     client = OpenAI(
    #         api_key=spark_api_key,
    #         base_url="https://spark-api-open.xf-yun.com/v1/chat/completions"
    #     )
    # 百度 文心一言 api
    elif model == "ernie-4.5-8k-preview":
        response = get_baidu_response(model, messages)
        return response


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

# for baidu

def get_baidu_access_token(api_key, secret_key):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    response = requests.post(url, params=params).json()
    return response["access_token"]

def get_baidu_response(attack_model,prompt):

    BAIDU_API_KEY = os.environ.get("BAIDU_API_KEY")
    BAIDU_SECRET_KEY = os.environ.get("BAIDU_SECRET_KEY")
    access_token = get_baidu_access_token(BAIDU_API_KEY, BAIDU_SECRET_KEY)

    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    params = {"access_token": access_token}
    payload = {
        "model": attack_model,
        "messages": prompt,
        "temperature": 0.5
    }
    response = requests.post(url, params=params, headers=headers, json=payload).json()
    return response["result"]

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