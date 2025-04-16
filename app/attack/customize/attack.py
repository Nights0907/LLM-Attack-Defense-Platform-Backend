from app.models import AttackParameter, attack_method_info

def custom_attack(attack_parameter: AttackParameter):

    # 获取自定义攻击方法对应的 prompt
    attack_method = attack_method_info.query.filter_by(attack_method_name=attack_parameter.attack_method).first()
    attack_method_prompt = attack_method.attack_method_prompt

    return attack_method_prompt
