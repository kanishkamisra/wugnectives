import argparse
import itertools
import pathlib
import random
import utils

import config

from collections import defaultdict
from string import Template

NAMES = [
    "Emily",
    "Lucy",
    "Adam",
    "John",
    "Cameron",
    "Erica",
    "Megan",
    "Kyle",
    "Jessy",
    "Daniel",
]


def main(args):
    stimuli_dir = args.stimuli_dir
    random.seed(1024)

    stimuli_types = {}
    if args.category == "all":
        stimuli_types = {
            "preference": f"{stimuli_dir}/preference_stimuli.csv",
            "temporal": f"{stimuli_dir}/temporal_stimuli.csv",
            "instantiation": f"{stimuli_dir}/instantiation_stimuli.csv",
        }
    elif args.category == "preference":
        stimuli_types = {
            "preference": f"{stimuli_dir}/preference_stimuli.csv",
        }
    elif args.category == "temporal":
        stimuli_types = {
            "temporal": f"{stimuli_dir}/temporal_stimuli.csv",
        }
    elif args.category == "instantiation":
        stimuli_types = {
            "preference": f"{stimuli_dir}/preference_stimuli.csv",
            "temporal": f"{stimuli_dir}/temporal_stimuli.csv",
            "instantiation": f"{stimuli_dir}/instantiation_stimuli.csv",
        }
    else:
        raise ValueError(
            "category must be 'preference', 'temporal', or 'instantiation'. Received: ",
            args.category,
        )

    prompts = []
    idx = 0

    for (
        stimuli_type,
        stimuli_path,
    ) in stimuli_types.items():
        stimuli = utils.read_csv_dict(stimuli_path)
        templates = config.DISQ_QUESTIONS

        for t_id, template in enumerate(templates):
            random.shuffle(NAMES)
            names = itertools.cycle(NAMES)
            for name, item in zip(names, stimuli):
                style = item["style"]
                prompt = template.substitute(
                    name=name, premise=item["premise"], question=item["disq_premise"]
                )

                label_space = "Yes/No"
                label = "Yes"
                if "counterfactual" in style:
                    label = "No"

                prompts.append(
                    {
                        "idx": idx,
                        "item": item["item_id"],
                        "stimuli_type": stimuli_type,
                        "connective": item["connective"],
                        "target": item["target"],
                        "stimuli_instance_description": item[
                            "stimuli_instance_description"
                        ],
                        "style":item["style"],
                        "counterfactual_index":item["counterfactual_index"],
                        "stimuli_instance": item["stimuli_instance"],
                        "entity1": item["entity1"],
                        "entity2": item["entity2"],
                        "prompt": prompt,
                        "prompt_template": f"prompt_{t_id}",
                        "label_space": label_space,
                        "label": label,
                    }
                )

                idx += 1
    
    pathlib.Path(args.out_dir).mkdir(exist_ok=True, parents=True)
    utils.write_dict_list_to_csv(prompts, f"{args.out_dir}/{args.outfile}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stimuli_dir", type=str, default="data/disq-stimuli-nonce")
    parser.add_argument("--out_dir", type=str, default="data/disq-stimuli-nonce/")
    parser.add_argument("--outfile", type=str, default="disq_prompts")
    parser.add_argument("--category", type=str, default="all")
    args = parser.parse_args()
    main(args)
