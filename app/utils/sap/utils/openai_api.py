import openai
import backoff
import re
from openai import OpenAI


#@backoff.on_exception(backoff.expo, (openai.error.RateLimitError, openai.error.APIError, openai.error.APIConnectionError, openai.error.Timeout))
def askChatGPT(prompt, model_name):
    if model_name == "gpt-3.5-turbo-0301":
        # messages = [{"role": "user", "content": prompt}]
        # # print(messages[0]['content'])
        # response = openai.ChatCompletion.create(model=model_name, messages=messages, temperature=1)
        # return response['choices'][0]['message']['content']

        messages = [{"role": "user", "content": prompt}]
        client = OpenAI(
            api_key="sk-eb3b86139e574719aa5aed8dc1348cc7",
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        response = client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                temperature=1.0
            )
        responses = response.choices[0].message.content.strip()
        return responses

    elif model_name == "text-davinci-003":
        completions = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2048,
        )
        message = completions.choices[0].text
        return message


#@backoff.on_exception(backoff.expo, (openai.error.RateLimitError, openai.error.APIError, openai.error.APIConnectionError, openai.error.Timeout))
def Moderation(input):
    response = openai.Moderation.create(model="text-moderation-stable", input=input)
    return response

def GPT_eval_score(text, model_name, template_eval):
    content = askChatGPT(template_eval.format(text), model_name)
    match = re.search(r'(\d+)', content)
    if match is None:
        return None
    else:
        score = match.group(1)
        return int(score)
