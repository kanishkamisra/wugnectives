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
            if direction == "right": 
                output_prompts[conn].append((new_prompt, new_question, nonce_2))
            else:
                output_prompts[conn].append((new_prompt, new_question, nonce_1))
            
    return output_prompts
    


# Examples:

# stimulus = make_stimuli(args=["I [wug]ed","I was [dax]."], 
#                         question="Was I [dax] before [wug]ing, after [wug]ing, or during [wug]ing?", 
#                         connectives=["as","then","previously"],
#                         nonces=["X","Y","Z"],
#                         template_nonces=["[wug]","[dax]"])


# for conn in stimulus.keys():
#     for prompt, question in stimulus[conn]:
#         print(prompt, "\tQ: ", question)
#     print("#-----------------------------------------------------------#")

# print()

# stimulus = make_stimuli(args=["I prefer [wug] to [dax]","I hate the snowy winters."], 
#                         question="Which has the snowy winters?", 
#                         connectives=["because", "however"],
#                         nonces=["X","Y","Z","A","B","C"],
#                         template_nonces=["[wug]","[dax]"])

# for conn in stimulus.keys():
#     for prompt, question in stimulus[conn]:
#         print(prompt, "\tQ: ", question)
#     print("#-----------------------------------------------------------#")



