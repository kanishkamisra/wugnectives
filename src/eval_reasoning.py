
import argparse
import pathlib
from minicons import scorer
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
from tqdm import tqdm
import utils

def main(args):
    try:
        tag = """Please reason step by step, and put your final answer within \\boxed{}."""

        results_dir = args.results_dir

        model_name = "Qwen/QwQ-32B"

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

        eval = utils.read_csv_dict(eval_path)



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

        batches = DataLoader(batch_prompts, batch_size=8)
        results = []
        all_responses = []
        for i, batch in tqdm(enumerate(batches),desc="Running...", total=len(batches)):

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


    except Exception as e:
        print (e)
        pass
    finally:
        print("writing to files...")
        pathlib.Path(results_dir).mkdir(parents=True, exist_ok=True)
        model_name = model_name.replace("/", "_")
        utils.write_csv(results, f"{results_dir}/{model_name}_reason.csv", header=["idx", "answer"])
        utils.write_csv(all_responses, f"{results_dir}/{args.prefix}{model_name}_responses.csv", header=["idx", "reasoning"])



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=str, default="data/results/nonce/")
    parser.add_argument("--eval_path", type=str, default="data/stimuli-nonce/prompts.csv")
    parser.add_argument("--prefix", type=str, default="")

    args = parser.parse_args()

    main(args)