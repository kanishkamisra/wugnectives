import csv
import itertools
import pathlib
import random

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


random.seed(42)

pref_dataset = []
template = defaultdict(set)

# critical concept is still e1

x = 0
bad = []

item_id = 1
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
                item_id += 1
                x += 1
            except:
                bad.append((connective, verb))

temporal_dataset = []

item_id = 1
for connective, template in connectives.TEMPORAL_TEMPLATES.items():
    orders = ["before"] * len(properties) + ["after"] * len(properties)
    random.shuffle(orders)
    event_pairs = list(itertools.combinations(entities.EVENTS, 2))
    random.shuffle(event_pairs)
    for i in range(len(properties)):
        e1, e2 = event_pairs[i]
        sampled_template = random.sample(template, 1)[0]

        occur_list = connectives.OCCUR_VERBS 
        occur_1, occur_2 = random.sample(occur_list, 2)

        order = orders[i]
        premise, inference1, inference2 = generators.TemporalPremise(
            e1, e2, sampled_template, order, 
        ).generate_inference_pair("", occur_1=occur_1, occur_2=occur_2)

        label = config.TEMPORAL_RULES[connective]
        if label == "e1":
            label = e1
        elif label == "e2":
            label = e2

        temporal_dataset.append(
            (
                item_id,
                "temporal",
                connective,
                order,
                i + 1,
                "",
                e1,
                e2,
                premise,
                inference1,
                inference2,
                label,
            )
        )
        item_id += 1

inst_dataset = []

item_id = 1
for connective, template in connectives.INSTANTIATION_TEMPLATES.items():
    object_pairs = list(itertools.combinations(entities.OBJECTS, 2))
    selected = [0, 1]
    for selection in selected:
        for i in range(len(properties)):
            e1, e2 = object_pairs[i]
            sampled_template = random.sample(template, 1)[0]

            premise, inference1, inference2 = generators.InstantiationPremise(
                e1, e2, sampled_template
            ).generate_inference_pair("")

            inst_dataset.append(
                (
                    item_id,
                    "instantiation",
                    connective,
                    "are",
                    i + 1,
                    "",
                    e1,
                    e2,
                    premise,
                    inference1,
                    inference2,
                    selection,
                )
            )

            item_id += 1

PATH = "data/stimuli-nonce"
pathlib.Path(PATH).mkdir(parents=True, exist_ok=True)
# write_stimuli(pref_dataset, f"{PATH}/preference_stimuli.csv")
write_stimuli(temporal_dataset, f"{PATH}/temporal_stimuli.csv")
# write_stimuli(inst_dataset, f"{PATH}/instantiation_stimuli.csv")
