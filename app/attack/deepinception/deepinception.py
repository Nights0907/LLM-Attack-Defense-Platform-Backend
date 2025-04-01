# -*- coding: utf-8 -*-
import os
import json
import argparse

from app.models import AttackParameter
# 引入 deepinception 的配置文件
from app.utils.deepinception.config import TARGET_TEMP, TARGET_TOP_P
from app.utils.deepinception.conversers import load_attack_and_target_models, TargetLM

def deep_inception(attack_parameter : AttackParameter):

    # 模型参数配置

    target_model = attack_parameter.attack_model
    # Maximum number of generated tokens for the target
    target_max_n_tokens = 300
    # Experiment file name : ['main', 'abl_c', 'abl_layer', 'multi_scene', 'abl_fig6_4', 'further_q']
    exp_name = "main"
    # LLM defense: None, Self-Reminder, In-Context
    defense = "none"

    # 有害问题数据集
    malicious_question_set = attack_parameter.malicious_question_set+'_'+exp_name+'.json'
    f = open(malicious_question_set)
    datas = json.load(f) 
    f.close() 
    results = [{} for _ in range(len(datas))]


    for idx, data in enumerate(datas):
        if exp_name in ['main', 'further_q']:
            questions = [data['inception_attack']] + data['questions']
        else:
            questions = data['questions']

        targetLM = TargetLM(model_name=target_model,
                 max_n_tokens=target_max_n_tokens,
                 temperature=TARGET_TEMP,  # init to 0
                 top_p=TARGET_TOP_P,  # init to 1
                 preloaded_model=None,
                 )
        results[idx]['topic'] = data['topic']
        # Get target responses
        results[idx]['qA_pairs'] = []
        for question in questions:
            target_response_list = targetLM.get_response(question, defense)
            results[idx]['qA_pairs'].append({'Q': question, 'A': target_response_list})
            print(target_response_list)

        del targetLM
    
    results_dumped = json.dumps(results)
    os.makedirs('app/results', exist_ok=True)
    with open(f'app/results/deepinception/{target_model}_{exp_name}_{defense}_results.json', 'w+') as f:
        f.write(results_dumped)
    f.close()
