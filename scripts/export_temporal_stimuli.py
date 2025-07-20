from generate_prompt_stimuli import main
from collections import namedtuple

Args = namedtuple("args", ["stimuli_dir", "out_dir", "outfile", "category"])
args = Args("data/stimuli-nonce", "data/stimuli-nonce/", "prompts_temporal", "temporal")
main(args)
