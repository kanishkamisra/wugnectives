premise1 = """Jessica said, "After blicketbash happened, daxday occurred." From this, which event started first? Answer either with daxday or blicketbash and nothing else. """
premise2 = """Estimate the number of boxes on earth"""
premise3 = """Estimate the number of boxes on the moon"""
premise4 = """Estimate the number of boxes on the jupiter"""
premise5 = """Estimate the number of boxes on the mars"""
tag = """Please reason step by step, and put your final answer within \\\boxed{}."""

prompt1 = premise1 + tag
prompt2 = premise2 + tag
prompt3 = premise3 + tag
prompt4 = premise4 + tag
prompt5 = premise5 + tag

batch_prompt_base = [prompt1, prompt2, prompt3, prompt4, prompt5, ]

from minicons import scorer
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
from torch.utils.data import DataLoader


cache_dir = "/home/shared/hf_cache"


# model_name = "Qwen/QwQ-32B"
model_name = "Qwen/Qwen2-0.5B-Instruct"
# model_name = "SummerSigh/Pythia410m-V0-Instruct"

# model_name = "EleutherAI/pythia-70m"

# bnb_config = BitsAndBytesConfig(
#             load_in_4bit=True,
#             bnb_4bit_use_double_quant=True,
#             bnb_4bit_quant_type="nf4",
#             bnb_4bit_compute_dtype=torch.bfloat16,
#         )

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    # torch_dtype="auto",
    # device_map="auto",
    torch_dtype="auto",
    device_map="auto",
    # quantization_config=bnb_config
)

tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left", cache_dir=cache_dir)
batch_prompts = []
for prompt in batch_prompt_base:
    messages = [
        {"role": "user", "content": prompt}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    batch_prompts.append(text)

batches = DataLoader(batch_prompts, batch_size=len(batch_prompts))

from tqdm import tqdm

results = []
all_responses = []
print("running model")
for batch in tqdm(batches):
    tokenizer.pad_token = tokenizer.eos_token

    model_inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True,
                       ).to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=25
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    responses = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    # print(prompt)
    # print(response)

    print("for all responses")
    print(responses)
    print("=====")
    for response in responses:
        try:
            idx = response.rindex("\\boxed{")
            boxed = response[idx:]
        except:
            boxed = "ERROR"
        
        results.append(("i", boxed))
        all_responses.append(("i", text, response))

    # results.append(("i", boxed))
    # responses.append(("i", text, response))


print(results)
