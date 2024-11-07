import os
import argparse

# Runs runner.py over multiple models
# Mostly as a quick solution to memory errors that built up with a plain for loop inside runner.py

parser = argparse.ArgumentParser(prog="Run Specified models on all human evaluated stimuli")

parser.add_argument("compute")
args = parser.parse_args()

if args.compute == None:
    compute = 'cpu'
else:
    compute = args.compute

model_dirs = [
    "/home/shared/hf_cache/models--mistralai--Mistral-7B-v0.3/snapshots/7e728d76bdbc28c23c0ff5de71bf45663be9ff36/", 
    "/home/shared/hf_cache/models--meta-llama--Llama-3.2-3B/snapshots/5cc0ffe09ee49f7be6ca7c794ee6bd7245e84e60/", 
    # "/home/shared/hf_cache/models--meta-llama--Llama-3.2-3B-Instruct/snapshots/392a143b624368100f77a3eafaa4a2468ba50a72/", -- DOESN'T WORK
    "/home/shared/hf_cache/models--babylm--babyllama-100m-2024/snapshots/9c1aeb3459c892ad28fd56ece6672a223c43ba9c/", 
    "/home/shared/hf_cache/models--babylm--opt-125m-strict/snapshots/cdc1b7349c61df949df94a03bdd7b43be5313cec/", 
    "/home/shared/hf_cache/models--mistralai--Mistral-7B-Instruct-v0.3/snapshots/d79d1742f78eb0cc788c11e5b41a7539d7cb56ef/", 
    "/home/shared/hf_cache/models--meta-llama--Llama-3.1-8B/snapshots/d04e592bb4f6aa9cfee91e2e20afa771667e1d4b/", 
    "/home/shared/hf_cache/models--meta-llama--Llama-3.1-8B-Instruct/snapshots/0e9e39f249a16976918f6564b8830bc894c89659/",
    "gpt2"
]

output_files = [
    "mistralai--Mistral-7B-v0.3", 
    "meta-llama--Llama-3.2-3B", 
    # "meta-llama--Llama-3.2-3B-Instruct",  -- DOESN'T WORK
    "babylm--babyllama-100m-2024", 
    "babylm--opt-125m-strict", 
    "mistralai--Mistral-7B-Instruct-v0.3", 
    "meta-llama--Llama-3.1-8B", 
    "meta-llama--Llama-3.1-8B-Instruct",
    "gpt2"
]


for model_name, outfile in zip(model_dirs, output_files):
    os.system("python src/runner.py " + model_name + " " + outfile + " " + compute)
    