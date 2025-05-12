import csv
import random
from minicons import scorer
import numpy as np
import json
from input_generator import make_stimuli
import torch
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
        df_out.loc[df_out["inference_id_A"] == inference_A_id, "nonce_A"] = nonce_A
        df_out.loc[df_out["inference_id_A"] == inference_A_id, "nonce_B"] = nonce_B
        
        # imput these prompts into the dataframe
        df_out.loc[df_out["inference_id_A"] == inference_A_id, "prompt_QA"] = QA_prompt  
        df_out.loc[df_out["inference_id_A"] == inference_A_id, "prompt_A_YN"] = YN_prompt_A
        df_out.loc[df_out["inference_id_A"] == inference_A_id, "prompt_B_YN"] = YN_prompt_B

    return df_out


def setup_dataframe_simpleprompt(df_stim:pd.DataFrame):
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
        
        QA_prompt = premise
        
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



def _chat_template(sequence, tokenizer, post_text="Response:"):
    formatted = [{"role": "user", "content": sequence.strip()}]
    templated = tokenizer.apply_chat_template(
        formatted, tokenize=False, add_generation_prompt=True
    )
    reformatted = tokenizer.decode(
        tokenizer(templated, add_special_tokens=False).input_ids[1:]
    ) + f"{post_text}"
    return reformatted


def chat_prompt(name, premise, inference1, inference2, reason):
    output = {"post":"", "inference_A":"", "inference_B":""}

    if reason:
        output["post"] = ""
        output["inference_A"] =  "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n You have all the information to answer this question correctly in this statement alone, even if it is not explicit. Please reason step by step, and put your final answer within \\boxed{}."
        output["inference_B"] =  "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n You have all the information to answer this question correctly in this statement alone, even if it is not explicit. Please reason step by step, and put your final answer within \\boxed{}."
        return output

    output["post"] = ""
    # output["inference_A"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n Answer [Yes] or [No] only."
    # output["inference_B"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n Answer [Yes] or [No] only."
    output["inference_A"] =  "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n Answer with Yes or No only."
    output["inference_B"] =  "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n Answer with Yes or No only."
    return output


    if "google/gemma-2-2b-it" in name:
        output["post"] = "["
        output["inference_A"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n Answer [Yes] or [No] only."
        output["inference_B"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n Answer [Yes] or [No] only."
        return output

    if "google/gemma-2-9b-it" in name:
        output["post"] = "["
        output["inference_A"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n Answer [Yes] or [No] only."
        output["inference_B"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n Answer [Yes] or [No] only."
        return output

    if "google/gemma-3-4b-it" in name:
        output["post"] = "["
        output["inference_A"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n Answer [Yes] or [No] only."
        output["inference_B"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n Answer [Yes] or [No] only."
        return output

    if "allenai/OLMo-2-1124-7B-Instruct" in name:
        output["post"] = "Answer: "
        output["inference_A"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n Answer [Yes] or [No] only. Answer in the format 'Answer: [answer]'"
        output["inference_B"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n Answer [Yes] or [No] only. Answer in the format 'Answer: [answer]'"
        return output

    if "allenai/OLMo-2-1124-13B-Instruct" in name:
        output["post"] = "Answer: "
        output["inference_A"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n Answer Yes or No only.  Answer in the format 'Answer: '"
        output["inference_B"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n Answer Yes or No only.  Answer in the format 'Answer: '"
        return output

    if "Mistral-7B-Instruct-v0.3" in name:
        output["post"] = "'Answer: "
        output["inference_A"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n Answer [Yes] or [No] only. Answer in the format 'Answer: '"
        output["inference_B"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n Answer [Yes] or [No] only. Answer in the format 'Answer: '"
        return output

    if "Llama-3.1-8B-Instruct" in name:
        output["post"] = "["
        output["inference_A"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference1 + "'?\n Answer [No] or [Yes] only."
        output["inference_B"] = "Given the following statement:\n'" + premise + "'\n\nIs it true that '" + inference2 + "'?\n Answer [No] or [Yes] only."
        return output

    raise ValueError("Unsupported model name")

def setup_dataframe_chat(df_stim:pd.DataFrame, lm:scorer, model_name, reason):
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

    if reason:
        df_out.insert(column="gen_A", loc=len(df_out.columns), value=None)
        df_out.insert(column="gen_B", loc=len(df_out.columns), value=None)


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
        


        prompt_nonqa = "Given the following statement:\n" + premise + "\n\nProduce a valid conclusion: "

        prompts = chat_prompt(model_name, premise, inference_A[:-1], inference_B[:-1], reason=reason)
        prompt_yn_A = prompts["inference_A"]
        prompt_yn_B = prompts["inference_B"]



        # extract nonces from sentences, as the ID is unclear which Nonce is being targeted 
        nonce_A = inference_A_id.split("_")[-2].split(" ")[0]
        nonce_B = inference_B_id.split("_")[-2].split(" ")[0]
        
        QA_prompt = _chat_template(prompt_nonqa, lm.tokenizer, post_text=prompts["post"])
        
        YN_prompt_A = _chat_template(prompt_yn_A, lm.tokenizer, post_text=prompts["post"])
        YN_prompt_B = _chat_template(prompt_yn_B, lm.tokenizer, post_text=prompts["post"])
        
        #input nonces into the dataframes
        df_out.loc[df_out["premise"] == premise, "nonce_A"] = nonce_A
        df_out.loc[df_out["premise"] == premise, "nonce_B"] = nonce_B
        
        # imput these prompts into the dataframe
        df_out.loc[df_out["premise"] == premise, "prompt_QA"] = QA_prompt  
        df_out.loc[df_out["premise"] == premise, "prompt_A_YN"] = YN_prompt_A
        df_out.loc[df_out["premise"] == premise, "prompt_B_YN"] = YN_prompt_B
    
    return df_out

def generate(lm:scorer.IncrementalLMScorer, prompt:str, post_text=""):
    model = lm.model
    tokenizer = lm.tokenizer
    text = _chat_template(prompt, tokenizer, post_text)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(**model_inputs, max_new_tokens=32768, temperature=0.6)
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # print(text)
    # print(response)
    return response



def p_yes(probs, n_yes_opts=2):
    alls = torch.tensor(probs).sum(1)
    yeses = [p[0:n_yes_opts] for p in probs]
    return (torch.tensor(yeses).sum(1) / alls)




def run_model(model:scorer, model_name:str, df:pd.DataFrame, chat=False, noformat=False, reason=False):
    df_out = df.copy()
    if chat:
        chat = True
    if noformat == True:
        chat = True

    if "pythia" in model_name or "gpt2" in model_name:
        bos = True
    else:
        bos = False

    #progress bar
    from tqdm import tqdm
    out_QA_A = []
    out_QA_B = []

    out_gen_A = []
    out_gen_B = []
          
    out_A_YN_Y = []
    out_A_YN_N = []
    out_B_YN_Y = []
    out_B_YN_N = []

    for index, row in tqdm(df_out.iterrows(),desc="Running Model...", total=len(df_out)):
        # premise         = row["premise"]

        # get scores
        if not chat:
            rating_QA_A = model.conditional_score(row["prompt_QA"], row["inference_A"])[0]
            rating_QA_B = model.conditional_score(row["prompt_QA"], row["inference_B"])[0]

            out_QA_A.append(rating_QA_A)
            out_QA_B.append(rating_QA_B)

        # if chat and not reason:
        #     rating_A_YN_Y = model.conditional_score(row["prompt_A_YN"], "Yes", chat=chat, separator="")[0]
        #     rating_A_YN_N = model.conditional_score(row["prompt_A_YN"], "No", chat=chat , separator="")[0] 
        #     rating_B_YN_Y = model.conditional_score(row["prompt_B_YN"], "Yes", chat=chat, separator="")[0]
        #     rating_B_YN_N = model.conditional_score(row["prompt_B_YN"], "No", chat=chat , separator="")[0] 
        if reason:
            gen_A = generate(model, row["prompt_A_YN"], "")
            gen_B = generate(model, row["prompt_B_YN"], "")
        else:
            prompts = (row["prompt_A_YN"], row["prompt_B_YN"])
            dist = model.next_word_distribution(prompts, bos_token=bos, chat=chat)
            probs, ranks = model.query(dist, [["Yes", "yes", "No", "no"]]*len(prompts))
            yes_probs = p_yes(probs)
            no_probs = 1 - yes_probs
            
            yes_probs = yes_probs.log().tolist()
            no_probs = no_probs.log().tolist()

            rating_A_YN_Y = yes_probs[0]
            rating_A_YN_N = no_probs[0]
            rating_B_YN_Y = yes_probs[1]
            rating_B_YN_N = no_probs[1]

            # rating_A_YN_Y = model.conditional_score(row["prompt_A_YN"], "Yes")[0]
            # rating_A_YN_N = model.conditional_score(row["prompt_A_YN"], "No")[0] 
            # rating_B_YN_Y = model.conditional_score(row["prompt_B_YN"], "Yes")[0]
            # rating_B_YN_N = model.conditional_score(row["prompt_B_YN"], "No")[0] 

        

        if not reason:
            out_A_YN_Y.append(rating_A_YN_Y)
            out_A_YN_N.append(rating_A_YN_N)
            out_B_YN_Y.append(rating_B_YN_Y)
            out_B_YN_N.append(rating_B_YN_N)
        else:
            out_gen_A.append(gen_A)
            out_gen_B.append(gen_B)

        # insert scores into dataframe
        # if not chat:
            # df_out.loc[df_out["premise"] == premise, "rating_QA_A"] =  rating_QA_A
            # df_out.loc[df_out["premise"] == premise, "rating_QA_B"] =  rating_QA_B
        # 
        # df_out.loc[df_out["premise"] == premise, "rating_A_YN_Y"] =  rating_A_YN_Y
        # df_out.loc[df_out["premise"] == premise, "rating_A_YN_N"] =  rating_A_YN_N
        # df_out.loc[df_out["premise"] == premise, "rating_B_YN_Y"] =  rating_B_YN_Y
        # df_out.loc[df_out["premise"] == premise, "rating_B_YN_N"] =  rating_B_YN_N
    
    if not chat or noformat:
        df_out["rating_QA_A"] =  out_QA_A
        df_out["rating_QA_B"] =  out_QA_B

    if not reason:
        df_out["rating_A_YN_Y"] =  out_A_YN_Y
        df_out["rating_A_YN_N"] =  out_A_YN_N
        df_out["rating_B_YN_Y"] =  out_B_YN_Y
        df_out["rating_B_YN_N"] =  out_B_YN_N
    else: 
        df_out["gen_A"] = out_gen_A
        df_out["gen_B"] = out_gen_B
    # model.conditional_score(given_str + produce_str_1, conclusion_1)[0]
    
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

        score_1 = model.conditional_score(given_str + produce_str_1, conclusion_1)[0]
        score_2 = model.conditional_score(given_str + produce_str_2, conclusion_2)[0]

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
                
            score_1 = model.conditional_score(given_str + produce_str_1, conclusion_1)[0]
            score_2 = model.conditional_score(given_str + produce_str_2, conclusion_2)[0]

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
                score_1 = model.conditional_score(prompt + " " + question, nonce_1)
                score_2 = model.conditional_score(prompt + " " + question, nonce_2)


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

