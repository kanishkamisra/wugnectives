import csv
import pathlib

old_pref_len = 3600
new_pref_len = 9600

path = "data/results/nonce/allenai_OLMo-2-1124-7B.csv"
pref_path = "data/results/nonce/pref_allenai_OLMo-2-1124-7B.csv"
changed_pref_path = "data/results/nonce/pref_changed_allenai_OLMo-2-1124-7B.csv"

prompt_path = "data/stimuli-nonce/prompts.csv"
pref_prompt_path = "data/stimuli-nonce/pref_prompts.csv"

def write_csv(dict_list, path, header=None):
    fieldnames = dict_list[0].keys()  # Assuming all dictionaries have the same keys

    with open(path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the data
        writer.writerows(dict_list)



def is_def_entailed(row):
    comparison = ["although", "but", "even though", "nevertheless", "though", "while", "yet", "despite that", "however", "as much as"]
    contingency = [ "therefore", "thus", "as a result", "since", "so", "as", "for example", "for instance", "for", "because"]

    # print(row["connective"], row["target"], row["label"])

    if row["connective"] in comparison:
        if row["target"] == "hate":
            if row["label"] == "Yes":
                return True
        else:
            if row["label"] == "No":
                return True

    if row["connective"] in contingency:
        if row["target"] == "love":
            if row["label"] == "Yes":
                return True
        else:
            if row["label"] == "No":
                return True
            
    return False

with open(prompt_path, newline='') as prompt:
    promptreader = csv.DictReader(prompt)

    _no_pref_prompts = [row for row in promptreader if not row["stimuli_type"] == "preference"]
    no_pref_prompts = []
    for row in _no_pref_prompts:
        row["entailed"] = True
        no_pref_prompts.append(row)



with open(pref_prompt_path, newline='') as pref_prompt:
    prefprompt_reader = csv.DictReader(pref_prompt)
    _pref_prompts = [row for row in prefprompt_reader]
    
    pref_prompts = []
    for row in _pref_prompts:
        row["entailed"] = is_def_entailed(row)
        pref_prompts.append(row)


all_prompts = []
all_prompts.extend(no_pref_prompts)
all_prompts.extend(pref_prompts)

for idx, row in enumerate(all_prompts):
    row["idx"] = idx

write_csv(all_prompts, "data/stimuli-nonce/all_prompts.csv")