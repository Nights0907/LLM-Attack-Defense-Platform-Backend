from openai import OpenAI
import time

# for gpt
def chatCompletion(model, messages, temperature, retry_times, round_sleep, fail_sleep, base_url=None):
    if base_url is None:
        client = OpenAI(
            api_key="sk-eb3b86139e574719aa5aed8dc1348cc7",
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
    else:
        client = OpenAI(
        api_key="sk-eb3b86139e574719aa5aed8dc1348cc7",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    try:
        response = client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                temperature=temperature
            )
    except Exception as e:
        print(e)
        for retry_time in range(retry_times):
            retry_time = retry_time + 1
            print(f"{model} Retry {retry_time}")
            time.sleep(fail_sleep)
            try:
                response = client.chat.completions.create(
                    model="qwen-plus",
                    messages=messages,
                    temperature=temperature,
                )
                break
            except:
                continue

    model_output = response.choices[0].message.content.strip()
    time.sleep(round_sleep)

    return model_output