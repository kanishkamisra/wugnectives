import json
from string import Template

PREF_VERBS = ["love", "hate"]


def write_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


PREFERENCE_RULES = {
    "although": {"hate": "Yes"},
    "as much as": {"hate": "Yes"},
    "but": {"hate": "Yes"},
    "even though": {"hate": "Yes"},
    "however": {"hate": "Yes"},
    "nevertheless": {"hate": "Yes"},
    "though": {"hate": "Yes"},
    "while": {"hate": "Yes"},
    "yet": {"hate": "Yes"},
    "despite that": {"hate": "Yes"},
    "as": {"love": "Yes", "hate": "No"},
    "as a result": {"love": "Yes", "hate": "No"},
    "because": {"love": "Yes", "hate": "No"},
    "for": {"love": "Yes", "hate": "No"},
    "for example": {"love": "Yes", "hate": "No"},
    "for instance": {"love": "Yes", "hate": "No"},
    "since": {"love": "Yes", "hate": "No"},
    "so": {"love": "Yes", "hate": "No"},
    "therefore": {"love": "Yes", "hate": "No"},
    "thus": {"love": "Yes", "hate": "No"},
}

EXTRA_PREFERENCE_RULES = {
    "although": {"love": "No"},
    "as much as": {"love": "No"},
    "but": {"love": "No"},
    "even though": {"love": "No"},
    "however": {"love": "No"},
    "nevertheless": {"love": "No"},
    "though": {"love": "No"},
    "while": {"love": "No"},
    "yet": {"love": "No"} 
}

TEMPORAL_RULES = {
    "e2": [
        "after",
        "as soon as",
        "because",
        "earlier",
        "even after",
        "even before",
        "even though",
        "once",
        "previously",
        "since",
        "thereafter",
        "eventually",
    ],
    "e1": [
        "afterwards",
        "as a result",
        "before",
        "consequently",
        "finally",
        "hence",
        "later",
        "next",
        "so",
        "subsequently",
        "then",
        "therefore",
    ],
}

TEMPORAL_RULES = {vv: k for k, v in TEMPORAL_RULES.items() for vv in v}

yn = "Answer either with Yes or No."

PREF_INSTANT_QUESTIONS = [
    Template(f'$name said, "$premise" From this, is it true that $inference? {yn}'),
    Template(f'$name said, "$premise" Does this mean that $inference? {yn}'),
    Template(
        f'$name said, "$premise" Can we conclude from this that $inference? {yn}'
    ),
    Template(f'$name said, "$premise" Does this suggest that $inference? {yn}'),
    Template(f'$name said, "$premise" Can we say from this that $inference? {yn}'),
    Template(
        f'$name said, "$premise" Can we conclude from what $name said that $inference? {yn}'
    ),
    Template(
        f'$name said, "$premise" Can we say from what $name said that $inference? {yn}'
    ),
    Template(f'$name said, "$premise" Does $name mean that $inference? {yn}'),
    Template(
        f'$name said, "$premise" Does what $name said suggest that $inference? {yn}'
    ),
    Template(
        f'$name said, "$premise" If you heard this, would you think that $inference? {yn}'
    ),
    Template(
        f'$name said, "$premise" If you heard $name, would you think that $inference? {yn}'
    ),
    Template(
        f'$name said, "$premise" From what $name said, do you think that $inference? {yn}'
    ),
]

TEMPORAL_QUESTIONS = [
    Template(
        f'$name said, "$premise" From this, which event started first? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From this, which event started earlier? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From this, which event began first? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From this, which event began earlier? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From this, which of the two events began first? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From this, which of the two events began earlier? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From what $name said, which event started first? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From what $name said, which event started earlier? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From what $name said, which event began first? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From what $name said, which event began earlier? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From what $name said, which of the two events began first? Answer either with $e1 or $e2 and nothing else.'
    ),
    Template(
        f'$name said, "$premise" From what $name said, which of the two events began earlier? Answer either with $e1 or $e2 and nothing else.'
    ),
]

prompt_templates = {
    "preference": PREF_INSTANT_QUESTIONS,
    "instantiation": PREF_INSTANT_QUESTIONS,
    "temporal": TEMPORAL_QUESTIONS,
}


DISQ_QUESTIONS = [
    Template(f'$name said, "$premise" $question {yn}'),
    Template(f'$name said, "$premise" From this, $question {yn}'),
    Template(
        f'$name said, "$premise" If you heard this, what would you think? $question {yn}'
    ),
    Template(
        f'$name said, "$premise" If you heard $name, what would you think? $question {yn}'
    ),
    
    Template(
        f'$name said, "$premise" If you heard $name, and were asked what they meant, what would you say? $question {yn}'
    ),

    Template(f'$name said, "$premise" Help me understand what $name meant. $question {yn}'),
    Template(f'$name said, "$premise" Clarify what $name meant. $question {yn}'),
    Template(f'$name said, "$premise" Analyze what was meant. $question {yn}'),
    Template(f'$name said, "$premise" I\'m confused by this. $question {yn}'),

]