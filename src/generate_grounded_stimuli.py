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

import utils

preferences = connectives.PREFERENCE_TEMPLATES
temporals = connectives.TEMPORAL_TEMPLATES
instances = connectives.INSTANTIATION_TEMPLATES

with open("data/properties.csv", "r") as f:
    reader = csv.DictReader(f)
    properties = list(reader)


with open("data/real_properties.csv", "r") as f:
    reader = csv.DictReader(f)
    real_properties = []
    for row in reader:
        real_properties.append({
            "property_id": int(row["property_id"]),
            "property": row["property"],
            "has_property": row["has_property"].split(";") if row["has_property"] else [],
            "not_property": row["not_property"].split(";") if row["not_property"] else [],
        })    


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


def needs_swap(verb, template):
    if verb == "hate" and "contingency" in utils.get_sense(template).lower():
        return True
    if verb == "love" and "comparison" in utils.get_sense(template).lower():
        return True
    return False


random.seed(42)

pref_dataset = []
template = defaultdict(set)

# critical concept is still e1

x = 0
bad = []

item_id = 20000
for connective, templates in connectives.PREFERENCE_TEMPLATES.items():
    pref_verbs = ["love", "hate"]
    for i, (prop, r_prop) in enumerate(zip(properties, real_properties)):
        for verb in pref_verbs:
            #e1 has property, e2, does not
            has_prop = r_prop["has_property"]
            not_prop = r_prop["not_property"]
            # random.shuffle(has_prop)
            # random.shuffle(not_prop)
            # has_prop = has_prop[:3]
            # not_prop = not_prop[:3]
            combos = list(itertools.product(has_prop, not_prop))
            random.shuffle(combos)
            combos = combos[:2]
            for e1, e2 in combos:
                # sample template
                sampled_template = random.sample(templates, 1)[0]

                if needs_swap(verb, sampled_template):
                    tmp = e1
                    e1 = e2
                    e2 = tmp

                premise, inference1, inference2 = generators.PreferencePremise(
                    e1,
                    e2,
                    sampled_template,
                    verb,
                    prop["property"],
                    prop["inference_phrase"],
                ).generate_inference_pair("")
                premise = premise.replace(",.", ".")
                
                try:
                    label = config.PREFERENCE_RULES[connective][verb]
                except:
                    label = config.EXTRA_PREFERENCE_RULES[connective][verb]
                finally:
                # except:
                #     bad.append((connective, verb))
                #     # label = config.EXTRA_PREFERENCE_RULES[connective][verb]
                # finally:
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


superset = [
    "birds",
    "mammals",
    "fruits",
    "string instruments",
    "insects",
    'fish',
]

subset_1 = [
    "sparrows",
    "cats",
    "grapes",
    "violins",
    "beetles",
    'tuna',
]

subset_2 = [
    "ravens",
    "dogs",
    "apples",
    "cellos",
    "grasshoppers",
    'salmon'
]

subset_3 = [
    "crows",
    "sheep",
    "pears",
    "violas",
    "ants",
    'trout'
]

inst_dataset = []
item_id = 1
for connective, template in connectives.INSTANTIATION_TEMPLATES.items():
    # object_pairs = list(itertools.combinations(entities.OBJECTS, 2))
    for subset in (subset_1, subset_2, subset_3):

        # for i in range(len(properties)):
        for e1, e2 in zip(superset, subset):
            sampled_template = random.sample(template, 1)[0]

            premise, inference1, inference2 = generators.InstantiationPremise(
                e1, e2, sampled_template
            ).generate_inference_pair("")
            for label in [0, 1]:
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
                        label,
                    )
                )

            item_id += 1



PATH = "data/stimuli-nonce"
pathlib.Path(PATH).mkdir(parents=True, exist_ok=True)
write_stimuli(pref_dataset, f"{PATH}/preference_stimuli_grounded.csv")
write_stimuli(inst_dataset, f"{PATH}/instantiation_stimuli_grounded.csv")
