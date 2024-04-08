import pathlib
import random
from minicons import scorer
import numpy as np
import json
from input_generator import make_stimuli
from model_prompter import evaluate_dataset
import sys
import csv
from generate_stimuli import pref_dataset, causal_dataset, temporal_dataset, inst_dataset, write_stimuli
import argparse

parser = argparse.ArgumentParser(prog="Run model on all stimuli")
parser.add_argument("model_name")
parser.add_argument("compute")

args = parser.parse_args()

# model_name = "../../../shared/hf_cache/models--mistralai--Mistral-7B-v0.1/snapshots/26bca36bde8333b5d7f72e9ed20ccda6a618af24/"
# compute = 'cuda:0'

compute = ''
model_name = ''

if args.compute == None:
    compute = 'cpu'
else:
    compute = args.compute

if args.model_name == None:
    model_name = 'gpt2'
else:
    model_name = args.model_name


print("Running model " + model_name + " on " + compute + "...")


model = scorer.IncrementalLMScorer(model_name, compute)

pref_dataset
temporal_dataset
causal_dataset
inst_dataset

print("Running pref dataset...", end="")
pref_scores = evaluate_dataset(model, pref_dataset)
print("Finished.")
print("Running temporal dataset...", end="")
temporal_scores = evaluate_dataset(model, temporal_dataset)
print("Finished.")
print("Running causal dataset...", end="")
causal_scores = evaluate_dataset(model, causal_dataset)
print("Finished.")
print("Running causal dataset...", end="")
inst_scores = evaluate_dataset(model, inst_dataset)
print("Finished.")


header = ["id", "score", "nonce", "connective", "target", "statement", "conclusion"]

pathlib.Path("data/results/" + model_name +
             "/").mkdir(parents=True, exist_ok=True)
write_stimuli(pref_scores,     "data/results/" +
              model_name + "/preference_results.csv", header)
write_stimuli(temporal_scores, "data/results/" +
              model_name + "/temporal_results.csv", header)
write_stimuli(causal_scores,   "data/results/" +
              model_name + "/causal_results.csv", header)
write_stimuli(inst_scores,     "data/results/" + model_name +
              "/instantiation_results.csv", header)


# question = "Which city is the state capital?"
# argset_1 = ["I prefer [X] to [Y]", "I like state capitals."]
# conn_1 = ["because", "however", "although", "but", "as", "since", "for", "though", "nevertheless", "even though"]
# directions_1 = ["left", "right", "right", "right", "left", "left", "left", "right", "right", "right"]

# argset_2 = ["I like state capitals.", "I prefer [X] to [Y]."]
# conn_2 = [ "As a result", "Yet", "Even though", "though", "So", "Thus", "therefore", "But", "for example", "for instance", "nevertheless"]
# directions_2 = ["left", "right", "right", "right", "left", "right", "right", "right", "left", "left", "right"]


# nonces = ("wugsland", "daxville", "wugsburg", "daxtown", "wug","dax","xyz","abc","X","Y")

# stimulus_1 = make_stimuli(args=argset_1,
#                           question=question,
#                           connectives=conn_1,
#                           directions=directions_1,
#                           nonces=nonces,
#                           template_nonces=["[X]", "[Y]"],)

# stimulus_2 = make_stimuli(args=argset_2,
#                           question=question,
#                           connectives=conn_2,
#                           directions=directions_2,
#                           nonces=nonces,
#                           template_nonces=["[X]", "[Y]"],)


# scores = []
# scores.append((stimulus_1, evaluate_stimuli(model,stimulus_1)))
# scores.append((stimulus_2, evaluate_stimuli(model,stimulus_2)))


# # print(scores)
# with open("output.csv", 'w+', newline='') as csvfile:
#     writer = csv.writer(csvfile, delimiter=",")

#     header = ["connective", "prompt", "question", "right direction", "direction", "nonce_1", "nonce_2", "nonce_1_score", "nonce_2_score"]

#     writer.writerow(header)

#     for stimulus, score in scores:
#         for conn in score.keys():
#             for p, q, direction, nonce_1, nonce_2 in stimulus[conn]:

#                 # check right direction
#                 nonce_1_score =  score[conn][(p,q)][nonce_1]
#                 nonce_2_score =  score[conn][(p,q)][nonce_2]

#                 correct = False

#                 if direction == "left" and nonce_1_score >= nonce_2_score:
#                     correct = True
#                 if direction == "right" and nonce_2_score >= nonce_1_score:
#                     correct = True

#                 # print(direction, correct, nonce_1_score, nonce_2_score, "\n")

#                 row = [conn, p, q, correct, direction, nonce_1, nonce_2, nonce_1_score, nonce_2_score]
#                 writer.writerow(row)
