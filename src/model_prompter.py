import random
from minicons import scorer
import numpy as np
import json
from input_generator import make_stimuli


model = scorer.IncrementalLMScorer('gpt2', 'cpu')


def evaluate_stimuli(model, stimuli: dict[str:list[str]], responses: tuple):
    
    # Dictionary of connective mapped to a dictionary of (prompt, question) 
    # mapped to a dictionary of repsonses mapped to their log-probs
    # so output_logprobs[connective][(prompt,question)][desired_response] gives the logprob of desired_response
    output_logprobs = {conn:{(p,q):{r:[] for r in responses} for p, q, r in stimuli[conn]} for conn in stimuli.keys()}

    for conn in stimuli.keys():
        for prompt, question, correct_response in stimuli[conn]:
            for response in responses:
                score = model.partial_score(prompt + question, response)
                output_logprobs[conn][(prompt, question)][response] = (score)
    
    return output_logprobs



# Examples:

# stimulus = make_stimuli(args=["I [wug]ed","I was [dax]."], 
#                         question="Was I [dax] before [wug]ing, after [wug]ing, or during [wug]ing?", 
#                         connectives=["as","then","previously"],
#                         nonces=["X","Y","Z"],
#                         template_nonces=["[wug]","[dax]"])

# scores = evaluate_stimuli(model,stimulus, ("before", "during", "after"))
# # print(scores)
# for conn in scores.keys():
#     for p, q in scores[conn].keys():
#         print(p, "\tQ:", q,"\t",scores[conn][(p,q)])

# print("#--------------------------------------------------------------------------#")

# stimulus = make_stimuli(args=["I prefer [wug] to [dax]","I hate the snowy winters."], 
#                         question="Which has the snowy winters?", 
#                         connectives=["because", "however"],
#                         nonces=["X","Y","Z","A","B","C"],
#                         template_nonces=["[wug]","[dax]"])

# scores = evaluate_stimuli(model,stimulus, ("before", "during", "after"))
# # print(scores)
# for conn in scores.keys():
#     for p, q in scores[conn].keys():
#         print(p, "\tQ:", q,"\t",scores[conn][(p,q)])

