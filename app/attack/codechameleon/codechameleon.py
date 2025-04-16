from app.attack.codechameleon.template import get_prompts


def set_config(model_generation_config, args):
    generation_config = model_generation_config
    generation_config.max_new_tokens = args.max_new_tokens
    generation_config.do_sample = args.do_sample
    generation_config.repetition_penalty = args.repetition_penalty
    generation_config.temperature = args.temperature
    generation_config.top_p = args.top_p
    generation_config.use_cache = args.use_cache

    return generation_config


def codechameleon(data):

    encrypt_rule = "binary_tree"  # 攻击方式
    prompt_style = "code"

    prompts = get_prompts(prompt_style, data, encrypt_rule)

    return prompts
