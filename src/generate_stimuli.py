import csv
import pathlib
import random

import config
import connectives
import entities
import generators

# import properties


# Count the number of templates for each type of connective
preferences = connectives.PREFERENCE_TEMPLATES
temporals = connectives.TEMPORAL_TEMPLATES
causals = connectives.CAUSAL_TEMPLATES
asgoals = connectives.ASGOAL_TEMPLATES
instances = connectives.INSTANTIATION_TEMPLATES

pref = len(preferences.keys())
temporal = len(temporals.keys())
causal = len(causals.keys())
asgoal = len(asgoals.keys())
inst = len(instances.keys())

print(f"Preference: {pref}")
print(f"Temporal: {temporal}")
print(f"Causal: {causal}")
print(f"AsGoal: {asgoal}")
print(f"Instantiation: {inst}")
# print(f"Total: {pref + temporal + causal}")
print(f"Total: {pref + temporal + causal + asgoal + inst}")


# preference connectives
random.seed(42)

# read properties
with open("data/properties.csv", "r") as f:
    reader = csv.DictReader(f)
    properties = list(reader)

pref_dataset = []

item_id = 1
for connective, templates in connectives.PREFERENCE_TEMPLATES.items():
    for prop in properties:
        # sample pairs of entities
        if prop["type"] == "objects":
            e_space = entities.OBJECTS
        elif prop["type"] == "locations":
            e_space = entities.LOCATIONS

        e1, e2 = random.sample(e_space, 2)

        # sample template
        sampled_template = random.sample(templates, 1)[0]

        # preference verbs
        # for pref_verb in ["love", "hate"]:
        pref_verb = random.sample(["love", "hate"], 1)[0]
        premise, inference1, inference2 = generators.PreferencePremise(
            e1,
            e2,
            sampled_template,
            pref_verb,
            prop["property"],
            prop["inference_phrase"],
        ).generate_inference_pair("")

        pref_dataset.append(
            (
                item_id,
                "preference",
                connective,
                pref_verb,
                prop["property_id"],
                prop["property"],
                e1,
                e2,
                premise,
                inference1,
                inference2,
            )
        )

        item_id += 1

# temporal connectives
temporal_dataset = []

item_id = 1
for connective, template in connectives.TEMPORAL_TEMPLATES.items():
    for i in range(len(properties)):
        e1, e2 = random.sample(entities.EVENTS, 2)
        sampled_template = random.sample(template, 1)[0]
        # for order in ["before", "after"]:
        order = random.sample(["before", "after"], 1)[0]
        premise, inference1, inference2 = generators.TemporalPremise(
            e1, e2, sampled_template, order
        ).generate_inference_pair("")

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
            )
        )

        item_id += 1

# causal connectives
causal_dataset = []

item_id = 1
for connective, template in connectives.CAUSAL_TEMPLATES.items():
    for i in range(len(properties)):
        e1, e2 = random.sample(entities.ACTIONS, 2)
        sampled_template = random.sample(template, 1)[0]
        # for cause in ["because", "so"]:
        premise, inference1, inference2 = generators.CausalPremise(
            e1, e2, sampled_template
        ).generate_inference_pair("")

        causal_dataset.append(
            (
                item_id,
                "causal",
                connective,
                "causes",
                i + 1,
                "",
                e1,
                e2,
                premise,
                inference1,
                inference2,
            )
        )

        item_id += 1

# asgoal connectives
asgoal_dataset = []

item_id = 1

for connective, template in connectives.ASGOAL_TEMPLATES.items():
    for i in range(len(properties)):
        e1, e2 = random.sample(entities.ACTIONS_PRESENT_TENSE, 2)
        sampled_template = random.sample(template, 1)[0]
        premise, inference1, inference2 = generators.AsGoalPremise(
            e1, e2, sampled_template
        ).generate_inference_pair("")

        asgoal_dataset.append(
            (
                item_id,
                "asgoal",
                connective,
                "requires",
                i + 1,
                "",
                e1,
                e2,
                premise,
                inference1,
                inference2,
            )
        )

        item_id += 1

# instantiation connectives
inst_dataset = []

item_id = 1

for connective, template in connectives.INSTANTIATION_TEMPLATES.items():
    for i in range(len(properties)):
        e1, e2 = random.sample(entities.OBJECTS, 2)
        sampled_template = random.sample(template, 1)[0]
        premise, inference1, inference2 = generators.InstantiationPremise(
            e1, e2, sampled_template
        ).generate_inference_pair("")

        inst_dataset.append(
            (
                item_id,
                "instantiation",
                connective,
                "are a type of",
                i + 1,
                "",
                e1,
                e2,
                premise,
                inference1,
                inference2,
            )
        )

        item_id += 1
# print(pref_dataset)


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
    ],
):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(dataset)


pathlib.Path("data/stimuli").mkdir(parents=True, exist_ok=True)
write_stimuli(pref_dataset, "data/stimuli/preference_stimuli.csv")
write_stimuli(temporal_dataset, "data/stimuli/temporal_stimuli.csv")
write_stimuli(causal_dataset, "data/stimuli/causal_stimuli.csv")
write_stimuli(asgoal_dataset, "data/stimuli/asgoal_stimuli.csv")
write_stimuli(inst_dataset, "data/stimuli/instantiation_stimuli.csv")