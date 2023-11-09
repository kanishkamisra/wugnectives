import sys
import argparse

parser = argparse.ArgumentParser(description="Generate questions with nonces.")
parser.add_argument("sentences")
parser.add_argument("nonces")
parser.add_argument("--template_nonces")


args = parser.parse_args()

sentences_txt = open(args.sentences, "r")
nonces_txt = open(args.nonces, "r")

nonces = []
for line in nonces_txt.readlines():
    nonces.append(line.strip())

sentences = []
for line in sentences_txt.readlines():
    sentences.append(line.split(","))

template_nonces = []
if args.template_nonces == None:
    template_nonces = ["wug", "dax", "XYZ","ABC"]
    # question_template_nonces = ("q_wug", "q_dax", "q_XYZ","q_ABC")
else:
    template_nonces_txt = open(args.template_nonces, "r")
    for line in template_nonces_txt.readlines():
        template_nonces.append(line.strip())


class Stimuli:
    def __init__(self, args, question, connectives):
        self.args = args
        self.question = question
        self.connectives = connectives
    
    def make_sentence(self, nonces):
        prompt = []
        nonce_args = []
        nonce_args_r = []
        questions = []
        
        
        # TODO: Refactor with list permutations (itertools.permutations?)
        # But next priority is getting it loaded into the model
        
        i = 0
        questions.append(str(self.question))
        questions.append(str(self.question))
        for index in range(len(nonces)):
            
            # BUG: Crashes if len(template_nonces) < len(nonces)
            questions[0] = questions[0].replace(template_nonces[index], nonces[index])
            questions[1]= questions[1].replace(template_nonces[1 - index], nonces[index])
            
        for arg in self.args:
            arg_r = str(arg)
            for index in range(len(nonces)):
                arg = arg.replace(template_nonces[index], nonces[index])
                arg_r = arg_r.replace(template_nonces[1 - index], nonces[index])

            nonce_args.append(arg)
            nonce_args_r.append(arg_r)

        for conn in self.connectives:
            if conn == "":
                conn = " "
            else:
                conn = " " + conn + " "
            prompt.append(nonce_args[0] +  conn + nonce_args[1])
            prompt.append(nonce_args_r[0] + conn + nonce_args_r[1])
        
        return (prompt, questions)


# Examples:
snowy_winters = Stimuli(["I prefer wug to dax","I hate fluffy creatures."], "Which creature is fluffy?", ["however", "because", ""])
prompt, question = snowy_winters.make_sentence(["A","B"])
print("Prompt:")
print("\t", prompt)
print("Question:")
print("\t", question)

print()
print(nonces)


snowy_winters = Stimuli(["I wuged","I was dax."], "Was I dax before wuging, after wuging, or during wuging?", ["as","then","previously"])
prompt, question = snowy_winters.make_sentence(nonces[0:4])
print("Prompt:")
print("\t", prompt)
print("Question:")
print("\t", question)