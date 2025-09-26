import csv
import argparse


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


def write_csv(dict_list, path):
    with open(path, "w", newline="") as csvfile:
        fieldnames = dict_list[0].keys()  # Assuming all dictionaries have the same keys
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()


        # print(dict_list[:4])
        # Write the data
        writer.writerows(dict_list)

def main(model):
    old_pref_len = 3600
    new_pref_len = 9600



    # model = "allenai_OLMo-2-1124-7B"

    path = "data/results/nonce/" + model + ".csv"
    pref_path = "data/results/nonce/pref_" + model + ".csv"
    changed_pref_path = "data/results/nonce/pref_changed_" + model + ".csv"

    pref_prompt_path = "data/stimuli-nonce/pref_prompts.csv" 
    all_prompt_path = "data/stimuli-nonce/all_prompts.csv"
    entail_prompt_path = "data/stimuli-nonce/entailed_prompts.csv"

    old_pref_len = 3600


    with open(path, newline='') as data:
        datareader = list(csv.DictReader(data))

        non_pref = datareader[old_pref_len:]

    non_pref_entail = [True] * len(non_pref)


    with open(pref_path) as pref_data:
        with open(changed_pref_path) as eq_pref_data:
            with open(pref_prompt_path) as all_prompt:
                prefdata_reader = csv.DictReader(pref_data)
                eqprefdata_reader = csv.DictReader(eq_pref_data)
                promptreader = csv.DictReader(all_prompt)
            
                pref_entail = []
                all_pref = []

                for row, prompt in zip(prefdata_reader, list(promptreader)):
                    item = row
                    if prompt["stimuli_instance_description"] == "equatorial climates":
                        item = dict(next(eqprefdata_reader))
                    all_pref.append((item))

                    pref_entail.append(is_def_entailed(prompt))


    all_entails = []
    all_entails.extend(non_pref_entail)
    all_entails.extend(pref_entail)

    all_prompts = []
    all_prompts.extend(non_pref)
    all_prompts.extend(all_pref)

    for e, row in zip(all_entails, all_prompts):
        row["entailed"] = e

    write_csv(all_prompts, f"data/results/all/{model}.csv")



# This relies on them already having answers aggragated into one file per stimuli category
def stitch_lrm():
    model = "lrm"
    inst_path = "data/results/nonce/" + model + "_inst_answers.csv"
    pref_path = "data/results/nonce/" + model + "_pref_answers.csv"
    temp_path = "data/results/nonce/" + model + "_temp_answers.csv"
    changed_pref_path = "data/results/nonce/" + model + "_pref_changed_answers.csv"


    with open(temp_path, newline='') as data:
        temp = list(csv.DictReader(data))
    temp_entail = [True] * len(temp)

    with open(inst_path, newline='') as data:
        inst = list(csv.DictReader(data))
    inst_entail = [True] * len(inst)


    pref_entail = []
    pref_prompt_path = "data/stimuli-nonce/pref_prompts.csv" 
    with open(pref_path) as pref_data:
        with open(changed_pref_path) as eq_pref_data:
            with open(pref_prompt_path) as all_prompt:
                prefdata_reader = csv.DictReader(pref_data)
                eqprefdata_reader = csv.DictReader(eq_pref_data)
                promptreader = csv.DictReader(all_prompt)
            
                pref = []

                for row, prompt in zip(prefdata_reader, list(promptreader)):
                    item = row
                    if prompt["stimuli_instance_description"] == "equatorial climates":
                        item = dict(next(eqprefdata_reader))
                        item["label"] = row["label"]
                    
                    pref.append((item))
                    pref_entail.append(is_def_entailed(prompt))
                    if is_def_entailed(prompt) is None: 
                        print(prompt["connective"], prompt["target"], prompt["label"])



    all = []
    all.extend(temp)
    all.extend(inst)
    all.extend(pref)

    all_entails = []
    all_entails.extend(temp_entail)
    all_entails.extend(inst_entail)
    all_entails.extend(pref_entail)


    for e, row in zip(all_entails, all):
        row["entailed"] = e
    
    write_csv(all, f"data/results/all/{model}.csv")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="all")

    args = parser.parse_args()

    if args.model == "lrm":
        stitch_lrm()
    elif args.model == "all":
        models = (
            "meta-llama_Meta-Llama-3.1-8B-Instruct", "Qwen_Qwen2.5-0.5B-Instruct", "Qwen_Qwen2.5-1.5B-Instruct", "Qwen_Qwen2.5-3B-Instruct", "Qwen_Qwen2.5-7B-Instruct", "allenai_OLMo-2-1124-7B-Instruct", "allenai_OLMo-2-0425-1B-Instruct",
            "meta-llama_Meta-Llama-3.1-8B", "Qwen_Qwen2.5-0.5B", "Qwen_Qwen2.5-1.5B", "Qwen_Qwen2.5-3B", "Qwen_Qwen2.5-7B", "allenai_OLMo-2-1124-7B", "allenai_OLMo-2-0425-1B",
            "Qwen_Qwen2.5-14B", "Qwen_Qwen2.5-14B-Instruct"
        )
        for model in models: 
            try:
                main(model)
            except:
                print("Error with " + model)

    else:
        main(args.model)