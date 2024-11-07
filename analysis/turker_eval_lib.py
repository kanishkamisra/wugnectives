import re
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from collections import defaultdict
from scipy import stats


def get_q_answers_raw(df, category, item):
    pattern = re.compile("^Answer\." + str(item) + "_.*_" + str(category) + ".*")

    keep_cols =  [c for c in df.columns if (re.search(pattern, c) or c == "WorkerId")]     
    df = df[keep_cols]

    df = df.dropna(axis=0, how="any")
    return df

def get_q_answers(df:pd.DataFrame, category, item):
    answers = get_q_answers_raw(df, category, item)
    answers.insert(loc=3, column="Choice", value=None)
    
    index = 0
    for _, row in answers.iterrows():
        if answers.iloc[index, 1] > answers.iloc[index, 2]:
            answers.iloc[index, 3] = 1
        elif answers.iloc[index, 1] < answers.iloc[index, 2]:
            answers.iloc[index, 3] = 2
        index += 1
    
    return answers

def get_q_consensus(_df:pd.DataFrame, category, item):
    df = get_q_answers(_df, category, item)
    
    consensus_vals = df["Choice"].value_counts(dropna=False)
    
    freq_None = consensus_vals.get(None)
    freq_1 = consensus_vals.get(1)
    freq_2 = consensus_vals.get(2)

    if freq_None == None:
        freq_None = -1
    if freq_1 == None:
        freq_1 = -1
    if freq_2 == None:
        freq_2 = -1
    
    max = np.max([freq_None, freq_1, freq_2])
    consensus = []
    if max == -1:
        raise Exception("TODO: fix this if it ever happens")
    
    if max == freq_None:
        consensus.append(None)
    if max == freq_1:
        consensus.append(1)
    if max == freq_2:
        consensus.append(2)
    
    df.insert(loc=4, column="agree_w_consensus", value=0)
    df.loc[(df["Choice"].isin(consensus)), "agree_w_consensus"] = 1
    # df.loc[(df["agree_w_consensus"] = None, "agree_w_consensus"] = 1
    
    return df

def get_q_consensus_nonone(_df:pd.DataFrame, category, item):
    df = get_q_answers(_df, category, item)
    
    consensus_vals = df["Choice"].value_counts(dropna=False)
    
    freq_None = consensus_vals.get(None)
    freq_1 = consensus_vals.get(1)
    freq_2 = consensus_vals.get(2)

    if freq_None == None:
        freq_None = -1
    if freq_1 == None:
        freq_1 = -1
    if freq_2 == None:
        freq_2 = -1
    
    max = np.max([freq_None, freq_1, freq_2])
    consensus = []
    if max == -1:
        raise Exception("TODO: fix this if it ever happens")
    
    # if max == freq_None:
    #     consensus.append(None)
    if max == freq_1:
        consensus.append(1)
    if max == freq_2:
        consensus.append(2)
    
    df.insert(loc=4, column="agree_w_consensus", value=0)
    df.loc[(df["Choice"].isin(consensus)), "agree_w_consensus"] = 1
    # df.loc[(df["agree_w_consensus"] = None, "agree_w_consensus"] = 1
    
    return df

def get_batch_questions(_df:pd.DataFrame):
    df = get_answers(_df)
    cols = list(df.columns[1:])
    questions = []
    for col in cols:
        col = col.lstrip("Answers.")
        vals = col.split("_")
        q = (vals[2], vals[0])
        questions.append(q)
        
    return set(questions)

def get_answers(df) -> pd.DataFrame:
    keep_cols =  [c for c in df.columns if (c.startswith("Answer.") or c == "WorkerId")] 
    df = df[keep_cols]
    return df

def get_abs_batch(_df, num):
    num = num - 1 # 1 index
    start = 0 + (num * 9)
    end = 9 + (num * 9)
    df = _df[start:end]
    df = df.dropna(axis=1, how="any")
    
    return df

def get_batch(_df, num):
    num = num - 1 # 1 index
    start = 0 + (num * 9)
    end = 9 + (num * 9)

    last_q = ""
    for column in reversed(_df[start:end].dropna(axis=1, how="any").columns):
        if column.startswith("Answer."):
            last_q = column
            break
    if last_q == "":
        assert(False)


    df = _df.copy()
    indices = []
    
    for index, row in _df.iterrows():
        if math.isnan(row[last_q]) :
            indices.append(index)
    df.drop(index=indices,axis=1, inplace=True)
    df = df.dropna(axis=1, how="any")
    return df


def agreement(_df:pd.DataFrame, batch:int):
    df_sample = get_batch(_df, batch)
    # answers = get_answers(df_sample)
    
    workers = {w:0 for w in df_sample["WorkerId"]}
    # workers["TOTAL"] = 0
    
    for category, item in get_batch_questions(df_sample):
        
        consensus = get_q_consensus(df_sample, category, item)


        for index in consensus.index:
            agree = consensus["agree_w_consensus"][index]
            worker = consensus["WorkerId"][index]
            workers[worker] += agree
        # workers["TOTAL"] += 1
    return workers

# def agreement_nonone(_df:pd.DataFrame, batch:int):
#     df_sample = get_batch(_df, batch)
#     # answers = get_answers(df_sample)
    
#     workers = {w:0 for w in df_sample["WorkerId"]}
#     # workers["TOTAL"] = 0
    
#     for category, item in get_batch_questions(df_sample):
#         # print(category, item)
#         consensus = get_q_consensus_nonone(df_sample, category, item)


#         for index in consensus.index:
#             agree = consensus["agree_w_consensus"][index]
#             worker = consensus["WorkerId"][index]
#             workers[worker] += agree
#         # workers["TOTAL"] += 1
#     return workers



def find_bottom(df:pd.DataFrame,  sortcolumn, returncolumn, percent):
    if percent == 0:
        return df[returncolumn]    
    assert(percent > 0 and percent <= 100)
    
    return df.nsmallest(math.ceil((len (df) * percent) / 100), sortcolumn)[returncolumn]
    

def cut_bottom(df:pd.DataFrame, column, percent):
    if percent == 0:
        return df
    assert(percent > 0 and percent <= 100)
    percent = 100 - percent 
    
    return df.nlargest((len (df) * percent) // 100, column)

def cut_agreements(to_cut, all_agreements, percentify = False):
    output = all_agreements.copy()
    for worker in to_cut:
        if worker in output:
            output.pop(worker)
    if percentify:
        for worker in output:
            output[worker] = output[worker] / 25 
    return output

def get_q_consensus_without(_df:pd.DataFrame, category, item, without):
    
    df = get_q_answers(_df, category, item)
    for worker in without:
        if worker in list(df["WorkerId"]):
            df = df.loc[df["WorkerId"] != worker]
    
    
    consensus_vals = df["Choice"].value_counts(dropna=False)
    
    freq_None = consensus_vals.get(None)
    freq_1 = consensus_vals.get(1)
    freq_2 = consensus_vals.get(2)

    if freq_None == None:
        freq_None = -1
    if freq_1 == None:
        freq_1 = -1
    if freq_2 == None:
        freq_2 = -1
    
    max = np.max([freq_None, freq_1, freq_2])
    consensus = []
    if max == -1:
        raise Exception("TODO: fix this if it ever happens")
    
    if max == freq_None:
        consensus.append(None)
    if max == freq_1:
        consensus.append(1)
    if max == freq_2:
        consensus.append(2)
    
    df.insert(loc=4, column="agree_w_consensus", value=0)
    df.loc[(df["Choice"].isin(consensus)), "agree_w_consensus"] = 1
    # df.loc[(df["agree_w_consensus"] = None, "agree_w_consensus"] = 1
    
    return df

def agreement_without_bottom(_df:pd.DataFrame, batch:int, without):
    df_sample = get_batch(_df, batch)
    # answers = get_answers(df_sample)
    
    workers = {w:0 for w in df_sample["WorkerId"]}
    for worker in without:
        if worker in workers:
            workers.pop(worker)

    
    for category, item in get_batch_questions(df_sample):
        
        consensus = get_q_consensus_without(df_sample, category, item, without)

        for index in consensus.index:
            agree = consensus["agree_w_consensus"][index]
            worker = consensus["WorkerId"][index]
            workers[worker] += agree

    return workers








def gold_accuracy(df_gold:pd.DataFrame, name, consensus="consensus"):
    correct = 0
    
    if consensus == "easyconsensus":
        correct = len(df_gold[(df_gold[name] == df_gold["consensus"])]) + df_gold["consensus"].value_counts(dropna=False)[None]
    else:
        correct = len(df_gold[df_gold[name] == df_gold[consensus]])

    total = len(df_gold)
    return correct / total

def get_overlap(df_base):
    gold_contained = {"preference":set(), "temporal":set(), "instantiation":set()}
    contained = {"preference":set(), "temporal":set(), "instantiation":set()}
    result = {"preference":set(), "temporal":set(), "instantiation":set()}

    inst_list = [6, 17, 22, 33]
    pref_list = [7, 12, 27, 33, 47, 58, 68, 79, 86, 100, 110, 112, 121, 132, 142, 152, 166, 176, 181, 1, 14, 21, 32, 41, 55, 63, 74, 88, 97, 106, 111, 126, 133, 141, 159, 170, 172, 187]
    temp_list = [6, 15, 23, 33, 43, 57, 65, 73, 82, 94, 110, 112, 128, 139, 141, 157, 161, 171, 184, 193, 206, 216, 228, 2, 16, 30, 32, 41, 52, 66, 77, 85, 92, 101, 114, 123, 132, 145, 155, 163, 173, 183, 194, 207, 218, 224]

    gold_contained["instantiation"].update(set(inst_list))
    gold_contained["preference"].update(set(pref_list))
    gold_contained["temporal"].update(set(temp_list))

    overlap_contained = {"preference":set(), "temporal":set(), "instantiation":set()}
    stim_category = {"preference", "temporal", "instantiation"}

    for column in df_base.columns:
        
        if not column.startswith("Answer"):
            pass #skip the first row
        
        column = column.lstrip("Answers.")
        vals = column.split("_")
        
        if "preference" in column:
            contained["preference"].add(int(vals[0]))

        elif "temporal" in column:
            contained["temporal"].add(int(vals[0]))
            
        elif "instantiation" in column:
            contained["instantiation"].add(int(vals[0]))
        
    result["preference"] = gold_contained["preference"].intersection(contained["preference"])
    result["instantiation"] = gold_contained["instantiation"].intersection(contained["instantiation"])
    result["temporal"] = gold_contained["temporal"].intersection(contained["temporal"])
    return result



def get_gold_q_answers(df:pd.DataFrame, category, item):
    return df.loc[(df["stimuli-type"] == category) & (df.item == item)] 





def get_consensus_worker_accuracy(df_base:pd.DataFrame, df_gold:pd.DataFrame, batch):
    stim_category = {"preference", "temporal", "instantiation"}
    overlap = get_overlap(get_batch(df_base, batch))
    # print(overlap)

    workers = {}

     # get all WorkerIds
    for worker in get_batch(df_base, batch)["WorkerId"]:
        workers[worker] = [0,0,0]
    # print(workers)
    
    for category in stim_category:
        for item in overlap[category]:
            
            # print(category, item)
            
            gold_answers = get_gold_q_answers(df_gold, category, item)
            worker_answers = get_q_answers(df_base, category, item)
            
            gold_answer = gold_answers.iloc[0,12]
            # print(gold_answers.iloc[0,14])
            
            for worker in workers.keys():
                # print("\t", worker_answers.loc[worker_answers['WorkerId'] == worker].iloc[0,3])
                worker_answer = worker_answers.loc[worker_answers['WorkerId'] == worker].iloc[0,3]
                if worker_answer == gold_answer:
                    workers[worker][0] += 1
    
    total_vals = sum([len(overlap["preference"]),len(overlap["temporal"]),len(overlap["instantiation"]), ])
    for worker in workers.keys():
        workers[worker][1] = (total_vals)
        workers[worker][2] = (workers[worker][0] / total_vals)

    return workers

def get_easyconsensus_worker_accuracy(df_base:pd.DataFrame, df_gold:pd.DataFrame, batch):
    stim_category = {"preference", "temporal", "instantiation"}
    overlap = get_overlap(get_batch(df_base, batch))
    # print(overlap)

    workers = {}

     # get all WorkerIds
    for worker in get_batch(df_base, batch)["WorkerId"]:
        workers[worker] = [0,0,0]
    # print(workers)
    
    for category in stim_category:
        for item in overlap[category]:
            
            # print(category, item)
            
            gold_answers = get_gold_q_answers(df_gold, category, item)
            worker_answers = get_q_answers(df_base, category, item)
            
            gold_answer = gold_answers.iloc[0,12]
            # print(gold_answers.iloc[0,14])
            
            for worker in workers.keys():
                # print("\t", worker_answers.loc[worker_answers['WorkerId'] == worker].iloc[0,3])
                worker_answer = worker_answers.loc[worker_answers['WorkerId'] == worker].iloc[0,3]
                if gold_answer == None: #TODO - Deal with case where worker chose 'neither'
                    workers[worker][0] += 1
                elif worker_answer == gold_answer:
                    workers[worker][0] += 1
    
    total_vals = sum([len(overlap["preference"]),len(overlap["temporal"]),len(overlap["instantiation"]), ])
    for worker in workers.keys():
        workers[worker][1] = (total_vals)
        workers[worker][2] = (workers[worker][0] / total_vals)

    return workers

def get_majority_worker_accuracy(df_base:pd.DataFrame, df_gold:pd.DataFrame, batch):
    stim_category = {"preference", "temporal", "instantiation"}
    overlap = get_overlap(get_batch(df_base, batch))
    # print(overlap)

    workers = {}

     # get all WorkerIds
    for worker in get_batch(df_base, batch)["WorkerId"]:
        workers[worker] = [0,0,0]
    # print(workers)
    
    for category in stim_category:
        for item in overlap[category]:
            
            # print(category, item)
            
            gold_answers = get_gold_q_answers(df_gold, category, item)
            worker_answers = get_q_answers(df_base, category, item)
            
            gold_answer = gold_answers.iloc[0,10]
            # print(gold_answers.iloc[0,14]
            
            for worker in workers.keys():
                # print("\t", worker_answers.loc[worker_answers['WorkerId'] == worker].iloc[0,3])
                worker_answer = worker_answers.loc[worker_answers['WorkerId'] == worker].iloc[0,3]
                if gold_answer == None: #TODO - Deal with case where worker chose 'neither'
                    workers[worker][0] += 1
                if worker_answer == gold_answer:
                    workers[worker][0] += 1
    
    total_vals = sum([len(overlap["preference"]),len(overlap["temporal"]),len(overlap["instantiation"]), ])
    for worker in workers.keys():
        workers[worker][1] = (total_vals)
        workers[worker][2] = (workers[worker][0] / total_vals)

    return workers