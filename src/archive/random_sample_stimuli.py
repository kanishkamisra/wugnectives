import random
import csv

from collections import defaultdict


def read_csv_dict(file):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]
    
def write_csv_dict(lst, file):
    with open(file, "w") as f:
        writer = csv.DictWriter(f, fieldnames=lst[0].keys())
        writer.writeheader()
        writer.writerows(lst)

STIMULI = ["causal", "instantiation", "preference", "temporal"]


# read stimuli files and store per connective
connective_stimuli = defaultdict(list)

for stimuli in STIMULI:
    path = f"data/stimuli/{stimuli}_stimuli.csv"
    stimuli_data = read_csv_dict(path)
    for row in stimuli_data:
        connective_stimuli[(row["connective"], stimuli)].append(row)


# for each connective in each stimuli type, sample a single instance
random.seed(1024)

i = 1
random_sampled_stimuli = []
for (connective, stimuli), stimuli_list in connective_stimuli.items():
    sample = random.choice(stimuli_list)
    random_sampled_stimuli.append({
        "idx": i,
        "item": sample["item_id"],
        "connective": connective,
        "stimuli-type": stimuli,
        "premise": sample["premise"],
        "inference1": sample["inference1"],
        "inference2": sample["inference2"]
    })
    i+=1

# print(random_sampled_stimuli, len(random_sampled_stimuli))
# save to csv
write_csv_dict(random_sampled_stimuli, "data/random_sampled_stimuli.csv")
