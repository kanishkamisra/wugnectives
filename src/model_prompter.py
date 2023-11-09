import random
from minicons import scorer
import numpy as np
import json
from input_generator import Stimuli


model = scorer.IncrementalLMScorer('gpt2', 'cpu')


def evaluate_stimuli(model, stimuli: dict[str:list[str]], responses: tuple):
    
    # why is list/dict comprehension
    output_logprobs = {conn:{(p,q):{r:[] for r in responses} for p, q in stimuli[conn]} for conn in stimuli.keys()}

    for conn in stimuli.keys():
        for prompt, question in stimuli[conn]:
            for response in responses:
                # for quick testing
                score = random.randint(0,10) # score = model.partial_score(prompt + question, response)
                
                output_logprobs[conn][(prompt, question)][response] = (score)
    
    # scores = model.partial_score(prefixes, queries)
    # return zip(queries, scores)
    # print(output_logprobs)
    return output_logprobs


# logprobs = model.compute_stats(model.prepare_text("It was the best of times, it was the worst of times"))

# queries = ["before", "during", "after"]
# prefixes = ["I ran then I was happy. Was I happy before running, after running, or during running?"] * len(queries)

# stats = model.compute_stats(model.prepare_text(prefixes))
# scores = model.token_score(prefixes)
# print(stats)
# cond_stats = model.partial_score(prefixes, queries)

# print(cond_stats)

stimulus = Stimuli.make_stimuli(arg=["I [wug]ed","I was [dax]."], 
                        question="Was I [dax] before [wug]ing, after [wug]ing, or during [wug]ing?", 
                        connectives=["as","then","previously"],
                        nonces=["X","Y","Z"],
                        template_nonces=["[wug]","[dax]"])

scores = evaluate_stimuli(model,stimulus, ("before", "during", "after"))
# print(scores)
for conn in scores.keys():
    for p, q in scores[conn].keys():
        print(p, "\tQ:", q,"\t",scores[conn][(p,q)])

print("#--------------------------------------------------------------------------#")

stimulus = Stimuli.make_stimuli(arg=["I prefer [wug] to [dax]","I hate the snowy winters."], 
                        question="Which has the snowy winters?", 
                        connectives=["because", "however"],
                        nonces=["X","Y","Z","A","B","C"],
                        template_nonces=["[wug]","[dax]"])

scores = evaluate_stimuli(model,stimulus, ("before", "during", "after"))
# print(scores)
for conn in scores.keys():
    for p, q in scores[conn].keys():
        print(p, "\tQ:", q,"\t",scores[conn][(p,q)])



model = scorer.MaskedLMScorer('bert-base-uncased', 'cpu')
# mask = model.tokenizer.mask_token

prompt = "I prefer wug to dax, however I hate the snowy winters."
question = "Which has snowy winters?"

print(model.partial_score(prompt + question, "dax"))

# # queries = ["before", "during", "after"]
# prefixes = ["I ran then I was happy. Was I happy before running, after [MASK], or during running? after","I ran before I was happy. Was I happy before running, after running, or during running? [MASK]"] 
prefixes = ["I ran then I was happy. Was I happy before running, after running, or during running? [MASK]","I ran before I was happy. Was I happy before running, after running, or during running? [MASK]"] 

stimuli = [[p, "[MASK]"] for p in prefixes]
print(stimuli)
result = model.cloze(stimuli)
print(result)
result = model.cloze_distribution(stimuli)
print(result)
result = model.token_score(prefixes)
print(result)


# mask = model.mask([("prefixes [hi] a", "[hi]"), ("aprefixes [hi] b", "[hi]")])
# print(mask[:-1])
# probs = model.cloze(mask)

# print(probs)

