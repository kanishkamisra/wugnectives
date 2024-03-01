import random
from minicons import scorer
import numpy as np
import json
from input_generator import make_stimuli
from model_prompter import evaluate_stimuli
import sys
import csv

model_dir = "../../../shared/hf_cache/models--mistralai--Mistral-7B-v0.1/snapshots/26bca36bde8333b5d7f72e9ed20ccda6a618af24/"
# model = scorer.IncrementalLMScorer('gpt2', 'cpu')
model = scorer.IncrementalLMScorer(model_dir, 'cuda:0')


question = "Which city is the state capital?"
argset_1 = ["I prefer [X] to [Y]", "I like state capitals."]
conn_1 = ["because", "however", "although", "but", "as", "since", "for", "though", "nevertheless", "even though"]
directions_1 = ["left", "right", "right", "right", "left", "left", "left", "right", "right", "right"]

argset_2 = ["I like state capitals.", "I prefer [X] to [Y]."]
conn_2 = [ "As a result", "Yet", "Even though", "though", "So", "Thus", "therefore", "But", "for example", "for instance", "nevertheless"]
directions_2 = ["left", "right", "right", "right", "left", "right", "right", "right", "left", "left", "right"]



nonces = ("wugsland", "daxville", "wugsburg", "daxtown", "wug","dax","xyz","abc","X","Y")

stimulus_1 = make_stimuli(args=argset_1,
                          question=question,
                          connectives=conn_1,
                          directions=directions_1,
                          nonces=nonces,
                          template_nonces=["[X]", "[Y]"],)

stimulus_2 = make_stimuli(args=argset_2,
                          question=question,
                          connectives=conn_2,
                          directions=directions_2,
                          nonces=nonces,
                          template_nonces=["[X]", "[Y]"],)


scores = []
scores.append(evaluate_stimuli(model,stimulus_1, nonces))
scores.append(evaluate_stimuli(model,stimulus_2, nonces))


# print(scores)
with open("output.csv", 'w+', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    
    header = ["prompt", "question", "expected output", "generated output"]
    
    # Get 'dummy' connectives and nonces in the scores object to add all included nonces to the output csv header
    # so it doesn't depend on having nonces/prompts/questions in this file, which may change
    header.extend(scores[0][next(iter(scores[0].keys()))][next(iter(scores[0][next(iter(scores[0].keys()))].keys()))])
    
    writer.writerow(header)
    
    for score in scores:
        for conn in score.keys():
            for p, q, r in stimulus_1[conn]:

                # find max score
                max = ["none", -sys.maxsize]
                for nonce, val in score[conn][(p,q)].items():
                    print(nonce + ":", val)

                    if val[0] >= max[1]:
                        max[0] = nonce
                        max[1] = val[0]


                row = [p, q, r, max[0]]
                raw_score = [ val[0] for val in score[conn][(p,q)].values() ]
                row.extend(raw_score)
                writer.writerow(row)

                print("expected response: \"" + r + "\"\tMax response:", max[0], "\tWas correct?", max[0] == r )
                print(p, "\tQ:", q,"\t",score[conn][(p,q)], "\n")

print("#-----------------------------------------------------------#")
