import argparse
import pathlib
import config
import torch
import utils

from string import Template
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
from minicons import scorer
from tqdm import tqdm

OPTIONS = ["Yes", "No", "yes", "no"]

def chat_template(sentence, tok, response_prompt=None):
    """
    A function that applies the model's chat template to simulate
    an interaction environment. Two possible options
    """
    if response_prompt is None:
        return tok.apply_chat_template(
            [
                {"role": "user", "content": sentence},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
    else:
        return tok.apply_chat_template(
            [
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": response_prompt},
            ],
            tokenize=False,
            continue_final_message=True,
        )


# def dialog_template(name1, name2, preamble, response_prompt=None):
#     substituted = TEMPLATE.substitute(name1=name1, name2=name2, preamble=preamble)
#     if response_prompt is None:
#         return substituted
#     else:
#         return f"{substituted}{response_prompt}"


def main(args):
    model = args.model
    results_dir = args.results_dir
    eval_path = args.eval_path
    instruct = args.instruct
    model_name = model.replace("/", "_")

    if "llama" in model_name.lower():
        model_family = "llama"
    elif "olmo-2" in model_name.lower():
        model_family = "olmo2"
    elif "qwen" in model_name.lower():
        model_family = "qwen"

    nonce_options = {
        "llama": {
            "gextravaganza": ["g", "G"],
            "daxday": ["d", "D"],
            "wugfest": ["w", "W"],
            "blicketbash": ["blick", "Blick"],
            "fepfestival": ["f", "F"],
        },
        "olmo2": {
            "gextravaganza": ["g", "G"],
            "daxday": ["d", "D"],
            "wugfest": ["w", "W"],
            "blicketbash": ["blick", "Blick"],
            "fepfestival": ["f", "F"],
        },
        "qwen": {
            "gextravaganza": ["g", "G"],
            "daxday": ["d", "D"],
            "wugfest": ["w", "W"],
            "blicketbash": ["b", "B"],
            "fepfestival": ["f", "F"],
        },
    }

    nonce_options = nonce_options[model_family]

    label_nonces = {vv: k for k, v in nonce_options.items() for vv in v}


    def get_label_space(entity1, entity2):
        return nonce_options[entity1] + nonce_options[entity2]


    def p_yes(probs):
        alls = torch.tensor(probs).sum(1)
        yeses = [[p[0], p[2]] for p in probs]
        return (torch.tensor(yeses).sum(1) / alls).tolist()


    def label_prob(probs):
        alls = torch.tensor(probs).sum(1)
        firsts = [[p[0], p[1]] for p in probs]
        return (torch.tensor(firsts).sum(1) / alls).tolist()

    def get_predictions(probs, label_space):
        readjusted = []
        for p in label_prob(probs):
            readjusted.append([p, 1-p])
        readjusted = torch.tensor(readjusted)
        preds = readjusted.argmax(1).tolist()
        predictions = []
        for i, (l, p) in enumerate(zip(preds, readjusted)):
            predictions.append((label_space[i][l], p[l].item()))

        return predictions

    # load the model
    lm = scorer.IncrementalLMScorer(model, device=args.device, trust_remote_code=True, use_auth_token=True)

    eval = utils.read_csv_dict(eval_path)

    eval_non_temporal = []
    eval_temporal = []
    for item in eval:
        if args.instruct:
            item.update({"input": chat_template(item["prompt"], lm.tokenizer)})
        else:
            item.update({"input": f'{item["prompt"]} Answer:'})
        if item["stimuli_type"] != "temporal":
            eval_non_temporal.append(item)
        else:
            eval_temporal.append(item)

    print("Non Temporal:")
    print([x["input"] for x in eval_non_temporal[:5]])

    print("Temporal:")
    print([x["input"] for x in eval_temporal[:5]])

    end = (577 + 369 + 134) * 8
    non_temporal_batches = DataLoader(eval_non_temporal[:end], batch_size=args.batch_size)
    temporal_batches = DataLoader(eval_temporal, batch_size=args.batch_size)

    results = []
    for batch in tqdm(non_temporal_batches):
        idx = batch["idx"]
        inputs = batch["input"]

        label_space = [OPTIONS] * len(inputs)

        dist = lm.next_word_distribution(inputs)
        probs, ranks = lm.query(dist, queries=label_space)

        yes_p = p_yes(probs)
        
        for i, p in zip(idx, yes_p):
            if p >= 0.5:
                l = "Yes"
            else:
                l = "No"
            results.append((i, p, l))

    for batch in tqdm(temporal_batches):
        idx = batch["idx"]
        inputs = batch["input"]
        entity1 = batch["entity1"]
        entity2 = batch["entity2"]
        label_space = [get_label_space(e1, e2) for e1, e2 in zip(entity1, entity2)]
        readj_space = [(e1,e2) for e1, e2 in zip(entity1, entity2)]

        dist = lm.next_word_distribution(inputs)
        probs, ranks = lm.query(dist, queries=label_space)

        preds = get_predictions(probs, readj_space)

        for i, (l, p) in zip(idx, preds):
            results.append((i, p, l))
        

    pathlib.Path(results_dir).mkdir(parents=True, exist_ok=True)
    utils.write_csv(results, f"{results_dir}/{args.out_prefix}{model_name}.csv", header=["idx", "prob", "label"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument("--results-dir", type=str, default="data/results/nonce/")
    parser.add_argument(
        "--eval_path", type=str, default="data/stimuli-nonce/prompts.csv"
    )
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--instruct", action="store_true")
    parser.add_argument("--device", type=str, default="cuda:0")

    parser.add_argument("--out_prefix", type=str, default="")

    args = parser.parse_args()

    main(args)
