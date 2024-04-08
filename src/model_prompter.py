import random
from minicons import scorer
import numpy as np
import json
from input_generator import make_stimuli

model = scorer.IncrementalLMScorer('gpt2', 'cpu')


def evaluate_dataset(model: scorer, dataset: list[tuple]):
    results = []
    for entry in dataset:
        e1 = entry[6]
        e2 = entry[7]
        statement = entry[8]

        given_str = "Given the following statement:\n" + statement
        produce_str_1 = "\n\nproduce a valid conclusion about " + e1+ ":"
        produce_str_2 = "\n\nproduce a valid conclusion about " + e2 + ":"
        
        conclusion_1 = entry[9]
        conclusion_2 = entry[10]

        score_1 = model.partial_score(given_str + produce_str_1, conclusion_1)[0]
        score_2 = model.partial_score(given_str + produce_str_2, conclusion_2)[0]

        results.append((entry[1], score_1, e1, entry[2], entry[3], statement, conclusion_1))
        results.append((entry[1], score_2, e2, entry[2], entry[3], statement, conclusion_2))
    
    return results


# print(evaluate_dataset(model, pref_dataset))




def evaluate_stimuli(model, stimuli: dict[str:list[str]]):
    
    # Dictionary of connective mapped to a dictionary of (prompt, question) 
    # mapped to a dictionary of repsonses mapped to their log-probs
    # so output_logprobs[connective][(prompt,question)][desired_response] gives the logprob of desired_response
    # output_logprobs = {conn:{(p,q):{r:[] for r in responses} for p, q, r in stimuli[conn]} for conn in stimuli.keys()}
    
    
    
    output_logprobs = {conn:{(p,q):{n1:0, n2:0} for p, q, d, n1, n2 in stimuli[conn]} for conn in stimuli.keys()}

    for conn in stimuli.keys():
        for prompt, question, direction, nonce_1, nonce_2 in stimuli[conn]:
                # score_1 = random.random()
                # score_2 = random.random()
                score_1 = model.partial_score(prompt + " " + question, nonce_1)
                score_2 = model.partial_score(prompt + " " + question, nonce_2)


                output_logprobs[conn][(prompt, question)][nonce_1] = score_1
                output_logprobs[conn][(prompt, question)][nonce_2] = score_2
                
    
    return output_logprobs



# Examples:


# question = "Which city is the state capital?"
# argset_1 = ["I prefer [X] to [Y]", "I like state capitals."]
# conn_1 = ["because", "however"]
# directions_1 = ["left", "right"]
# nonces = ("wugsland", "daxville", "wugsburg", "daxtown", "wug","dax","xyz","abc","X","Y")

# stimulus = make_stimuli(args=argset_1,
#                           question=question,
#                           connectives=conn_1,
#                           directions=directions_1,
#                           nonces=nonces,
#                           template_nonces=["[X]", "[Y]"],)

# scores = evaluate_stimuli(model,stimulus)
# for conn in scores.keys():
#     for p, q in scores[conn]:
#         print(p, "\t", q, "\t", scores[conn][(p,q)])

# print(scores)

