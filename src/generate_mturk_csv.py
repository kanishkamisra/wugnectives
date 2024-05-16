import csv
import random

from generate_balanced_stimuli import write_stimuli

#unpack from csv (maybe not neccessary?)
pref_data = []
with open('data/stimuli/preference_stimuli.csv') as pref_csv_file:
        pref_reader = csv.reader(pref_csv_file)
        
        lines = 0
        
        for entry in pref_reader:
            if lines == 0:
                #header row
                # item_id,stimuli_type,connective,target,stimuli_instance,stimuli_instance_description,entity1,entity2,premise,inference1,inference2 = entry
                pass
            lines += 1
            pref_data.append(entry)

            
inst_data = []
with open('data/stimuli/preference_stimuli.csv') as inst_csv_file:
        inst_reader = csv.reader(inst_csv_file)
        
        lines = 0
        
        for entry in inst_reader:
            if lines == 0:
                #header row
                #item_id,stimuli_type,connective,target,stimuli_instance,stimuli_instance_description,entity1,entity2,premise,inference1,inference2 = entry
                pass
            lines += 1
            inst_data.append(entry)


causal_data = []
with open('data/stimuli/preference_stimuli.csv') as causal_csv_file:
        causal_reader = csv.reader(causal_csv_file)
        
        lines = 0
        
        for entry in causal_reader:
            if lines == 0:
                #header row
                #item_id,stimuli_type,connective,target,stimuli_instance,stimuli_instance_description,entity1,entity2,premise,inference1,inference2 = entry
                pass
            lines += 1
            causal_data.append(entry)


temp_data = []
with open('data/stimuli/preference_stimuli.csv') as temp_csv_file:
        temp_reader = csv.reader(temp_csv_file)
        
        lines = 0
        
        for entry in temp_reader:
            if lines == 0:
                #header row
                #item_id,stimuli_type,connective,target,stimuli_instance,stimuli_instance_description,entity1,entity2,premise,inference1,inference2 = entry
                pass
            lines += 1
            temp_data.append(entry)
    



# allocate questions, ensuring there is a mix, and a few temporal in each

# remove headers 
temp_data = temp_data[1:]
causal_data = causal_data[1:]
pref_data = pref_data[1:]
inst_data = inst_data[1:]


random.seed(2048)
random.shuffle(temp_data)
non_temp_data = []
non_temp_data.extend(inst_data)
non_temp_data.extend(causal_data)
non_temp_data.extend(pref_data)

random.shuffle(non_temp_data)



output = []
idx = 0
while (len(temp_data) + len(non_temp_data)) > 25:
    output.append([None] * 25)
    
    temp_instances = 5
    
    for i in range(temp_instances):
        if len(temp_data) != 0:
            output[idx][i] = temp_data[0]
            temp_data.remove(temp_data[0])
    
    for i in range(25 - temp_instances):
        if len(non_temp_data) != 0:
            output[idx][i + temp_instances] = non_temp_data[0]
            non_temp_data.remove(non_temp_data[0])
    
    # either temp xor non_temp data is empty
    while None in output[idx]:
        output[idx].remove(None)
        if len(temp_data) != 0:
            output[idx].append(temp_data[0])
            temp_data.remove(temp_data[0])
        else: 
            output[idx].append(non_temp_data[0])
            non_temp_data.remove(non_temp_data[0])
    
    
    random.shuffle(output[idx])
    
    idx += 1


print("Number of 25-stimuli hits generated:", len(output))
print("Unused temp_data", len(temp_data))
# print(temp_data)
print("Unused non_temp_data", len(non_temp_data))
# print(non_temp_data)


#prep for CSV output
mturk_header = ["premise_1","inference_1A","inference_id_1A","inference_1B","inference_id_1B","premise_2","inference_2A","inference_id_2A","inference_2B","inference_id_2B","premise_3","inference_3A","inference_id_3A","inference_3B","inference_id_3B","premise_4","inference_4A","inference_id_4A","inference_4B","inference_id_4B","premise_5","inference_5A","inference_id_5A","inference_5B","inference_id_5B","premise_6","inference_6A","inference_id_6A","inference_6B","inference_id_6B","premise_7","inference_7A","inference_id_7A","inference_7B","inference_id_7B","premise_8","inference_8A","inference_id_8A","inference_8B","inference_id_8B","premise_9","inference_9A","inference_id_9A","inference_9B","inference_id_9B","premise_10","inference_10A","inference_id_10A","inference_10B","inference_id_10B","premise_11","inference_11A","inference_id_11A","inference_11B","inference_id_11B","premise_12","inference_12A","inference_id_12A","inference_12B","inference_id_12B","premise_13","inference_13A","inference_id_13A","inference_13B","inference_id_13B","premise_14","inference_14A","inference_id_14A","inference_14B","inference_id_14B","premise_15","inference_15A","inference_id_15A","inference_15B","inference_id_15B","premise_16","inference_16A","inference_id_16A","inference_16B","inference_id_16B","premise_17","inference_17A","inference_id_17A","inference_17B","inference_id_17B","premise_18","inference_18A","inference_id_18A","inference_18B","inference_id_18B","premise_19","inference_19A","inference_id_19A","inference_19B","inference_id_19B","premise_20","inference_20A","inference_id_20A","inference_20B","inference_id_20B","premise_21","inference_21A","inference_id_21A","inference_21B","inference_id_21B","premise_22","inference_22A","inference_id_22A","inference_22B","inference_id_22B","premise_23","inference_23A","inference_id_23A","inference_23B","inference_id_23B","premise_24","inference_24A","inference_id_24A","inference_24B","inference_id_24B","premise_25","inference_25A","inference_id_25A","inference_25B","inference_id_25B"]
mturk_output = []

for hit in output:
    mturk_row = []
    for stimuli in hit:
        item_id,stimuli_type,connective,target,stimuli_instance,stimuli_instance_description,entity1,entity2,premise,inference1,inference2 = stimuli

        mturk_id_a = item_id + "_" + stimuli_instance + "_" + stimuli_type + "_" + entity1 + "_" + connective + "_" + entity2 + "_" + inference1 + "_" + target
        mturk_id_b = item_id + "_" + stimuli_instance + "_" + stimuli_type + "_" + entity1 + "_" + connective + "_" + entity2 + "_" + inference2 + "_" + target

        mturk_row.extend([premise, inference1, mturk_id_a, inference2, mturk_id_b])
    # print(len(mturk_row))
    mturk_output.append(mturk_row)


write_stimuli(mturk_output, "mturk_stimuli.csv", mturk_header)

