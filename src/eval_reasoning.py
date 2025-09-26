
import argparse
import pathlib
from minicons import scorer
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
from tqdm import tqdm
import utils

def main(args):
        results_dir = args.results_dir

        # model_name = "Qwen/QwQ-32B"

        model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"

        bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16,
                )

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
            quantization_config=bnb_config
        )
        
        cache_dir = "/home/shared/hf_cache"
        tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left", cache_dir=cache_dir)

        eval_path = args.eval_path

        if eval_path == "all":
            all_inst = [utils.read_csv_dict(eval_path) for eval_path in pathlib.Path("data/stimuli-nonce/split_inst").glob("*.csv")]
            all_pref = [utils.read_csv_dict(eval_path) for eval_path in pathlib.Path("data/stimuli-nonce/split_pref").glob("*.csv")]
            all_temp = [utils.read_csv_dict(eval_path) for eval_path in pathlib.Path("data/stimuli-nonce/split_temp").glob("*.csv")]

            all_eval = [] 
            for inst, pref, temp in zip(all_inst, all_pref, all_temp):
                all_eval.append(inst)
                all_eval.append(pref)
                all_eval.append(temp)
            names = []
            for i, (inst, pref, temp) in enumerate(zip(all_inst, all_pref, all_temp)):
                names.append(f"inst{i}")
                names.append(f"pref{i}")
                names.append(f"temp{i}")

        elif pathlib.Path(eval_path).is_dir():
            all_eval = [utils.read_csv_dict(eval_path) for eval_path in pathlib.Path(eval_path).glob("*.csv")]
            names = [str(eval_path) for eval_path in pathlib.Path(eval_path).glob("*.csv")]
        else:
            all_eval = [utils.read_csv_dict(eval_path)]
            # names = [str(eval_path)]
            names = [""]



        for i, (name, eval) in enumerate(zip(names, all_eval)):
            try:
                batch_prompts = make_batch(tokenizer, eval)

                batches = DataLoader(batch_prompts, batch_size=8)
                results, all_responses = run_model(model, name, tokenizer, batches)
            finally:
                print("writing to files...")
                pathlib.Path(results_dir).mkdir(parents=True, exist_ok=True)
                model_name = model_name.replace("/", "_")
                utils.write_csv(results, f"{results_dir}/{args.prefix}{model_name}_reasons_{name}.csv", header=["idx", "answer"])
                utils.write_csv(zip(all_responses, batch_prompts), f"{results_dir}/{args.prefix}{model_name}_responses_{name}.csv", header=["idx", "reasoning","prompt"])





def make_batch(tokenizer, eval):
    tag = """Please reason step by step, and put your final answer within \\boxed{}."""

    batch_prompts = []
    for row in eval:
        messages = [
                {"role": "user", "content": row["prompt"]+ " " + tag}
            ]

        text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

        batch_prompts.append(text)
    return batch_prompts

def run_model(model, name, tokenizer, batches):
    results = []
    all_responses = []
    try:
        for i, batch in tqdm(enumerate(batches),desc=f"Running {name}...", total=len(batches)):
            model_inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True,
                        ).to(model.device)
                
            generated_ids = model.generate(
                    **model_inputs,
                    max_new_tokens=32768
                )
            generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]

            responses = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            for response in responses:
                try:
                    idx = response.rindex("\\boxed{")
                    boxed = response[idx:]
                except:
                    boxed = "ERROR"
                    
                results.append((i, boxed))
                all_responses.append((i, response))
    finally:
        return results, all_responses



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=str, default="data/results/nonce/")
    parser.add_argument("--eval_path", type=str, default="data/stimuli-nonce/prompts.csv")
    parser.add_argument("--prefix", type=str, default="")

    args = parser.parse_args()

    main(args)