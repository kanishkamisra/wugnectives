import csv
import itertools
import pathlib
import random
import config
import connectives
import entities
import generators
from disq import Disq, detect_sense, detect_occurs
from collections import defaultdict

preferences = connectives.PREFERENCE_TEMPLATES
temporals = connectives.TEMPORAL_TEMPLATES
instances = connectives.INSTANTIATION_TEMPLATES

with open("data/properties.csv", "r") as f:
    reader = csv.DictReader(f)
    properties = list(reader)


# write to csv
def write_stimuli(
    dataset,
    filename,
    header=[
        "item_id",
        "stimuli_type",
        "connective",
        "target",
        "stimuli_instance",
        "stimuli_instance_description",
        "entity1",
        "entity2",
        "premise",
        "style",  # targeted, converse, counterfactual, or converse-counterfactual
        "counterfactual_index",
        "disq_premise",
        "label"
    ],
):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(dataset)

temporal_cause_conns = ["as a result", "because", "consequently", "hence", "since", "so", "then", "therefore", ]
temporal_deny_conns = ["even though"]



def nonce_stim_to_disq(path, family):
    with open(path) as f:
        reader = csv.DictReader(f)
        dataset = []

        for row in reader:
            item_id = row["item_id"]
            stimuli_type = row["stimuli_type"]
            connective = row["connective"]
            target = row["target"]
            stimuli_instance = row["stimuli_instance"]
            entity1 = row["entity1"]
            entity2 = row["entity2"]
            premise = row["premise"]

            sense = detect_sense(premise)
            stimuli_instance_description = ""

            mapping = {
                "[e1]": entity1,
                "[e2]": entity2,
            }
            
            if family == "instantiation":
                mapping["Is "] = "Are "
            
            if family == "preference":
                stimuli_instance_description = row["stimuli_instance_description"]
                mapping["[property]"] = row["stimuli_instance_description"]
                mapping["[pref-verb]"] = target

            if family == "temporal":
                occur1, occur2 = detect_occurs(premise)
                mapping["occur_1"] = occur1
                mapping["occur_2"] = occur2
            

            disq = Disq(premise, sense, family)
            disq.format(mapping)

            counterfactual_index = 0
            converse_counterfactual_index = 0

            for question, style in disq.items():
                count = -1
                label = "Yes"
                if style == "converse_counterfactual":
                    label = "No"
                    count = converse_counterfactual_index
                    converse_counterfactual_index += 1
                if style == "counterfactual":
                    label = "No"
                    count = counterfactual_index
                    counterfactual_index += 1
                
                skip_casual = (family == "temporal") and (connective in temporal_cause_conns) and (("reason" in question) or ("result" in question))
                skip_denier = (family == "temporal") and (connective in temporal_deny_conns) and ("contradict" in question)
                skip = skip_casual or skip_denier

                if not skip:
                    dataset.append(
                        (
                            item_id,
                            stimuli_type,
                            connective,
                            target,
                            stimuli_instance,
                            stimuli_instance_description,
                            entity1,
                            entity2,
                            premise,
                            style,
                            count,
                            question,
                            label
                        )
                    )

        return dataset


stim_path = "data/stimuli-nonce/{}_stimuli.csv"

family = "instantiation"
inst_dataset = nonce_stim_to_disq(stim_path.format(family), family)

family = "temporal"
temporal_dataset = nonce_stim_to_disq(stim_path.format(family), family)

family = "preference"
pref_dataset = nonce_stim_to_disq(stim_path.format(family), family)


PATH = "data/disq-stimuli-nonce"
pathlib.Path(PATH).mkdir(parents=True, exist_ok=True)
write_stimuli(pref_dataset, f"{PATH}/preference_stimuli.csv")
write_stimuli(temporal_dataset, f"{PATH}/temporal_stimuli.csv")
write_stimuli(inst_dataset, f"{PATH}/instantiation_stimuli.csv")
