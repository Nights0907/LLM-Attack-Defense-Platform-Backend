from tqdm import tqdm
import time

from app.models import AttackParameter
from app.utils.codechameleon.utils import save_generation, complete_format, save_prompts
from app.attack.codechameleon.template import get_prompts
from app.utils.renellm.llm_completion_utils import get_llm_responses

def set_config(model_generation_config, args):
    generation_config = model_generation_config
    generation_config.max_new_tokens = args.max_new_tokens
    generation_config.do_sample = args.do_sample
    generation_config.repetition_penalty = args.repetition_penalty
    generation_config.temperature = args.temperature
    generation_config.top_p = args.top_p
    generation_config.use_cache = args.use_cache

    return generation_config


def codechameleon(attack_parameter : AttackParameter):

    # 配置攻击默认参数  :
    encrypt_rule = "binary_tree"  # 攻击方式
    prompt_style = "code"
    temperature = 0

    # 获取原始 prompts 模板
    prompts, original_queries = get_prompts(attack_parameter.prompt,prompt_style, attack_parameter.malicious_question_set, encrypt_rule)
    # 包装成 大模型对话框架
    complete_prompts,original_queries_list = complete_format(prompts, original_queries)
    # 获取攻击结果

    results = []
    idx = 0

    with tqdm(total=len(complete_prompts)) as pbar:
        for chat_prompt in complete_prompts:

            # 保存原始有害问题
            original_harm_behavior = original_queries_list[idx]

            # 记录大模型问答消耗时间
            start_time = time.time()
            idx = idx + 1
            attack_output = get_llm_responses(attack_parameter.attack_model, chat_prompt, temperature,attack_parameter.retry_times)
            pbar.update(1)

            item = {}
            end_time = time.time()
            elapsed_time = end_time - start_time

            # 6个必要参数
            item['idx'] = idx
            item['original_harm_behavior'] = original_harm_behavior
            item['attack_output'] = attack_output
            item['time_cost'] = elapsed_time

            results.append(item)

            # 每10次对话保存一次结果
            if idx % 10 == 0:
                save_generation(attack_parameter, results,idx)

            time.sleep(1)

    # 保存攻击结果
    save_generation(attack_parameter, results,idx)

    return results
