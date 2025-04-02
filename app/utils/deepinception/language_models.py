import gc
import os
import time
from typing import Dict, List

import openai
import torch
from openai import OpenAI

from app.models import AttackParameter
from app.utils.renellm.llm_completion_utils import get_llm_responses


class LanguageModel():
    def __init__(self, model_name):
        self.model_name = model_name

    def batched_generate(self, prompts_list: List, max_n_tokens: int, temperature: float):
        """
        Generates responses for a batch of prompts using a language model.
        """
        raise NotImplementedError


class HuggingFace(LanguageModel):
    def __init__(self, model_name, model, tokenizer):
        self.model_name = model_name
        self.model = model
        self.tokenizer = tokenizer
        self.eos_token_ids = [self.tokenizer.eos_token_id]

    def batched_generate(self,
                         full_prompts_list,
                         max_n_tokens: int,
                         temperature: float,
                         top_p: float = 1.0, ):
        inputs = self.tokenizer(full_prompts_list, return_tensors='pt', padding=True)
        inputs = {k: v.to(self.model.device.index) for k, v in inputs.items()}

        # Batch generation
        if temperature > 0:
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_n_tokens,
                do_sample=True,
                temperature=temperature,
                eos_token_id=self.eos_token_ids,
                top_p=top_p,
            )
        else:
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_n_tokens,
                do_sample=False,
                eos_token_id=self.eos_token_ids,
                top_p=1,
                temperature=1,  # To prevent warning messages
            )

        # If the model is not an encoder-decoder type, slice off the input tokens
        if not self.model.config.is_encoder_decoder:
            output_ids = output_ids[:, inputs["input_ids"].shape[1]:]

        # Batch decoding
        outputs_list = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)

        for key in inputs:
            inputs[key].to('cpu')
        output_ids.to('cpu')
        del inputs, output_ids
        gc.collect()
        torch.cuda.empty_cache()

        return outputs_list

    def extend_eos_tokens(self):
        # Add closing braces for Vicuna/Llama eos when using attacker model
        self.eos_token_ids.extend([
            self.tokenizer.encode("}")[1],
            29913,
            9092,
            16675])


class GPT(LanguageModel):
    API_RETRY_SLEEP = 10
    API_ERROR_OUTPUT = "$ERROR$"
    API_QUERY_SLEEP = 2
    API_MAX_RETRY = 5
    API_TIMEOUT = 20

    def generate(self, attack_model : str,
                 conv: List[Dict],
                 temperature: float,
                 retry_times: int,
                 ):

        output = self.API_ERROR_OUTPUT

        for _ in range(self.API_MAX_RETRY):
            output = get_llm_responses(attack_model,conv,temperature,retry_times)
            break


        return output

    def batched_generate(self,
                         attack_model : str,
                         convs_list: List[List[Dict]],
                         temperature: float,
                         retry_times: int,
                         ):
        return [self.generate(attack_model,conv,temperature,retry_times) for conv in convs_list]
