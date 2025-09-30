import csv
import connectives
import utils

senses = {
    "Although I prefer [e1] to [e2], I [pref-verb] [property].": "Comparison.Concession.Arg1-as-denier",
    "I prefer [e1] to [e2], although I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "Although I [pref-verb] [property], I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "I prefer [e1] to [e2], as I [pref-verb] [property].": "Contingency.Cause.Reason",
    "I prefer [e1] to [e2], as I [pref-verb] [property].": "Contingency.Cause.Reason",
    "After [e2] [occur], [e1] [occur].": "Temporal.Asynchronous.Succession",
    "[e1] [occur] after [e2] [occur].": "Temporal.Asynchronous.Succession",
    "I [pref-verb] [property]. As a result, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. As a result, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "As much as I [pref-verb] [property], I prefer [e1] to [e2].": "Comparison.Concession.Arg1-as-denier",
    "I prefer [e1] to [e2] because I [pref-verb] [property].": "Contingency.Cause.Reason",
    "[e1] [occur]. Afterwards, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "Because I [pref-verb] [property], I prefer [e1] to [e2].": "Contingency.Cause.Reason",
    "[e2] [occur] as a result of [e1].": "Temporal.Asynchronous.Precedence",
    "I prefer [e1] to [e2] because I [pref-verb] [property].": "Contingency.Cause.Reason",
    "Because I [pref-verb] [property], I prefer [e1] to [e2].": "Contingency.Cause.Reason",
    "I [pref-verb] [property]. But, I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "I prefer [e1] to [e2]. But, I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "I [pref-verb] [property], even though I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "[e1] [occur]. As a result, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "Even though I prefer [e1] to [e2], I [pref-verb] [property].": "Comparison.Concession.Arg1-as-denier",
    "I prefer [e1] to [e2], even though I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "Even though I [pref-verb] [property], I prefer [e1] to [e2].": "Comparison.Concession.Arg1-as-denier",
    "[e1] [occur] as soon as [e2] [occur].": "Temporal.Asynchronous.Succession",
    "I prefer [e1] to [e2], for I [pref-verb] [property].": "Contingency.Cause.Reason",
    "I prefer [e1] to [e2], for I [pref-verb] [property].": "Contingency.Cause.Reason",
    "I hate [e1]. For example, [e2] are awful.": "Expansion.Instantiation.Arg2-as-instance",
    "I [pref-verb] [property]. For example, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I like [e1]. For example, [e2] are nice.": "Expansion.Instantiation.Arg2-as-instance",
    "I [pref-verb] [property]. For example, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. For instance, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I hate [e1]. For instance, [e2] are awful.": "Expansion.Instantiation.Arg2-as-instance",
    "I like [e1]. For instance, [e2] are nice.": "Expansion.Instantiation.Arg2-as-instance",
    "I [pref-verb] [property]. For instance, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. However, I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "I prefer [e1] to [e2]. However, I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "I prefer [e1] to [e2], nevertheless, I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "I [pref-verb] [property], nevertheless, I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "I prefer [e1] to [e2], since I [pref-verb] [property].": "Contingency.Cause.Reason",
    "As soon as [e2] [occur], [e1] [occur].": "Temporal.Asynchronous.Succession",
    "Since I [pref-verb] [property], I prefer [e1] to [e2].": "Contingency.Cause.Reason",
    "Since I [pref-verb] [property], I prefer [e1] to [e2].": "Contingency.Cause.Reason",
    "I prefer [e1] to [e2], since I [pref-verb] [property].": "Contingency.Cause.Reason",
    "[e1] [occur] because [e2] [occur].": "Temporal.Asynchronous.Succession",
    "Because [e2] [occur], [e1] [occur].": "Temporal.Asynchronous.Succession",
    "I [pref-verb] [property]. So, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. So, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. Therefore, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. Therefore, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "Before [e2] [occur], [e1] [occur].": "Temporal.Asynchronous.Precedence",
    "I [pref-verb] [property], though I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "Though I [pref-verb] [property], I prefer [e1] to [e2].": "Comparison.Concession.Arg1-as-denier",
    "I prefer [e1] to [e2], though I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "Though I prefer [e1] to [e2], I [pref-verb] [property].": "Comparison.Concession.Arg1-as-denier",
    "I [pref-verb] [property]. Thus, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. Thus, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "While I prefer [e1] to [e2], I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "While I [pref-verb] [property], I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "I [pref-verb] [property], yet I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "I [pref-verb] [property]. Despite that, I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "I find [e1], in particular, [e2] to be cute.": "Expansion.Instantiation.Arg2-as-instance",
    "I find [e1], in particular, [e2] to be awful.": "Expansion.Instantiation.Arg2-as-instance",
    "I find [e1], specifically, [e2] to be awful.": "Expansion.Instantiation.Arg2-as-instance",
    "I find [e1], specifically, [e2] to be cute.": "Expansion.Instantiation.Arg2-as-instance",
    "I find [e1] such as [e2], to be cute.": "Expansion.Instantiation.Arg2-as-instance",
    "I find [e1] such as [e2], to be awful.": "Expansion.Instantiation.Arg2-as-instance",
    "[e1] [occur] before [e2].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur]. Consequently, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur]. Earlier, [e2] [occur].": "Temporal.Asynchronous.Succession",
    "[e1] [occur] even after [e2] [occur].": "Temporal.Asynchronous.Succession",
    "Even after [e2] [occur], [e1] [occur].": "Temporal.Asynchronous.Succession",
    "Even before [e1] [occur], [e2] [occur].": "Temporal.Asynchronous.Succession",
    "[e2] [occur] even before [e1] [occur].": "Temporal.Asynchronous.Succession",
    "[e1] [occur] even though [e2] [occur].": "Temporal.Asynchronous.Succession",
    "Even though [e2] [occur], [e1] [occur].": "Temporal.Asynchronous.Succession",
    "[e2] [occur]. Eventually, [e1] [occur].": "Temporal.Asynchronous.Succession",
    "[e1] [occur]. Finally, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur]. Hence, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur]. Later, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur]. Next, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "Once [e2] [occur], [e1] [occur].": "Temporal.Asynchronous.Succession",
    "[e1] [occur] once [e2] [occur].": "Temporal.Asynchronous.Succession",
    "[e1] [occur]. Previously, [e2] [occur].": "Temporal.Asynchronous.Succession",
    "Since [e2] [occur], [e1] [occur].": "Temporal.Asynchronous.Succession",
    "[e1] [occur] since [e2] [occur].": "Temporal.Asynchronous.Succession",
    "[e1] [occur]. So, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur]. Subsequently, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur]. Then, [e2] [occur].": "Temporal.Asynchronous.Precedence",
    "[e2] [occur]. Thereafter, [e1] [occur].": "Temporal.Asynchronous.Succession",
    "[e1] [occur]. Therefore, [e2] [occur].": "Temporal.Asynchronous.Precedence",
}


prompt_path = "data/stimuli-nonce/all_prompts.csv"
with open(prompt_path, newline='') as prompts:
    prompts = list(csv.DictReader(prompts))


_pref_templates = [t for conn, ll in connectives.PREFERENCE_TEMPLATES.items() for t in ll]
temp_templates = [t for conn, ll in connectives.TEMPORAL_TEMPLATES.items() for t in ll]
inst_templates = [t for conn, ll in connectives.INSTANTIATION_TEMPLATES.items() for t in ll]

#normalize occur verbs
occur = "[occur]"
temp_templates = [l.replace("[occur_1]", occur).replace("[occur_2]", occur) for l in temp_templates]

with open("data/properties.csv", "r") as f:
    reader = csv.DictReader(f)
    properties = list(reader)
    properties = [p["property"] for p in properties]

#normalize properties
pref_templates = []
for pref in _pref_templates:
    pref = pref.replace("love", "[pref-verb]")
    pref = pref.replace("hate", "[pref-verb]")
    for p in properties:
        pref = pref.replace(p, "[property]")
    pref_templates.append(pref)


results = []
for row in prompts:
    idx = row["idx"]
    category = row["stimuli_type"]
    e1 = row["entity1"]
    e2 = row["entity2"]
    stimuli = row["prompt"]

    stimuli = stimuli.replace(e1, "[e1]")
    stimuli = stimuli.replace(e2, "[e2]")
    
    for ov in connectives.OCCUR_VERBS:
        stimuli = stimuli.replace(ov, occur)

    for p in properties:
        stimuli = stimuli.replace(p, "[property]")
    


    if category == "preference":
        stimuli = stimuli.replace("love", "[pref-verb]")
        stimuli = stimuli.replace("hate", "[pref-verb]")

        template = pref_templates
    elif category == "temporal":
        template = temp_templates
    elif category == "instantiation":
        template = inst_templates

    sense = None
    for t in template:
        if t in stimuli:
            sense = senses[t]
        
    if sense is None:
        raise ValueError(stimuli)

    results.append([idx, sense])
    # print(sense)

outpath = "data/stimuli-nonce/senses.csv"
utils.write_csv(results, outpath, ("idx", "sense"))
