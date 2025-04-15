from app.attack.jailbreakingllm.common import conv_template, extract_json
# from language_models import APILiteLLM, GPT
from app.attack.jailbreakingllm.language_models import GPT
from app.defense.defense import adapt_defense_method
from app.models import AttackParameter
from app.utils.renellm.llm_completion_utils import get_llm_responses_stream
from app.utils.renellm.log_utils import print_and_log


def load_attack_and_target_models(attack_model,attack_max_n_tokens,max_n_attack_attempts,category,evaluate_locally,target_model,target_max_n_tokens,jailbreakbench_phase):
    # create attack model and target model
    attackLM = AttackLM(model_name = attack_model,
                        max_n_tokens = attack_max_n_tokens,
                        max_n_attack_attempts = max_n_attack_attempts,
                        category = category,
                        evaluate_locally = evaluate_locally
                        )
    
    targetLM = TargetLM(model_name = target_model,
                        category = category,
                        max_n_tokens = target_max_n_tokens,
                        evaluate_locally = evaluate_locally,
                        phase = jailbreakbench_phase
                        )
    
    return attackLM, targetLM

def load_indiv_model(model_name, local = False, use_jailbreakbench=True):
    lm = GPT(model_name)
    return lm

class AttackLM():
    """
        Base class for attacker language models.
        
        Generates attacks for conversations using a language model. The self.model attribute contains the underlying generation model.
    """
    def __init__(self, 
                model_name: str, 
                max_n_tokens: int, 
                max_n_attack_attempts: int, 
                category: str,
                evaluate_locally: bool):
        
        self.model_name = model_name
        self.max_n_tokens = max_n_tokens
        self.max_n_attack_attempts = max_n_attack_attempts

        from app.attack.jailbreakingllm.config import ATTACK_TEMP, ATTACK_TOP_P
        self.temperature = ATTACK_TEMP
        self.top_p = ATTACK_TOP_P

        self.category = category
        self.evaluate_locally = evaluate_locally
        self.model = load_indiv_model(model_name, 
                                      local = evaluate_locally, 
                                      use_jailbreakbench=False # Cannot use JBB as attacker
                                      )
        self.initialize_output = self.model.use_open_source_model
        self.template = self.model_name

    def preprocess_conversation(self, convs_list: list, prompts_list: list[str]):
        # For open source models, we can seed the generation with proper JSON
        init_message = ""
        if self.initialize_output:
            
            # Initalize the attack model's generated output to match format
            if len(convs_list[0].messages) == 0:# If is first message, don't need improvement
                init_message = '{"improvement": "","prompt": "'
            else:
                init_message = '{"improvement": "'
        for conv, prompt in zip(convs_list, prompts_list):
            conv.append_message(conv.roles[0], prompt)
            if self.initialize_output:
                conv.append_message(conv.roles[1], init_message)
        openai_convs_list = [conv.to_openai_api_messages() for conv in convs_list]
        return openai_convs_list, init_message
        
    def _generate_attack(self,attack_parameter:AttackParameter, openai_conv_list: list[list[dict]], init_message: str):
        batchsize = len(openai_conv_list)
        indices_to_regenerate = list(range(batchsize))
        valid_outputs = [None] * batchsize
        new_adv_prompts = [None] * batchsize
        
        # Continuously generate outputs until all are valid or max_n_attack_attempts is reached
        for attempt in range(self.max_n_attack_attempts):
            # Subset conversations based on indices to regenerate
            convs_subset = [openai_conv_list[i] for i in indices_to_regenerate]
            # Generate outputs 
            outputs_list = self.model.batched_generate_attack(
                                                            attack_parameter.attack_model,
                                                            convs_subset,
                                                            self.temperature,
                                                            attack_parameter.retry_times
                                                       )
            # Check for valid outputs and update the list
            new_indices_to_regenerate = []
            for i, full_output in enumerate(outputs_list):
                orig_index = indices_to_regenerate[i]
                full_output = init_message + full_output + "}" # Add end brace since we terminate generation on end braces
                attack_dict, json_str = extract_json(full_output)
                if attack_dict is not None:
                    valid_outputs[orig_index] = attack_dict
                    new_adv_prompts[orig_index] = json_str
                else:
                    new_indices_to_regenerate.append(orig_index)
            
            # Update indices to regenerate for the next iteration
            indices_to_regenerate = new_indices_to_regenerate
            # If all outputs are valid, break
            if not indices_to_regenerate:
                break

        if any([output is None for output in valid_outputs]):
            raise ValueError(f"Failed to generate valid output after {self.max_n_attack_attempts} attempts. Terminating.")
        return valid_outputs, new_adv_prompts

    def get_attack(self, attack_parameter : AttackParameter,convs_list, prompts_list):
        """
        Generates responses for a batch of conversations and prompts using a language model. 
        Only valid outputs in proper JSON format are returned. If an output isn't generated 
        successfully after max_n_attack_attempts, it's returned as None.
        
        Parameters:
        - convs_list: List of conversation objects.
        - prompts_list: List of prompts corresponding to each conversation.
        
        Returns:
        - List of generated outputs (dictionaries) or None for failed generations.
        """
        assert len(convs_list) == len(prompts_list), "Mismatch between number of conversations and prompts."
        
        # Convert conv_list to openai format and add the initial message
        processed_convs_list, init_message = self.preprocess_conversation(convs_list, prompts_list)
        valid_outputs, new_adv_prompts = self._generate_attack(attack_parameter,processed_convs_list, init_message)

        for jailbreak_prompt, conv in zip(new_adv_prompts, convs_list):
            # For open source models, we can seed the generation with proper JSON and omit the post message
            # We add it back here
            if self.initialize_output:
                jailbreak_prompt += self.model.post_message
            conv.update_last_message(jailbreak_prompt)
        
        return valid_outputs

class TargetLM():
    """
        JailbreakBench class for target language models.
    """
    def __init__(self, 
            model_name: str, 
            category: str,
            max_n_tokens : int,
            phase: str,
            evaluate_locally: bool = False,
            use_jailbreakbench: bool = True,
            ):
        
        self.model_name = model_name
        self.max_n_tokens = max_n_tokens
        self.phase = phase
        self.use_jailbreakbench = use_jailbreakbench
        self.evaluate_locally = evaluate_locally

        from app.attack.jailbreakingllm.config import TARGET_TEMP,  TARGET_TOP_P
        self.temperature = TARGET_TEMP
        self.top_p = TARGET_TOP_P

        self.model = load_indiv_model(model_name, evaluate_locally, use_jailbreakbench)            
        self.category = category

    def get_response(self, attack_parameter : AttackParameter,prompts_list,goal,idx):

        user_input = prompts_list[0]

        if attack_parameter.defense_method != "":
            print_and_log(f"应用防御方法:{attack_parameter.defense_method}\n")
            final_question = adapt_defense_method(attack_parameter, user_input)
            print_and_log(f"最终提示词:\n{final_question}\n")
        else:
            final_question = user_input

        user_message = {"role": "user", "content": final_question}
        messages = [user_message]

        model_output = get_llm_responses_stream(attack_parameter.attack_model,messages,0,attack_parameter.retry_times)
        return model_output

