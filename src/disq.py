from connectives import *
import numpy as np
import re
from connectives import OCCUR_VERBS


# Building off of 
# [Discursive Socratic Questioning: Evaluating the Faithfulness of Language Models’ Understanding of Discourse Relations]
# (https://aclanthology.org/2024.acl-long.341/) (Miao et al., ACL 2024)
#
# Code from:
# https://github.com/YisongMiao/DiSQ-Score/blob/9d1b9119fd286d8138ca3a84be962b22e1a827f3/scripts/qa_utils.py



senses = {
    "Although I prefer [e1] to [e2], I [pref-verb] [property].": "Comparison.Concession.Arg1-as-denier",
    "I prefer [e1] to [e2], although I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "Although I [pref-verb] [property], I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "I prefer [e1] to [e2], as I [pref-verb] [property].": "Contingency.Cause.Reason",
    "I prefer [e1] to [e2], as I [pref-verb] [property].": "Contingency.Cause.Reason",
    "After [e2] [occur_2], [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "[e1] [occur_1] after [e2] [occur_2].": "Temporal.Asynchronous.Succession",
    "I [pref-verb] [property]. As a result, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. As a result, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "As much as I [pref-verb] [property], I prefer [e1] to [e2].": "Comparison.Concession.Arg1-as-denier",
    "I prefer [e1] to [e2] because I [pref-verb] [property].": "Contingency.Cause.Reason",
    "[e1] [occur_1]. Afterwards, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "Because I [pref-verb] [property], I prefer [e1] to [e2].": "Contingency.Cause.Reason",
    "[e2] [occur_2] as a result of [e1].": "Temporal.Asynchronous.Precedence",
    "I prefer [e1] to [e2] because I [pref-verb] [property].": "Contingency.Cause.Reason",
    "Because I [pref-verb] [property], I prefer [e1] to [e2].": "Contingency.Cause.Reason",
    "I [pref-verb] [property]. But, I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "I prefer [e1] to [e2]. But, I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "I [pref-verb] [property], even though I prefer [e1] to [e2].": "Comparison.Concession.Arg2-as-denier",
    "[e1] [occur_1]. As a result, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "Even though I prefer [e1] to [e2], I [pref-verb] [property].": "Comparison.Concession.Arg1-as-denier",
    "I prefer [e1] to [e2], even though I [pref-verb] [property].": "Comparison.Concession.Arg2-as-denier",
    "Even though I [pref-verb] [property], I prefer [e1] to [e2].": "Comparison.Concession.Arg1-as-denier",
    "[e1] [occur_1] as soon as [e2] [occur_2].": "Temporal.Asynchronous.Succession",
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
    "As soon as [e2] [occur_2], [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "Since I [pref-verb] [property], I prefer [e1] to [e2].": "Contingency.Cause.Reason",
    "Since I [pref-verb] [property], I prefer [e1] to [e2].": "Contingency.Cause.Reason",
    "I prefer [e1] to [e2], since I [pref-verb] [property].": "Contingency.Cause.Reason",
    "[e1] [occur_1] because [e2] [occur_2].": "Temporal.Asynchronous.Succession",
    "Because [e2] [occur_2], [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "I [pref-verb] [property]. So, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. So, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. Therefore, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "I [pref-verb] [property]. Therefore, I prefer [e1] to [e2].": "Contingency.Cause.Result",
    "Before [e2] [occur_2], [e1] [occur_1].": "Temporal.Asynchronous.Precedence",
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
    "[e1] [occur_1] before [e2].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur_1]. Consequently, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur_1]. Earlier, [e2] [occur_2].": "Temporal.Asynchronous.Succession",
    "[e1] [occur_1] even after [e2] [occur_2].": "Temporal.Asynchronous.Succession",
    "Even after [e2] [occur_2], [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "Even before [e1] [occur_1], [e2] [occur_2].": "Temporal.Asynchronous.Succession",
    "[e2] [occur_2] even before [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "[e1] [occur_1] even though [e2] [occur_2].": "Temporal.Asynchronous.Succession",
    "Even though [e2] [occur_2], [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "[e2] [occur_2]. Eventually, [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "[e1] [occur_1]. Finally, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur_1]. Hence, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur_1]. Later, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur_1]. Next, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "Once [e2] [occur_2], [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "[e1] [occur_1] once [e2] [occur_2].": "Temporal.Asynchronous.Succession",
    "[e1] [occur_1]. Previously, [e2] [occur_2].": "Temporal.Asynchronous.Succession",
    "Since [e2] [occur_2], [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "[e1] [occur_1] since [e2] [occur_2].": "Temporal.Asynchronous.Succession",
    "[e1] [occur_1]. So, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur_1]. Subsequently, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "[e1] [occur_1]. Then, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
    "[e2] [occur_2]. Thereafter, [e1] [occur_1].": "Temporal.Asynchronous.Succession",
    "[e1] [occur_1]. Therefore, [e2] [occur_2].": "Temporal.Asynchronous.Precedence",
}

families = {
    "Although I prefer [e1] to [e2], I [pref-verb] [property].": "preference",
    "I prefer [e1] to [e2], although I [pref-verb] [property].": "preference",
    "Although I [pref-verb] [property], I prefer [e1] to [e2].": "preference",
    "I prefer [e1] to [e2], as I [pref-verb] [property].": "preference",
    "I prefer [e1] to [e2], as I [pref-verb] [property].": "preference",
    "After [e2] [occur_2], [e1] [occur_1].": "temporal",
    "[e1] [occur_1] after [e2] [occur_2].": "temporal",
    "I [pref-verb] [property]. As a result, I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property]. As a result, I prefer [e1] to [e2].": "preference",
    "As much as I [pref-verb] [property], I prefer [e1] to [e2].": "preference",
    "I prefer [e1] to [e2] because I [pref-verb] [property].": "preference",
    "[e1] [occur_1]. Afterwards, [e2] [occur_2].": "temporal",
    "Because I [pref-verb] [property], I prefer [e1] to [e2].": "preference",
    "[e2] [occur_2] as a result of [e1].": "temporal",
    "I prefer [e1] to [e2] because I [pref-verb] [property].": "preference",
    "Because I [pref-verb] [property], I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property]. But, I prefer [e1] to [e2].": "preference",
    "I prefer [e1] to [e2]. But, I [pref-verb] [property].": "preference",
    "I [pref-verb] [property], even though I prefer [e1] to [e2].": "preference",
    "[e1] [occur_1]. As a result, [e2] [occur_2].": "temporal",
    "Even though I prefer [e1] to [e2], I [pref-verb] [property].": "preference",
    "I prefer [e1] to [e2], even though I [pref-verb] [property].": "preference",
    "Even though I [pref-verb] [property], I prefer [e1] to [e2].": "preference",
    "[e1] [occur_1] as soon as [e2] [occur_2].": "temporal",
    "I prefer [e1] to [e2], for I [pref-verb] [property].": "preference",
    "I prefer [e1] to [e2], for I [pref-verb] [property].": "preference",
    "I hate [e1]. For example, [e2] are awful.": "instantiation",
    "I [pref-verb] [property]. For example, I prefer [e1] to [e2].": "preference",
    "I like [e1]. For example, [e2] are nice.": "instantiation",
    "I [pref-verb] [property]. For example, I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property]. For instance, I prefer [e1] to [e2].": "preference",
    "I hate [e1]. For instance, [e2] are awful.": "instantiation",
    "I like [e1]. For instance, [e2] are nice.": "instantiation",
    "I [pref-verb] [property]. For instance, I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property]. However, I prefer [e1] to [e2].": "preference",
    "I prefer [e1] to [e2]. However, I [pref-verb] [property].": "preference",
    "I prefer [e1] to [e2], nevertheless, I [pref-verb] [property].": "preference",
    "I [pref-verb] [property], nevertheless, I prefer [e1] to [e2].": "preference",
    "I prefer [e1] to [e2], since I [pref-verb] [property].": "preference",
    "As soon as [e2] [occur_2], [e1] [occur_1].": "temporal",
    "Since I [pref-verb] [property], I prefer [e1] to [e2].": "preference",
    "Since I [pref-verb] [property], I prefer [e1] to [e2].": "preference",
    "I prefer [e1] to [e2], since I [pref-verb] [property].": "preference",
    "[e1] [occur_1] because [e2] [occur_2].": "temporal",
    "Because [e2] [occur_2], [e1] [occur_1].": "temporal",
    "I [pref-verb] [property]. So, I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property]. So, I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property]. Therefore, I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property]. Therefore, I prefer [e1] to [e2].": "preference",
    "Before [e2] [occur_2], [e1] [occur_1].": "temporal",
    "I [pref-verb] [property], though I prefer [e1] to [e2].": "preference",
    "Though I [pref-verb] [property], I prefer [e1] to [e2].": "preference",
    "I prefer [e1] to [e2], though I [pref-verb] [property].": "preference",
    "Though I prefer [e1] to [e2], I [pref-verb] [property].": "preference",
    "I [pref-verb] [property]. Thus, I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property]. Thus, I prefer [e1] to [e2].": "preference",
    "While I prefer [e1] to [e2], I [pref-verb] [property].": "preference",
    "While I [pref-verb] [property], I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property], yet I prefer [e1] to [e2].": "preference",
    "I [pref-verb] [property]. Despite that, I prefer [e1] to [e2].": "preference",
    "I find [e1], in particular, [e2] to be cute.": "instantiation",
    "I find [e1], in particular, [e2] to be awful.": "instantiation",
    "I find [e1], specifically, [e2] to be awful.": "instantiation",
    "I find [e1], specifically, [e2] to be cute.": "instantiation",
    "I find [e1] such as [e2], to be cute.": "instantiation",
    "I find [e1] such as [e2], to be awful.": "instantiation",
    "[e1] [occur_1] before [e2].": "temporal",
    "[e1] [occur_1]. Consequently, [e2] [occur_2].": "temporal",
    "[e1] [occur_1]. Earlier, [e2] [occur_2].": "temporal",
    "[e1] [occur_1] even after [e2] [occur_2].": "temporal",
    "Even after [e2] [occur_2], [e1] [occur_1].": "temporal",
    "Even before [e1] [occur_1], [e2] [occur_2].": "temporal",
    "[e2] [occur_2] even before [e1] [occur_1].": "temporal",
    "[e1] [occur_1] even though [e2] [occur_2].": "temporal",
    "Even though [e2] [occur_2], [e1] [occur_1].": "temporal",
    "[e2] [occur_2]. Eventually, [e1] [occur_1].": "temporal",
    "[e1] [occur_1]. Finally, [e2] [occur_2].": "temporal",
    "[e1] [occur_1]. Hence, [e2] [occur_2].": "temporal",
    "[e1] [occur_1]. Later, [e2] [occur_2].": "temporal",
    "[e1] [occur_1]. Next, [e2] [occur_2].": "temporal",
    "Once [e2] [occur_2], [e1] [occur_1].": "temporal",
    "[e1] [occur_1] once [e2] [occur_2].": "temporal",
    "[e1] [occur_1]. Previously, [e2] [occur_2].": "temporal",
    "Since [e2] [occur_2], [e1] [occur_1].": "temporal",
    "[e1] [occur_1] since [e2] [occur_2].": "temporal",
    "[e1] [occur_1]. So, [e2] [occur_2].": "temporal",
    "[e1] [occur_1]. Subsequently, [e2] [occur_2].": "temporal",
    "[e1] [occur_1]. Then, [e2] [occur_2].": "temporal",
    "[e2] [occur_2]. Thereafter, [e1] [occur_1].": "temporal",
    "[e1] [occur_1]. Therefore, [e2] [occur_2].": "temporal",
}


# From https://github.com/YisongMiao/DiSQ-Score/blob/9d1b9119fd286d8138ca3a84be962b22e1a827f3/scripts/qa_utils.py
DR_Q_mapping = {
            "Expansion.Conjunction":
            {
                'targeted': ['are contributed to the same situation'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with' , 'is reason for', 'is result of', 'is an example of'],
            },
            "Contingency.Cause.Reason":
            {
                'targeted': ['is reason for'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of', 'is equivalent to'],
            },
            "Expansion.Instantiation.Arg2-as-instance":
            {
                'targeted': ['is an example of'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Comparison.Concession.Arg2-as-denier":
            {
                'targeted': ['is denied or contradicted with'],
                'counterfactual': ['is reason for', 'is result of', 'is an example of', 'is equivalent to', 'does provide more detail about'],
            },
            "Expansion.Level-of-detail.Arg2-as-detail":
            {
                'targeted': ['does provide more detail about'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Temporal.Asynchronous.Precedence":
            {
                'targeted': ['does happens before'],
                'counterfactual': ['does happens after', 'is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of'],
            },
            "Expansion.Level-of-detail.Arg1-as-detail":
            {
                'targeted': ['does provide more detail about'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Expansion.Equivalence":
            {
                'targeted': ['is equivalent to'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is an example of'],
            },
            "Contingency.Cause.Result":
            {
                'targeted': ['is result of'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is an example of', 'is equivalent to'],
            },
            "Contingency.Cause+Belief.Reason+Belief":
            {
                'targeted': ['is reason for'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of', 'is equivalent to'],
            },
            "Temporal.Synchronous":
            {
                'targeted': ['does happens at the same time as'],
                'counterfactual': ['does happens before', 'is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of'],
            },
            "Expansion.Substitution.Arg2-as-subst":
            {
                'targeted': ['is an alternative to'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Expansion.Substitution.Arg1-as-subst":
            {
                'targeted': ['is an alternative to'],
                'counterfactual': ['is contrasted with', 'is denied or contradicted with', 'is reason for', 'is result of', 'is equivalent to'],
            },
            "Temporal.Asynchronous.Succession":
            {
                'targeted': ['does happens after'],
                'counterfactual': ['does happens before', 'is contrasted with', 'is denied or contradicted with', 'is result of', 'is an example of'],
            },
            "Comparison.Concession.Arg1-as-denier":
            {
                'targeted': ['is denied or contradicted with'],
                'counterfactual': ['is reason for', 'is result of', 'is an example of', 'is equivalent to', 'does provide more detail about'],
            },
            "Comparison.Contrast":
            {
                'targeted': ['is contrasted with'],
                'counterfactual': ['is denied or contradicted with', 'is reason for', 'is result of', 'is an example of', 'is equivalent to'],
            },
        }


converse_question_mapping = {
            # contingency
            'is result of': 'is reason for',
            'is reason for': 'is result of',
            # temporal
            'does happens at the same time as': 'does happens at the same time as',
            'does happens before': 'does happens after',
            'does happens after': 'does happens before',
            # comparison
            'is contrasted with': 'is contrasted with',
            'is denied or contradicted with': 'denies or contradicts with',
            # expansion
            'is an alternative to': 'is being provided an alternative by',
            'does provide more detail about': 'is being provided more detail by',
            'is equivalent to': 'is equivalent to',
            'are contributed to the same situation': 'are contributed to the same situation',
            'is an example of': 'is being exemplified by',
        }


def glue(event1, event2, prompt):
        # event1 = event1.lower() + ' (event 1)'
        # event2 = event2.lower() + ' (event 2)'
        
        # Given all prompt in self.DR_Q_mapping, glue them into a grammarly correct question
        # all possible question is ['is result of', 'does happens at the same time as', 'is contrasted with', 'is an alternative to', 'is reason for', 'does provide more detail about', 'does happens before', 'is an example of', 'does happens after', 'is equivalent to', 'are contributed to the same situation', 'is denied or contradicted with']
        if prompt == 'is result of':
            return 'Is "{}" the result of "{}"?'.format(event1, event2)
        elif prompt == 'does happens at the same time as':
            return 'Does "{}" happen at the same time as "{}"?'.format(event1, event2)
        elif prompt == 'is contrasted with':
            return 'Is "{}" contrasted with "{}"?'.format(event1, event2)
        elif prompt == 'is an alternative to':
            return 'Is "{}" an alternative to "{}"?'.format(event1, event2)
        elif prompt == 'is reason for':
            return 'Is "{}" the reason for "{}"?'.format(event1, event2)
        elif prompt == 'does provide more detail about':
            return 'Does "{}" provide more detail about "{}"?'.format(event1, event2)
        elif prompt == 'does happens before':
            return 'Does "{}" happen before "{}"?'.format(event1, event2)
        elif prompt == 'is an example of':
            return 'Is "{}" an example of "{}"?'.format(event1, event2)
        elif prompt == 'does happens after':
            return 'Does "{}" happen after "{}"?'.format(event1, event2)
        elif prompt == 'is equivalent to':
            return 'Is "{}" equivalent to "{}"?'.format(event1, event2)
        elif prompt == 'are contributed to the same situation':
            return 'Is "{}" contributed to the same situation as "{}"?'.format(event1, event2)
        elif prompt == 'is denied or contradicted with':
            return 'Is "{}" denied or contradicted with "{}"?'.format(event1, event2)
        elif prompt == 'denies or contradicts with':
            return 'Does "{}" deny or contradict with "{}"?'.format(event1, event2)
        elif prompt == 'is being provided an alternative by':
            return 'Is "{}" being provided an alternative by "{}"?'.format(event1, event2)
        elif prompt == 'is being provided more detail by':
            return 'Is "{}" being provided more detail by "{}"?'.format(event1, event2)
        elif prompt == 'is being exemplified by':
            return 'Is "{}" being exemplified by "{}"?'.format(event1, event2)
        # put all question part into a list, e.g. "the result of", "happen at the same time as", "is contrasted with", "an alternative to", "the reason for", "provide more detail about", "happen before", "an example of", "happen after", "equivalent to", "contributed to the same situation", "denied or contradicted with"
        # question_prompt_list = ['the result of', 'happen at the same time as', 'contrasted with', 'an alternative to', 'the reason for', 'provide more detail about', 'happen before', 'an example of', 'happen after', 'equivalent to', 'contributed to the same situation', 'denied or contradicted with', 'deny or contradict with', 'being  an alternative by', 'being provided more detail by', 'being exemplified by']
        else:
            return 'Error: prompt not found'
        

def generate_questions(event1, event2, sense):
        # Get both targeted and counterfactual questions for a given DR
        # return a list of questions
        targeted_question_prompts = DR_Q_mapping[sense]['targeted']
        counterfactual_questions = DR_Q_mapping[sense]['counterfactual']
        # The order of event1 and event2 is important. 
        # In forward_relations, it is event1 is X to event2
        
        forward_relations = ["Temporal.Asynchronous.Precedence", "Expansion.Level-of-detail.Arg1-as-detail", "Comparison.Concession.Arg1-as-denier"]

        if sense in forward_relations:
            targeted_question = glue(event1, event2, targeted_question_prompts[0])
            counterfactual_question = [glue(event1, event2, item) for item in counterfactual_questions]
            converse_targeted_question = glue(event2, event1, converse_question_mapping[targeted_question_prompts[0]])
            converse_counterfactual_question = [glue(event2, event1, converse_question_mapping[item]) for item in counterfactual_questions]
        else:
            # 
            targeted_question = glue(event2, event1, targeted_question_prompts[0])
            counterfactual_question = [glue(event2, event1, item) for item in counterfactual_questions]
            # then we need to generate the converse question for both targeted and counterfactual questions, which means we alter the order of event1 and event2 but use a converse prompt
            converse_targeted_question = glue(event1, event2, converse_question_mapping[targeted_question_prompts[0]])
            converse_counterfactual_question = [glue(event1, event2, converse_question_mapping[item]) for item in counterfactual_questions]
        
        return targeted_question, counterfactual_question, converse_targeted_question, converse_counterfactual_question

def multi_replace(text, mapping:dict):
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text

def detect_occurs(stimuli):
    for occur1 in OCCUR_VERBS:
        for occur2 in OCCUR_VERBS:
            if (not occur1 == occur2) and occur1 in stimuli and occur2 in stimuli:
                idx1 = stimuli.find(occur1)
                idx2 = stimuli.find(occur2)
                if idx1 < idx2:
                    return (occur1, occur2)
                else:
                    return (occur2, occur1)
    #possibly only one occur verb
    for occur1 in OCCUR_VERBS:
        if occur1 in stimuli:
            return (occur1, "")
    raise ValueError("Bad temporal stimuli", stimuli)

class DisqPref:
    def __init__(self, stimuli, sense):
        self.s1 = "I prefer [e1] to [e2]"
        self.s2 = "I {} [property]"
        pref_verb = ""
        if "I hate P" in stimuli: 
            pref_verb = "hate"
        elif "I love P" in stimuli:
            pref_verb = "love"
        else:
            pref_verb = "[pref-verb]"
            # raise ValueError("No pref Verb:", stimuli)
        self.s2 = self.s2.format(pref_verb)

        if sense == "Contingency.Cause.Result":
            self.s1, self.s2 = (self.s2, self.s1)
        
        (
            self.targeted_question,
            self.counterfactual_question,
            self.converse_targeted_question,
            self.converse_counterfactual_question,
        ) = generate_questions(self.s1, self.s2, sense)


class DisqTemp:
    def __init__(self, stimuli, sense):
        self.s1 = "[e1] [occur_1]"
        self.s2 = "[e2] [occur_2]"

        (
            self.targeted_question,
            self.counterfactual_question,
            self.converse_targeted_question,
            self.converse_counterfactual_question,
        ) = generate_questions(self.s1, self.s2, sense)

class DisqInst:
    def __init__(self, stimuli, sense):
        self.s1 = "[e1]"
        self.s2 = "[e2]"

        (
            self.targeted_question,
            self.counterfactual_question,
            self.converse_targeted_question,
            self.converse_counterfactual_question,
        ) = generate_questions(self.s1, self.s2, sense)

class Disq: 
    def __init__(self, stimuli, sense, family):
        disq = None
        if family == "instantiation":
            disq = DisqInst(stimuli, sense)
        elif family == "preference":
            disq = DisqPref(stimuli, sense)
        elif family == "temporal":
            disq = DisqTemp(stimuli, sense)
        else:
            raise ValueError("Family must be one of 'instantiation', 'preference', or 'temporal'")
        
        self.targeted_question = disq.targeted_question
        self.counterfactual_question = disq.counterfactual_question
        self.converse_targeted_question = disq.converse_targeted_question
        self.converse_counterfactual_question = disq.converse_counterfactual_question

    def format(self, mapping:dict):
        self.targeted_question = multi_replace(self.targeted_question, mapping)
        self.converse_targeted_question = multi_replace(self.converse_targeted_question, mapping)
        self.counterfactual_question = [multi_replace(q, mapping) for q in self.counterfactual_question]
        self.converse_counterfactual_question = [multi_replace(q, mapping) for q in self.converse_counterfactual_question]
    
        
    def items(self):
        all = [self.targeted_question, self.converse_targeted_question, *self.counterfactual_question, *self.converse_counterfactual_question]
        style = ["targeted", "converse"]
        style.extend(["counterfactual"] * len(self.counterfactual_question))
        style.extend(["converse_counterfactual"] * len(self.converse_counterfactual_question))
        return zip(all, style)
    

def detect_sense(stimuli):
    for template, sense in senses.items():
        template = template.replace(".", "\\.")
        template = template.replace("[e1]", ".*")
        template = template.replace("[e2]", ".*")
        template = template.replace("[pref-verb]", "(love|hate)")
        template = template.replace("[property]", ".*")
        template = template.replace("[occur_1]", ".*")
        template = template.replace("[occur_2]", ".*")

        if re.match(template,stimuli):
            return sense
    raise ValueError("No Sense Found for: ", stimuli)
