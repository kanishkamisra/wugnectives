import csv
import json
import re
import unicodedata


def read_jsonl(path):
    with open(path) as f:
        data = f.readlines()
    data = [json.loads(line) for line in data]
    return data


def read_csv_dict(path):
    data = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for line in reader:
            data.append(line)
    return data


def roundup(x):
    return x if x % 1000 == 0 else x + 1000 - x % 1000


def read_file(path):
    """TODO: make read all"""
    return [
        unicodedata.normalize("NFKD", i.strip())
        for i in open(path, encoding="utf-8").readlines()
        if i.strip() != ""
    ]

def write_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for line in data:
            f.write(line + "\n")

def belongingness(tup1, tup2):
    """is tup1 contained in tup2?"""
    assert tup1[0] <= tup1[1] and tup2[0] <= tup2[1]

    if tup2[0] <= tup1[0] and tup2[1] >= tup1[1]:
        return True
    else:
        return False


def write_dict_list_to_csv(dict_list, csv_file):
    fieldnames = dict_list[0].keys()  # Assuming all dictionaries have the same keys

    with open(csv_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the data
        writer.writerows(dict_list)


def write_jsonl(data, path):
    with open(path, "w") as f:
        for line in data:
            f.write(json.dumps(line) + "\n")


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]

def write_csv(data, path, header=None):
    with open(path, "w") as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(data)

def get_sense(template):
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
        "Even before [e1] [occur], [e2] [occur].": "Temporal.Asynchronous.Precedence",
        "[e2] [occur] even before [e1] [occur].": "Temporal.Asynchronous.Precedence",
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
    return senses[template]