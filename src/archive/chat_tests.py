import random
from minicons import scorer
import numpy as np
import pandas as pd
from model_prompter import *


lm = scorer.IncrementalLMScorer("google/gemma-2-9b-it", "cpu")

premise = "<premise>"
inference = "<inference>"

prompt_nonqa = "Given the following statement:\n" + premise + "\n\nProduce a valid conclusion: "
prompt_yn = "Given the following statement:\n" + premise + "\n\nIs it true that " + inference + "? Answer in the format 'Answer: [answer]'"


def _chat_template(sequence, tokenizer, post_text="Response:"):
    formatted = [{"role": "user", "content": sequence.strip()}]
    templated = tokenizer.apply_chat_template(
        formatted, tokenize=False, add_generation_prompt=True
    )
    reformatted = tokenizer.decode(
        tokenizer(templated, add_special_tokens=False).input_ids[1:]
    ) + f"{post_text}\n"
    return reformatted

formatted = _chat_template(prompt_nonqa, lm.tokenizer, post_text="")

print(formatted)
print("===========================")

formatted = _chat_template(prompt_yn, lm.tokenizer, post_text="Answer:")
print(formatted)
