import openai
import re
from openai import OpenAI

from app.utils.llm_completion_utils import get_llm_responses


#@backoff.on_exception(backoff.expo, (openai.error.RateLimitError, openai.error.APIError, openai.error.APIConnectionError, openai.error.Timeout))
def askChatGPT(prompt, model_name):

    messages = [{"role": "user", "content": prompt}]
    client = OpenAI(
        api_key="sk-eb3b86139e574719aa5aed8dc1348cc7",
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=1.0
        )
    responses = response.choices[0].message.content.strip()
    return responses

    # elif model_name == "text-davinci-003":
    #     completions = openai.Completion.create(
    #         engine="text-davinci-003",
    #         prompt=prompt,
    #         max_tokens=2048,
    #     )
    #     message = completions.choices[0].text

    return message


#@backoff.on_exception(backoff.expo, (openai.error.RateLimitError, openai.error.APIError, openai.error.APIConnectionError, openai.error.Timeout))
def Moderation(input):
    response = openai.Moderation.create(model="text-moderation-stable", input=input)
    return response

def GPT_eval_score(model_name, text,temperature,retry_times,template_eval):

    message = template_eval.format(text).replace('"', ' ').replace("'", ' ')
    messages = [{"role": "user", "content": message}]
    print(messages)

    content = get_llm_responses(model_name,messages,temperature,retry_times)
    print(content)

    match = re.search(r'(\d+)', content)
    if match is None:
        return None
    else:
        score = match.group(1)
        return int(score)
