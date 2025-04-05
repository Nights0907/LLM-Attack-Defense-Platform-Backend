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

# def open_source_attack(args):
#     prompts, original_queries = get_prompts(args)
#     complete_prompts = complete_format(args, prompts)
#     if args.save_prompts==True:
#         save_prompts(complete_prompts, args)
#
#     tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
#     tokenizer.pad_token = tokenizer.eos_token
#     model = AutoModelForCausalLM.from_pretrained(args.model_path, torch_dtype=torch.bfloat16, trust_remote_code=True,device_map="auto")
#
#     model_generation_config = model.generation_config
#     model_generation_config = set_config(model_generation_config, args)
#
#     results = []
#     index = 0
#     for iters in tqdm(range(len(complete_prompts))):
#         index += 1
#
#         input_ids = tokenizer(complete_prompts[iters], return_tensors="pt").to('cuda')
#         output = model.generate(**input_ids, generation_config=model_generation_config)
#         prompt_len = input_ids['attention_mask'].shape[-1]
#         result = tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)
#         results.append(result)
#
#         if index % 50 == 0:
#             save_generation(args,results, index)
#     save_generation(args,results, index)


def codechameleon(attack_parameter : AttackParameter):

    # 配置攻击默认参数  :  攻击方式 : different encrypt methods
    encrypt_rule = "binary_tree"
    prompt_style = "code"
    temperature = 0

    # 获取原始 prompts 模板
    prompts, original_queries = get_prompts(prompt_style, attack_parameter.malicious_question_set, encrypt_rule)
    # 包装成 大模型对话框架
    complete_prompts = complete_format(attack_parameter.attack_model, prompts)
    # 获取攻击结果

    results = []
    index = 0

    with tqdm(total=len(complete_prompts)) as pbar:
        for chat_prompt in complete_prompts:
            start_time = time.time()
            index = index + 1
            model_output = get_llm_responses(attack_parameter.attack_model, chat_prompt, temperature,
                                             attack_parameter.retry_times)
            pbar.update(1)

            item = {}
            item['idx'] = index
            item['attack_output'] = model_output
            end_time = time.time()
            elapsed_time = end_time - start_time
            item['time_cost'] = elapsed_time

            print(item)

            results.append(item)


            if index % 20 == 0:
                save_generation(attack_parameter, results, index)

            time.sleep(1)

    # 保存攻击结果
    save_generation(attack_parameter, results, index)

    return results
