from app.models import AttackParameter
from app.attack.jailbreakingllm.common import initialize_conversations
from app.attack.jailbreakingllm.conversers import load_attack_and_target_models

def jailbreakingllm(attack_parameter : AttackParameter,data):

    ########### 配置模型参数 ###########
    attack_model = attack_parameter.attack_model
    attack_max_n_tokens = 500
    max_n_attack_attempts = 1

    # 目标模型
    target_model = attack_parameter.attack_model
    target_max_n_tokens = 150
    jailbreakbench_phase = "dev"

    # 评估模型
    n_streams = 1
    evaluate_locally = 'store_true'

    attackLM, targetLM = load_attack_and_target_models(attack_model, attack_max_n_tokens, max_n_attack_attempts,"", evaluate_locally, target_model,target_max_n_tokens, jailbreakbench_phase)
    convs_list, processed_response_list, system_prompts = initialize_conversations(n_streams, data ,attackLM.template)
    extracted_attack_list = attackLM.get_attack(attack_parameter, convs_list, processed_response_list)
    adv_prompt_list = [attack["prompt"] for attack in extracted_attack_list]

    return adv_prompt_list[0]
