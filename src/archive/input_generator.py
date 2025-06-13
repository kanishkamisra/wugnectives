import itertools

# Function for generating stimulus, given two args(phrases), a templated base question,
# a list of connectives, and a list of the template nonces used.
#
# Returns: dict of connectives, mapping to a list of (prompt, question, correct_response) stimuli
def make_stimuli(args, question, connectives, directions, nonces, template_nonces):
    
    template_prompts = []
    
    for conn in connectives:
        template_prompts.append((conn,args[0] + " " + conn + " " + args[1]))
        
    output_prompts = {conn:[] for conn in connectives}

    for (conn, prompt), direction in zip(template_prompts, directions):
        for nonce_1, nonce_2 in itertools.permutations(nonces, 2):
            new_prompt = prompt.replace(template_nonces[0], nonce_1).replace(template_nonces[1], nonce_2)
            new_question = question.replace(template_nonces[0], nonce_1).replace(template_nonces[1], nonce_2)
            
            output_prompts[conn].append((new_prompt, new_question, direction, nonce_1, nonce_2))
            
            # if direction == "right": 
                # output_prompts[conn].append((new_prompt, new_question, nonce_2))
                
            # else:
                # output_prompts[conn].append((new_prompt, new_question, nonce_1))
            
    return output_prompts
    


# Examples:

# question = "Which city is the state capital?"
# argset_1 = ["I prefer [X] to [Y]", "I like state capitals."]
# conn_1 = ["because", "however", "although", "but", "as", "since", "for", "though", "nevertheless", "even though"]
# directions_1 = ["left", "right", "right", "right", "left", "left", "left", "right", "right", "right"]
# nonces = ("wugsland", "daxville", "wugsburg", "daxtown", "wug","dax","xyz","abc","X","Y")

# stimulus = make_stimuli(args=argset_1,
#                           question=question,
#                           connectives=conn_1,
#                           directions=directions_1,
#                           nonces=nonces,
#                           template_nonces=["[X]", "[Y]"],)

# for conn in stimulus.keys():
#     for prompt, question, direction, nonce_1, nonce_2 in stimulus[conn]:
#         print(prompt, "\tQ: ", question, "\t", direction, "\t", nonce_1, "\t", nonce_2)
#     print("#-----------------------------------------------------------#")
