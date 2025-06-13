import csv
import itertools
import pathlib
import random

import config
import connectives as connectives
import entities
import generators


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


if "__main__" == __name__:
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
        # pref_verb = random.sample(["love", "hate"], 1)[0]
        pref_verbs = ["love"] * int(len(properties) / 2) + ["hate"] * int(
            len(properties) / 2
        )
        random.shuffle(pref_verbs)
        object_pairs = list(itertools.combinations(entities.OBJECTS, 2))
        location_pairs = list(itertools.combinations(entities.LOCATIONS, 2))
        random.shuffle(object_pairs)
        random.shuffle(location_pairs)
        for i, prop in enumerate(properties):
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
                pref_verbs[i],
                prop["property"],
                prop["inference_phrase"],
            ).generate_inference_pair("")

            pref_dataset.append(
                (
                    item_id,
                    "preference",
                    connective,
                    pref_verbs[i],
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
        orders = ["before"] * len(properties) + ["after"] * len(properties)
        random.shuffle(orders)
        event_pairs = list(itertools.combinations(entities.EVENTS, 2))
        random.shuffle(event_pairs)
        for i in range(len(properties)):
            e1, e2 = event_pairs[i]
            sampled_template = random.sample(template, 1)[0]

            order = orders[i]
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
        action_pairs = list(itertools.combinations(entities.ACTIONS, 2))
        random.shuffle(action_pairs)
        for i in range(len(properties)):
            e1, e2 = action_pairs[i]
            sampled_template = random.sample(template, 1)[0]

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

    # instantiation connectives
    inst_dataset = []

    item_id = 1
    for connective, template in connectives.INSTANTIATION_TEMPLATES.items():
        object_pairs = list(itertools.combinations(entities.OBJECTS, 2))
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
                )
            )

            item_id += 1

        PATH = "data/stimuli-new"
        pathlib.Path(PATH).mkdir(parents=True, exist_ok=True)
        write_stimuli(pref_dataset, f"{PATH}/preference_stimuli.csv")
        write_stimuli(temporal_dataset, f"{PATH}/temporal_stimuli.csv")
        write_stimuli(causal_dataset, f"{PATH}/causal_stimuli.csv")
        write_stimuli(inst_dataset, f"{PATH}/instantiation_stimuli.csv")
