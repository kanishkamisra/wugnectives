declare -a models=(meta-llama/Meta-Llama-3-8B-Instruct Qwen/Qwen2.5-0.5B-Instruct Qwen/Qwen2.5-1.5B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-7B-Instruct allenai/OLMo-2-1124-7B-Instruct allenai/OLMo-2-0425-1B-Instruct)

for model in "${models[@]}"; do
    python src/eval.py --instruct --model $model
done

declare -a models=(meta-llama/Meta-Llama-3-8B Qwen/Qwen2.5-0.5B Qwen/Qwen2.5-1.5B Qwen/Qwen2.5-3B Qwen/Qwen2.5-7B allenai/OLMo-2-1124-7B allenai/OLMo-2-0425-1B)

for model in "${models[@]}"; do
    python src/eval.py --model $model
done
