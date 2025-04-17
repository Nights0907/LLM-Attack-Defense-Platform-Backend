import random

from app.models import AttackParameter
from app.utils.log_utils import print_and_log
from app.utils.renellm.prompt_rewrite_utils import shortenSentence, misrewriteSentence, changeOrder, addChar,languageMix, styleChange
from app.utils.renellm.scenario_nest_utils import SCENARIOS
from app.utils.harmful_classification_utils import harmful_classification


def renellm(attack_parameter: AttackParameter,data,idx):

    # 加载改写方法与嵌套场景
    operations = [shortenSentence, misrewriteSentence, changeOrder, addChar, languageMix, styleChange]  # 所有可用的改写操作
    scenarios = SCENARIOS  # 所有可用的场景模板

    # 存储最终输出信息
    global harm_behavior,final_prompt

    # 提示词改写阶段
    while True:
        print_and_log(f"\n************** 开始第 {idx+1} 个提示词的改写! **************\n")
        # 随机选择改写操作的数量
        n = random.randint(1, 6)
        # 随机排列操作顺序
        operation_indexes = random.sample(range(6), n)
        print_and_log(f"改写函数数量: {n}\n")
        print_and_log(f"改写操作顺序: {operation_indexes}\n")


        temp_rewrite_results = [['原始提示词', data]]  # 保存改写轨迹
        # 按顺序执行改写操作
        for index in operation_indexes:
            print_and_log(f"执行函数 {index}: {operations[index].__name__}\n")
            harm_behavior = operations[index](attack_parameter, data)
            print_and_log(f"改写后的提示词: {harm_behavior}\n")
            temp_rewrite_results.append([operations[index].__name__, harm_behavior])

        # 检查提示词是否已被改写为无害
        print_and_log("\n************** 检查提示词是否已被改写为无害 **************\n")
        label = harmful_classification(attack_parameter, harm_behavior)
        print_and_log(f"{attack_parameter.attack_model} 给出的标签是: {label}\n")

        if label == "1":  # 1表示有害
            print_and_log(f"\n************** 第 {idx+1} 个提示词改写完成! **************\n")
            break
        else:
            print_and_log(f"\n************** 第 {idx+1} 个提示词改写失败! **************\n")
            harm_behavior = data  # 恢复原始提示词
            continue

    # 场景嵌套阶段
    print_and_log(f"\n************** 开始第 {idx+1} 个提示词的场景嵌套! **************\n")
    print_and_log(f"有害行为:{data}\n")

    # 随机选择一个场景模板
    scenario = random.choice(scenarios)
    nested_prompt = scenario.replace("<>", harm_behavior)  # 将有害行为嵌入场景
    final_prompt = nested_prompt


    return final_prompt