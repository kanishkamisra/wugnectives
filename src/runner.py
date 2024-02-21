import random
from minicons import scorer
import numpy as np
import json
from input_generator import make_stimuli
from model_prompter import evaluate_stimuli
import sys
import csv


model = scorer.IncrementalLMScorer('gpt2', 'cpu')


question = "Which city is the state capital?"
argset_1 = ["I prefer [X] to [Y]", "I like state capitals."]
conn_1 = ["because", "however", "although", "but", "as", "though"]
directions_1 = ["left", "right", "right", "right", "right", "right"]


argset_2 = ["I like state capitals", "I prefer [X] to [Y]."]
conn_2 = ["as a result", "yet", "even though", "though", "so", "thus",
          "therefore", "but", "for example", "for instance", "nevertheless"]


nonces = ("wugsland", "daxville", "wugsburg", "daxtown")

stimulus_1 = make_stimuli(args=argset_1,
                          question=question,
                          connectives=conn_1,
                          directions=directions_1,
                          nonces=nonces,
                          template_nonces=["[X]", "[Y]"],)

# print(stimulus_1)
# print("#-----------------------------------------------------------#")

scores = evaluate_stimuli(model,stimulus_1, nonces)


# print(scores)
with open("output.csv", 'w+', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    
    header = ["prompt", "question", "expected output", "generated output"]
    
    # Get 'dummy' connectives and nonces in the scores object to add all included nonces to the output csv header
    # so it doesn't depend on having nonces/prompts/questions in this file, which may change
    header.extend(scores[next(iter(scores.keys()))][next(iter(scores[next(iter(scores.keys()))].keys()))])
    
    writer.writerow(header)
    
    for conn in scores.keys():
        for p, q, r in stimulus_1[conn]:
            
            # find max score
            max = ["none", -sys.maxsize]
            for nonce, score in scores[conn][(p,q)].items():
                print(nonce + ":", score)

                if score[0] >= max[1]:
                    max[0] = nonce
                    max[1] = score[0]
            
            
            row = [p, q, r, max[0]]
            raw_scores = [ val[0] for val in scores[conn][(p,q)].values() ]
            row.extend(raw_scores)
            writer.writerow(row)
            
            print("expected response: \"" + r + "\"\tMax response:", max[0], "\tWas correct?", max[0] == r )
            print(p, "\tQ:", q,"\t",scores[conn][(p,q)], "\n")

print("#-----------------------------------------------------------#")
