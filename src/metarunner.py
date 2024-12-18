import csv
import os
import argparse
import getpass

# Runs runner.py over multiple models
# Mostly as a quick solution to memory errors that built up with a plain for loop inside runner.py

parser = argparse.ArgumentParser(prog="Run Specified models on all human evaluated stimuli")

parser.add_argument("models_csv")
parser.add_argument("compute")
parser.add_argument("--use_hf_token", default=False)
parser.add_argument("--use_chat", default=False, action=argparse.BooleanOptionalAction)

args = parser.parse_args()

token = ""

if args.compute == None:
    compute = 'cpu'
else:
    compute = args.compute
if not args.use_hf_token == False:
    token = getpass("Input your huggingface access token.")

use_chat = ""
if args.use_chat:
    use_chat = "--use_chat"

with open(args.models_csv) as csv_file:
    models_csv = csv.reader(csv_file)
    lines = -1
    
    for entry in models_csv:
        model, outfile, delete_afterwards = entry
        lines += 1
        
        if lines == 0:
            # header row
            if not (model == "model" and outfile == "outfile" and "delete_afterwards" == delete_afterwards):
                print("malformed CSV. Must start have headers \"model\", \"outfile\", and \"delete_afterwards\"")
                print("You have", model + ",", outfile + ", and", delete_afterwards)
                break
            else:
                continue
        
        # normalize delete_afterwards to a bool from a string
        delete_afterwards = (delete_afterwards.lower().strip() == "true")
        
        print(model, outfile, delete_afterwards, type(delete_afterwards))
        if "70B-Instruct" in model:
            print("RUNNING LLAMA 70B INSTRUCT ")
            os.system("HF_HOME=\"~/tmpcache\" TRANSFORMERS_CACHE=\"~/tmpcache\" python src/runner.py " + model + " " + outfile + " " + compute + " " + token + " " + use_chat)
        else:
            os.system("python src/runner.py " + model + " " + outfile + " " + compute + " " + token + " " + use_chat)
           
        if delete_afterwards:
            # doesn't work so just commented out for now
            
            # path = "/home/shared/hf_cache/models--" + model.replace("/", "--")
            # print("deleting", path + "...")
            # os.system("rm -rI path")
            pass

#                       models--google--gemma-2-2b
# /home/shared/hf_cache/models--google--gemma-2-2b
    
# for model_name, outfile in zip(gemma_model_dirs, gemma_output_files):
    