# declare -a models=(allenai/OLMo-2-1124-13B-Instruct Qwen/Qwen2.5-14B-Instruct)
declare -a models=(Qwen/Qwen2.5-14B-Instruct)

for model in "${models[@]}"; do
    CUDA_VISIBLE_DEVICES=0,2 python src/eval.py --instruct --model $model --eval_path data/stimuli-nonce/pref_prompts.csv --out_prefix pref_ --device auto
done

declare -a models=(allenai/OLMo-2-1124-13B Qwen/Qwen2.5-14B)

for model in "${models[@]}"; do
    CUDA_VISIBLE_DEVICES=0,2 python src/eval.py --model $model --eval_path data/stimuli-nonce/pref_prompts.csv --out_prefix pref_ --device auto
done