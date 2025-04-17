from app.models import model_info

import os
import time
import requests

from openai import OpenAI
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from app.utils.log_utils import log_message, print_and_log


def get_model_info(model_name:str):
    curr_model = model_info.query.filter_by(model_name=model_name).first()
    return curr_model.base_url,curr_model.api_key

# for gpt
def get_llm_responses(model, messages, temperature, retry_times):

    base_url,api_key = get_model_info(model)

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    # # 科大讯飞 星火 api
    # elif model == "lite" :
    #     client = OpenAI(
    #         api_key=spark_api_key,
    #         base_url="https://spark-api-open.xf-yun.com/v1/chat/completions"
    #     )

    # # 百度 文心一言 api
    # elif model == "ernie-4.5-8k-preview":
    #     model_output = get_baidu_response(model, messages)
    #     return model_output


    try:
        response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )

        model_output = response.choices[0].message.content.strip()
        time.sleep(1)
        return model_output

    except Exception as e:
        print(e)


def get_llm_responses_stream(model, messages, temperature=0.7, retry_times=3, stream=True):
    """
    获取大模型响应（支持流式传输/完整返回）

    Args:
        model: 模型名称（qwen-plus/deepseek-reasoner/...）
        messages: 对话消息列表
        temperature: 温度参数
        retry_times: 错误重试次数
        stream: 是否流式传输（True=流式，False=完整返回）
    """
    base_url, api_key = get_model_info(model)

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    # 重试逻辑
    for attempt in range(retry_times):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=stream  # 是否流式传输
            )

            if stream:
                full_response = ""
                print(f"*************{model} 大模型的输出如下:*************\n", end=" ", flush=True)
                for chunk in response:
                    content = chunk.choices[0].delta.content or ""
                    log_message(content)
                    print(content, end="", flush=True)  # 实时打印
                    full_response += content
                return full_response.strip()
            else:
                return response.choices[0].message.content.strip()

        except Exception as e:
            print_and_log(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retry_times - 1:
                raise  # 最后一次重试仍失败则抛出异常
            time.sleep(1)  # 延迟后重试

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
        "temperature": 0.5,
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