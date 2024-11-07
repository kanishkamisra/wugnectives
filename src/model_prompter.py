import csv
import random
from minicons import scorer
import numpy as np
import json
from input_generator import make_stimuli
import pandas as pd
# model = scorer.IncrementalLMScorer('gpt2', 'cpu')


def format_stimuli(df_stim_raw:pd.DataFrame):
    cols = ["premise", "inference_A", "inference_id_A", "inference_B", "inference_id_B"]
    
    df_stim = pd.DataFrame(columns=cols)
    
    for _, row in df_stim_raw.iterrows():
        for idx in range(0, int(len(row) / len(cols))):
            premise         = row.iloc[len(cols) * idx + 0]
            inference_A     = row.iloc[len(cols) * idx + 1]
            inference_A_id  = row.iloc[len(cols) * idx + 2]
            inference_B     = row.iloc[len(cols) * idx + 3]
            inference_B_id  = row.iloc[len(cols) * idx + 4]
            
            to_add = [premise, inference_A, inference_A_id, inference_B, inference_B_id]
            df_stim.loc[len(df_stim)] = to_add
            
    return df_stim

def setup_dataframe(df_stim:pd.DataFrame):
    df_out = df_stim.copy()
    
    df_out.insert(column="nonce_A", loc=len(df_out.columns), value=None)
    df_out.insert(column="nonce_B", loc=len(df_out.columns), value=None)

    # df_output.insert(column="inference_A", loc=len(df_output.columns), value=None)
    # df_output.insert(column="inference_B", loc=len(df_output.columns), value=None)
    
    # one column for each prompt - QA
    df_out.insert(column="prompt_QA", loc=len(df_out.columns), value=None)
    
    df_out.insert(column="prompt_A_YN", loc=len(df_out.columns), value=None)
    df_out.insert(column="prompt_B_YN", loc=len(df_out.columns), value=None)
    
    # one column for each rating - QA 
    df_out.insert(column="rating_QA_A", loc=len(df_out.columns), value=None)
    df_out.insert(column="rating_QA_B", loc=len(df_out.columns), value=None)

    df_out.insert(column="rating_A_YN_Y", loc=len(df_out.columns), value=None)
    df_out.insert(column="rating_A_YN_N", loc=len(df_out.columns), value=None)
    df_out.insert(column="rating_B_YN_Y", loc=len(df_out.columns), value=None)
    df_out.insert(column="rating_B_YN_N", loc=len(df_out.columns), value=None)
    
    
    for index, row in df_stim.iterrows():       
        
        premise         = row["premise"]
        inference_A     = row["inference_A"]
        inference_A_id  = row["inference_id_A"]
        inference_B     = row["inference_B"]
        inference_B_id  = row["inference_id_B"]
        
        # extract nonces from sentences, as the ID is unclear which Nonce is being targeted 
        nonce_A = inference_A_id.split("_")[-2].split(" ")[0]
        nonce_B = inference_B_id.split("_")[-2].split(" ")[0]
        
        QA_prompt = "Given the following statement:\n" + premise + "\n\nProduce a valid conclusion: "
        
        YN_prompt_A = "Given the following statement:\n" + premise + "\n\nIs it true that " + inference_A[:-1] + "? Answer yes or no: "
        YN_prompt_B = "Given the following statement:\n" + premise + "\n\nIs it true that " + inference_B[:-1] + "? Answer yes or no: "
        
        #input nonces into the dataframes
        df_out.loc[df_out["premise"] == premise, "nonce_A"] = nonce_A
        df_out.loc[df_out["premise"] == premise, "nonce_B"] = nonce_B
        
        # imput these prompts into the dataframe
        df_out.loc[df_out["premise"] == premise, "prompt_QA"] = QA_prompt  
        df_out.loc[df_out["premise"] == premise, "prompt_A_YN"] = YN_prompt_A
        df_out.loc[df_out["premise"] == premise, "prompt_B_YN"] = YN_prompt_B
    
    return df_out

def run_model(model:scorer, df:pd.DataFrame):
    df_out = df.copy()
    
    for index, row in df_out.iterrows():
        premise         = row["premise"]
        
        # get scores
        rating_QA_A = model.partial_score(row["prompt_QA"], row["inference_A"])[0]
        rating_QA_B = model.partial_score(row["prompt_QA"], row["inference_B"])[0]

        rating_A_YN_Y = model.partial_score(row["prompt_A_YN"], "yes")[0]
        rating_A_YN_N = model.partial_score(row["prompt_A_YN"], "no")[0] 
        rating_B_YN_Y = model.partial_score(row["prompt_B_YN"], "yes")[0]
        rating_B_YN_N = model.partial_score(row["prompt_B_YN"], "no")[0] 
        
        # insert scores into dataframe
        df_out.loc[df_out["premise"] == premise, "rating_QA_A"] =  rating_QA_A
        df_out.loc[df_out["premise"] == premise, "rating_QA_B"] =  rating_QA_B
        
        df_out.loc[df_out["premise"] == premise, "rating_A_YN_Y"] =  rating_A_YN_Y
        df_out.loc[df_out["premise"] == premise, "rating_A_YN_N"] =  rating_A_YN_N
        df_out.loc[df_out["premise"] == premise, "rating_B_YN_Y"] =  rating_B_YN_Y
        df_out.loc[df_out["premise"] == premise, "rating_B_YN_N"] =  rating_B_YN_N
        
    # model.partial_score(given_str + produce_str_1, conclusion_1)[0]
    
    return df_out



















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


def evaluate_human_dataset(model: scorer):
    results = []
    with open('data/random_sampled_stimuli.csv') as csv_file:
        human_dataset = csv.reader(csv_file)
        lines = 0
        
        for entry in human_dataset:
            if lines == 0:
                # header row
                pass
            lines += 1
            
            e1 = entry[5].split()[0] # the nonces are the first words in the infrences, not stored elsewhere
            e2 = entry[6].split()[0] # same as above

            statement = entry[4]
        
            given_str = "Given the following statement:\n" + statement
            produce_str_1 = "\n\nproduce a valid conclusion about " + e1+ ":"
            produce_str_2 = "\n\nproduce a valid conclusion about " + e2 + ":"
    
            conclusion_1 = entry[5]
            conclusion_2 = entry[6]
                
            score_1 = model.partial_score(given_str + produce_str_1, conclusion_1)[0]
            score_2 = model.partial_score(given_str + produce_str_2, conclusion_2)[0]

            score_1 = 1
            score_2 = 2
    
            output = []
            output.extend(entry)
            output.append(score_1)
            output.append(score_2)
            
            print(output)
            
            results.append(output)
    
    return results


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

