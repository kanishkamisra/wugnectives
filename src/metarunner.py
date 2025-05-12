import csv
import os
import argparse
import getpass 
from getpass import getpass

# Runs runner.py over multiple models
# Mostly as a quick solution to memory errors that built up with a plain for loop inside runner.py

parser = argparse.ArgumentParser(prog="Run Specified models on all human evaluated stimuli")

parser.add_argument("models_csv")
parser.add_argument("compute")
parser.add_argument("--use_hf_token", default=False, action=argparse.BooleanOptionalAction)
parser.add_argument("--use_chat", default=False, action=argparse.BooleanOptionalAction)
parser.add_argument("--use_chat_noformat", default=False, action=argparse.BooleanOptionalAction)
parser.add_argument("--reason", default=False, action=argparse.BooleanOptionalAction)
parser.add_argument("--prefix_name", default="")
parser.add_argument("--temp_stim", default=False, action=argparse.BooleanOptionalAction)
args = parser.parse_args()

with open("failures.txt", "w") as file:
    # opening in w should clear file
    file.close()

from datetime import datetime
now = datetime.now()
date_str = now.strftime("%y-%m-%d_%H:%M_")



token = ""


if args.use_chat and args.use_chat_noformat:
    raise ValueError("Select only one of --use_chat or --use_chat_noformat. Both set chat=True, but noformat does not add the chat template (i.e. <|user|>)")

if args.compute == None:
    compute = 'cpu'
else:
    compute = args.compute
if not args.use_hf_token == False:
    token = getpass("Input your huggingface access token.")

use_chat = ""
if args.use_chat:
    print("CHATTING\n\n")
    use_chat = "--use_chat"

noformat = ""
if args.use_chat_noformat:
    noformat = "--use_chat_noformat"


reason = ""
if args.reason:
    print("REASONING\n\n")
    reason = "--reason"

temp_stim = ""
if args.temp_stim:
    print("Temporal stimuli\n\n")
    use_chat = "--temp_stim"


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
        outfile = args.prefix_name + outfile
        print(model, outfile, delete_afterwards, type(delete_afterwards))
        if not token == "":
            os.system("python src/runner.py " + model + " " + outfile + " " + compute + " --hf_token " + token + " " + use_chat + " " + reason + " " + temp_stim + " " + noformat)
        else:
            os.system("python src/runner.py " + model + " " + outfile + " " + compute + " " + token + " " + use_chat + " " + reason + " " + temp_stim + " " + noformat)
           
        if delete_afterwards:
            # doesn't work so just commented out for now
            
            # path = "/home/shared/hf_cache/models--" + model.replace("/", "--")
            # print("deleting", path + "...")
            # os.system("rm -rI path")
            pass

import shutil
shutil.move('failure.txt', date_str + 'failure.txt')
