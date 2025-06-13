PREFERENCE_TEMPLATES = {
    "although": [
        "I prefer [e1] to [e2], although I [pref-verb] [property].",
        "Although I [pref-verb] [property], I prefer [e1] to [e2].",
        "Although I prefer [e1] to [e2], I [pref-verb] [property].",
    ],
    "as": [
        "I prefer [e1] to [e2], as I [pref-verb] [property].",
    ],
    "as a result": [
        "I [pref-verb] [property]. As a result, I prefer [e1] to [e2].",
    ],
    "as much as": [
        "As much as I [pref-verb] [property], I prefer [e1] to [e2].",
    ],
    "because": [
        "I prefer [e1] to [e2] because I [pref-verb] [property].",
        "Because I [pref-verb] [property], I prefer [e1] to [e2].",
    ],
    "but": [
        "I prefer [e1] to [e2], but I [pref-verb] [property].",
        "I [pref-verb] [property], but I prefer [e1] to [e2].",
    ],
    "even though": [
        "I prefer [e1] to [e2], even though I [pref-verb] [property].",
        "Even though I prefer [e1] to [e2], I [pref-verb] [property].",
        "I [pref-verb] [property], even though I prefer [e1] to [e2].",
        "Even though I [pref-verb] [property], I prefer [e1] to [e2].",
    ],
    "for": [
        "I prefer [e1] to [e2], for I [pref-verb] [property].",
    ],
    "for example": [
        "I [pref-verb] [property]. For example, I prefer [e1] to [e2].",
    ],
    "for instance": [
        "I [pref-verb] [property]. For instance, I prefer [e1] to [e2].",
    ],
    "however": [
        "I prefer [e1] to [e2], however, I [pref-verb] [property].",
    ],
    "nevertheless": [
        "I prefer [e1] to [e2], nevertheless, I [pref-verb] [property].",
        "I [pref-verb] [property], nevertheless, I prefer [e1] to [e2].",
    ],
    "since": [
        "I prefer [e1] to [e2], since I [pref-verb] [property].",
        "Since I [pref-verb] [property], I prefer [e1] to [e2].",
    ],
    "so": [
        "I [pref-verb] [property]. So, I prefer [e1] to [e2].",
    ],
    "therefore": [
        "I [pref-verb] [property]. Therefore, I prefer [e1] to [e2].",
    ],
    "though": [
        "I prefer [e1] to [e2], though I [pref-verb] [property].",
        "Though I [pref-verb] [property], I prefer [e1] to [e2].",
        "Though I prefer [e1] to [e2], I [pref-verb] [property].",
        "I [pref-verb] [property], though I prefer [e1] to [e2].",
    ],
    "thus": [
        "I [pref-verb] [property]. Thus, I prefer [e1] to [e2].",
    ],
    "while": [
        "While I [pref-verb] [property], I prefer [e1] to [e2].",
        "While I prefer [e1] to [e2], I [pref-verb] [property].",
    ],
    "yet": [
        "I [pref-verb] [property], yet I prefer [e1] to [e2].",
    ],
}

TEMPORAL_TEMPLATES = {
    "after": [
        "[e1] happened after [e2].",
        "After [e2], [e1] happened.",
    ],
    "afterwards": [
        "[e1] happened. Afterwards, [e2] happened.",
    ],
    "as soon as": [
        "As soon as [e2] finished, [e1] happened.",
        "[e1] happened as soon as [e2] finished.",
    ],
    "as a result": [
        "[e1] happened. As a result, [e2] happened.",
        "[e2] happened as a result of [e1].",
    ],
    "because": [
        "[e1] happened because [e2] happened.",
        "because [e2] happened, [e1] happened.",
    ],
    "before": [
        "[e1] happened before [e2].",
        "Before [e2], [e1] happened.",
    ],
    "consequently": [
        "[e1] happened. Consequently, [e2] happened.",
    ],
    "earlier": [
        "[e1] happend. Earlier, [e2] had happened.",
    ],
    "even after": [
        "Even after [e2], [e1] happened.",
        "[e1] happened even after [e2].",
    ],
    "even before": [
        "Even before [e1], [e2] happened.",
        "[e2] happened even before [e1].",
    ],
    "even though": [
        "Even though [e2] had happened, [e1] happened.",
        "[e1] happened even though [e2] had happened.",
    ],
    "finally": [
        "[e1] happened. Finally, [e2] happened.",
    ],
    "hence": [
        "[e1] happened. Hence, [e2] happened.",
    ],
    "later": [
        "[e1] happened. Later, [e2] happened.",
    ],
    "next": [
        "[e1] happened. Next, [e2] happened.",
    ],
    "once": [
        "[e1] happened once [e2] happened.",
        "Once [e2] happened, [e1] happened.",
    ],
    "previously": [
        "[e1] happened. Previously, [e2] happened.",
    ],
    "since": [
        "[e1] happened since [e2] happened.",
        "Since [e2] happened, [e1] happened.",
    ],
    "so": [
        "[e1] happened. So, [e2] happened.",
    ],
    "subsequently": [
        "[e1] happened. Subsequently, [e2] happened.",
    ],
    "then": [
        "[e1] happened. Then, [e2] happened.",
    ],
    "thereafter": [
        "[e1] happened. Thereafter, [e2] happened.",
    ],
    "therefore": [
        "[e1] happened. Therefore, [e2] happened.",
    ],
}

CAUSAL_TEMPLATES = {
    "as long as": [
        "[e1] will happen as long as [e2] happens.",
    ],
    "as a result": [
        "[e1] happened. As a result, [e2] happened.",
    ],
    "because": [
        "[e1] happened because [e2] happened.",
    ],
    "because of": [
        "[e1] happened because of [e2].",
    ],
    "consequently": [
        "[e1] happened. Consequently, [e2] happened.",
    ],
    "hence": [
        "[e1] happened. Hence, [e2] happened.",
    ],
    "if": [
        "[e1] will happen if [e2] happens.",
    ],
    "only if": [
        "[e1] will happen only if [e2] happens.",
    ],
    "therefore": [
        "[e1] happened. Therefore, [e2] happened.",
    ],
}

ASGOAL_TEMPLATES = {
    "in order to": [
        "You need to [e1] in order to [e2].",
        "In order to [e2], you need to [e1]."
    ],
    "so that": [
        "You need to [e1] so that you can [e2].",
    ],
    "so as": [
        "You need to [e1] so as to be able to [e2].",
    ]
    # "without": [
    #     "I was [e1] without [e2].", 
    # ],
    # "thereby": [
    #     "I was [e1]. Thereby, I was [e2].",
    # ]
}

INSTANTIATION_TEMPLATES = {
    "for example": [
        "I like [e1], for example, [e2] are nice.",
        "I hate [e1], for example, [e2] are awful.",
    ],
    "for instance": [
        "I like [e1], for instance, [e2] are nice.",
        "I hate [e1], for instance, [e2] are awful.",
    ],
    "in particular": [
        "I find [e1], in particular, [e2] to be cute.",
        "I find [e1], in particular, [e2] to be awful.",
    ],
    "such as": [
        "I find [e1] such as [e2], to be cute.",
        "I find [e1] such as [e2], to be awful.",
    ]
}
