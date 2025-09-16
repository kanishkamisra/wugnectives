import csv
import itertools
import pathlib
import random
import re

import config
import connectives
import entities
import generators

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
        "inference1",
        "inference2",
        "label",
    ],
):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(dataset)

def flip_label(label: str):
    if label.lower() == "yes":
        return "No"
    if label.lower() == "no":
        return "Yes"
    raise ValueError("Label must be Yes or No, got " + label)


random.seed(42)

pref_dataset = []
alt_inference_pref_dataset = []
template = defaultdict(set)

# critical concept is still e1
item_id = 1
x = 0
for connective, templates in connectives.PREFERENCE_TEMPLATES.items():
    pref_verbs = ["love", "hate"]
    object_pairs = list(itertools.combinations(entities.OBJECTS, 2))
    location_pairs = list(itertools.combinations(entities.LOCATIONS, 2))
    random.shuffle(object_pairs)
    random.shuffle(location_pairs)
    for i, prop in enumerate(properties):
        for verb in pref_verbs:
            # sample pairs of entities
            if prop["type"] == "objects":
                e1, e2 = object_pairs[i]
            elif prop["type"] == "locations":
                e1, e2 = location_pairs[i]

            # sample template
            sampled_template = random.sample(templates, 1)[0]
            premise, inference1, inference2 = generators.PreferencePremise(
                e1,
                e2,
                sampled_template,
                verb,
                prop["property"],
                prop["inference_phrase"],
            ).generate_inference_pair("")

            try:
                label = config.PREFERENCE_RULES[connective][verb]
            except:
                label = config.EXTRA_PREFERENCE_RULES[connective][verb]


            pref_dataset.append(
                (
                    item_id,
                    "preference",
                    connective,
                    verb,
                    prop["property_id"],
                    prop["property"],
                    e1,
                    e2,
                    premise,
                    inference1,
                    inference2,
                    label,
                )
            )

            alt_label = flip_label(label)
            alt_inference_pref_dataset.append(
                (
                    item_id,
                    "preference",
                    connective,
                    verb,
                    prop["property_id"],
                    prop["property"],
                    e1,
                    e2,
                    premise,
                    inference2,
                    inference1,
                    alt_label,
                )
            )

            item_id += 1
            x += 1

pref_dataset.extend(alt_inference_pref_dataset)

PATH = "data/stimuli-nonce"
pathlib.Path(PATH).mkdir(parents=True, exist_ok=True)
write_stimuli(pref_dataset, f"{PATH}/preference_stimuli.csv")

