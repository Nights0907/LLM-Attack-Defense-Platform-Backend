from app.defense.goal_priority import goal_priority
from app.defense.self_reminders import self_reminders
from app.models import AttackParameter


def adapt_defense_method(attack_parameter:AttackParameter,attack_prompt:str):
    given_defense_method = attack_parameter.defense_method
    if given_defense_method == "self_reminders":
        return self_reminders(attack_prompt)
    if given_defense_method == "goal_priority":
        return goal_priority(attack_prompt)