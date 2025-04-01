import time
import json
import os
import argparse
import random

from app.models import AttackParameter
from app.utils.renellm.data_utils import data_reader
from app.utils.renellm.llm_completion_utils import chatCompletion
from app.utils.renellm.prompt_rewrite_utils import shortenSentence, misrewriteSentence, changeOrder, addChar, languageMix, styleChange
from app.utils.renellm.scenario_nest_utils import SCENARIOS
from app.utils.renellm.harmful_classification_utils import harmful_classification

def renellm(attack_parameter:AttackParameter):

    # 设置默认值
    save_suffix = "normal"
    iter_max = 20
    round_sleep = 1
    fail_sleep = 1

    # 读取有害问题数据集
    data = data_reader(attack_parameter.malicious_question_set)

    # 检查数据集问题个数
    assert (len(data) == 5)

    # data= data[:1] # for test
    # single prompt jailbreak
    # if args.prompt is not None:
    #     data = [args.prompt]

    # 加载 rewrite 方法与 nested 场景
    operations = [shortenSentence, misrewriteSentence, changeOrder, addChar, languageMix, styleChange]
    scenarios = SCENARIOS

    # 存储最终输出信息
    data_list = []

    for idx, harm_behavior in enumerate(data):

        start_time = time.time()
        temp_harm_behavior = harm_behavior

        if not os.path.exists('../../results/renellm/temp'):
            os.makedirs('../../results/renellm/temp')

        # 每 10 个样本存储一次数据
        if idx != 0 and idx % 10 == 0:
            file_name = f"../../results/renellm/temp/{save_suffix}_{idx}.json"

            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(data_list, f, ensure_ascii=False, indent=4)
            file_path = os.path.abspath(file_name)
            print(f"\nThe temporary file has been saved to: {file_path}\n")

        loop_count = 0
        
        while True:
            print(
            "\n################################\n"
            f"Current Data: {idx+1}/{len(data)}, {harm_behavior}\n"
            f"Current Iteration Round: {loop_count+1}/{iter_max}\n"
            "################################\n")
            # prompt rewriting
            while True:
                print(f"******* Start idx {idx} Prompt Rewriting! *******")
                # randomly select the number of rewriting operations.
                n = random.randint(1, 6)
                # arrange the execution order randomly
                operation_indexes = random.sample(range(6), n)
                print(f"The number of rewriting functions is: {n}")
                print(f"The order of the rewriting operations is: {operation_indexes}\n")

                temp_rewrite_results = [['original prompt', temp_harm_behavior]]
                for index in operation_indexes:
                    print(f"Excute function {index}: {operations[index].__name__}")
                    harm_behavior = operations[index](attack_parameter, harm_behavior)
                    print(f"Rewritten prompt: {harm_behavior}\n")
                    temp_rewrite_results.append([operations[index].__name__, harm_behavior])

                # check if the prompt meets the requirements; if it does, break out of the loop.
                print("******* Check if the prompt has been modified to be harmless *******")
                label = harmful_classification(attack_parameter, harm_behavior)
                print(f"\nThe label given by {attack_parameter.model_name} is: {label}\n")
                if label == "1":
                    print(f"******* Prompt idx {idx} Rewriting Done! *******\n")
                    break
                else:
                    print(f"******* Prompt idx {idx} Rewriting Failed! *******\n")
                    harm_behavior = temp_harm_behavior
                    continue

            # scenario nesting
            print(f"******* Start idx {idx} Prompt Scenario Nesting! *******")
            print(f"harm_behavior:\n{harm_behavior}\n")
            # randomly select a scenario
            scenario = random.choice(scenarios)
            nested_prompt = scenario.replace("<>", harm_behavior)
            print(f"nested_prompt:\n{nested_prompt}\n")

            print(f"******* Start idx {idx} Prompt Jailbreaking on {attack_parameter.model_name}! *******")


            #修改成国内模型Qwen
            nested_prompt = {"role": "user", "content": nested_prompt}
            messages = []

            messages.append(nested_prompt)

            attack_output = chatCompletion(attack_parameter.model_name,
                                          messages,
                                          random.uniform(0, 1),
                                          # If the prompt always is rewritten to be harmless, use random temperature instead of 0.
                                          attack_parameter.retry_times,
                                          round_sleep,
                                          fail_sleep,
                                       )

            # attack_output = claudeCompletion(
            #     args.attack_model,
            #     args.max_tokens,
            #     args.temperature,
            #     nested_prompt,
            #     args.retry_times,
            #     args.round_sleep,
            #     args.fail_sleep,
            #     args.claude_api_key,
            #     args.claude_base_url
            #     )
                
            print(f"The output of the attacked model {attack_parameter.model_name} is:\n\n{attack_output}\n")

            loop_count += 1

            if "apologize" not in attack_output and "sorry" not in attack_output.lower():

                print(f"******* Determine if the attacked model's response to the nested idx {idx} prompt is harmful *******")
                jailbreak_label = harmful_classification(attack_parameter, attack_output)
            
            else:
                if loop_count < iter_max:
                    print(f"\nJailbreaking idx {idx} Prompt Failed!\n")
                    harm_behavior = temp_harm_behavior
                    continue
                else:
                    print(f"\n******* Exceeded the maximum number of iterations {iter_max}, adopt the current round results and end the loop.*******\n")
                    # save the data
                    item = {}
                    item['idx']  = idx
                    item['original_harm_behavior']  = temp_harm_behavior
                    item['rewrite_model']  = attack_parameter.model_name
                    item['operation_functions'] = [operations[i].__name__ for i in operation_indexes]
                    item['rewrite_track'] = temp_rewrite_results
                    item['rewritten_prompt']  = harm_behavior
                    item['nested_prompt']  = nested_prompt
                    item['judge_model']  = attack_parameter.model_name
                    item['attack_model']  = attack_parameter.model_name
                    item['attack_output']  = attack_output
                    item['model_label'] = "0"
                    item['iteration_count']  = loop_count
                    data_list.append(item)

                    break

            if jailbreak_label == "1":
                print(f"\n******* Jailbreaking idx {idx} Prompt Successful! *******\n")
                # save the data
                item = {}
                item['idx']  = idx
                item['original_harm_behavior']  = temp_harm_behavior
                item['rewrite_model']  = attack_parameter.model_name
                item['operation_functions'] = [operations[i].__name__ for i in operation_indexes]
                item['rewrite_track'] = temp_rewrite_results
                item['rewritten_prompt']  = harm_behavior
                item['nested_prompt']  = nested_prompt
                item['judge_model']  = attack_parameter.model_name
                item['attack_model']  = attack_parameter.model_name
                item['attack_output']  = attack_output
                item['model_label'] = "1"
                item['iteration_count']  = loop_count
                

                end_time = time.time()  
                elapsed_time = end_time - start_time  
                item['time_cost'] = elapsed_time

                data_list.append(item)

                break
            else:
                if loop_count < iter_max:
                    print(f"\nJailbreaking idx {idx} Prompt Failed!\n")
                    harm_behavior = temp_harm_behavior
                    continue
                else:
                    print(f"\n******* Exceeded the maximum number of iterations {iter_max}, adopt the current round results and end the loop.*******\n")
                    # save the data
                    item = {}
                    item['idx']  = idx
                    item['original_harm_behavior']  = temp_harm_behavior
                    item['rewrite_model']  = attack_parameter.model_name
                    item['rewrite_functions'] = [operations[i].__name__ for i in operation_indexes]
                    item['rewrite_track'] = temp_rewrite_results
                    item['rewritten_prompt']  = harm_behavior
                    item['nested_prompt']  = nested_prompt
                    item['judge_model']  = attack_parameter.model_name
                    item['attack_model']  = attack_parameter.model_name
                    item['attack_output']  = attack_output
                    item['model_label'] = "0"
                    item['iteration_count']  = loop_count
                    data_list.append(item)

                    break

    # save all data after jailbreaking.
    if not os.path.exists('../../results/renellm/final'):
        os.makedirs('../../results/renellm/final')
    file_name = f"../../results/renellm/final/judge_by_{attack_parameter.model_name}_attack_on_{attack_parameter.model_name}_{save_suffix}.json"

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

    file_path = os.path.abspath(file_name)
    print(f"\nThe final file has been saved to:\n{file_path}\n")
    return data_list
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # advbench
    parser.add_argument('--data_path', type=str, default='../../data/renellm/advbench/harmful_behaviors_test.csv')
    # your single prompt
    parser.add_argument('--prompt', type=str, default=None)
    parser.add_argument('--rewrite_model', type=str, default="gpt-3.5-turbo", choices=["gpt-3.5-turbo", "gpt-4"], help='model uesd for rewriting the prompt')
    parser.add_argument('--judge_model', type=str, default="gpt-3.5-turbo", choices=["gpt-3.5-turbo", "gpt-4"], help='model uesd for harmful classification')
    parser.add_argument('--attack_model', type=str, default="anthropic.claude-v2", choices=["anthropic.claude-v2", "gpt-4"], help='model to be attacked')
    parser.add_argument('--iter_max', type=int, default=10, help='max iteration times')
    parser.add_argument("--max_tokens", type=int, default=10086)
    parser.add_argument('--temperature', type=float, default=0, help='model temperature')
    parser.add_argument('--round_sleep', type=int, default=1, help='sleep time between every round')
    parser.add_argument('--fail_sleep', type=int, default=1, help='sleep time for fail response')
    parser.add_argument('--retry_times', type=int, default=1000, help='retry times when exception occurs')
    parser.add_argument('--save_suffix', type=str, default='normal')
    parser.add_argument("--gpt_api_key",type=str, default=None)
    parser.add_argument("--gpt_base_url", type=str, default=None)
    parser.add_argument("--claude_api_key", type=str, default=None)
    parser.add_argument("--claude_base_url", type=str, default=None)

    args = parser.parse_args()

    renellm(args)
