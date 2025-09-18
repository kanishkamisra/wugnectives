import argparse
import csv
import pathlib
import config
import utils


def main(args):
    prompts_path = args.in_prompts
    stimuli_path = args.stimuli_path
    num_templates = len(config.PREF_INSTANT_QUESTIONS) # same number for temporal
    with open(prompts_path, "r") as f:
        reader = csv.DictReader(f)
        prompts = list(reader)

        prompts = [prompt for prompt in prompts if prompt["stimuli_type"] == args.category]

    with open(stimuli_path, "r") as f:
        reader = csv.DictReader(f)
        stimuli = list(reader)

    for i in range(num_templates):
        new_prompts = prompts[i * len(stimuli): (i + 1) * (len(stimuli))] 

        pathlib.Path(args.out_dir).mkdir(exist_ok=True, parents=True)
        utils.write_dict_list_to_csv(new_prompts, f"{args.out_dir}/{args.outfile}{i}.csv")




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_prompts", type=str, default="data/stimuli-nonce/pref_prompts.csv")
    parser.add_argument("--stimuli_path", type=str, default="data/stimuli-nonce/preference_stimuli.csv")
    parser.add_argument("--out_dir", type=str, default="data/stimuli-nonce/split_pref/")
    parser.add_argument("--outfile", type=str, default="prompts_template_")
    parser.add_argument("--category", type=str, default="temporal")
    args = parser.parse_args()
    main(args)