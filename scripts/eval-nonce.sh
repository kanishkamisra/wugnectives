# declare -a models=(meta-llama/Meta-Llama-3-8B-Instruct Qwen/Qwen2.5-0.5B-Instruct Qwen/Qwen2.5-1.5B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-7B-Instruct allenai/OLMo-2-1124-7B-Instruct allenai/OLMo-2-0425-1B-Instruct)
# declare -a models=(allenai/OLMo-2-1124-7B-Instruct allenai/OLMo-2-0425-1B-Instruct)

# for model in "${models[@]}"; do
#     python src/eval.py --instruct --model $model
# done

# declare -a models=(meta-llama/Meta-Llama-3-8B Qwen/Qwen2.5-0.5B Qwen/Qwen2.5-1.5B Qwen/Qwen2.5-3B Qwen/Qwen2.5-7B allenai/OLMo-2-1124-7B allenai/OLMo-2-0425-1B allenai/OLMo-2-1124-13B)
# declare -a models=(allenai/OLMo-2-1124-7B)

# for model in "${models[@]}"; do
#     python src/eval.py --model $model
# done

# declare -a models=(allenai/OLMo-2-1124-13B-Instruct Qwen/Qwen2.5-14B-Instruct)
declare -a models=(Qwen/Qwen2.5-14B-Instruct)

for model in "${models[@]}"; do
    CUDA_VISIBLE_DEVICES=0,1 python src/eval.py --instruct --model $model --device auto
done

# declare -a models=(allenai/OLMo-2-1124-13B Qwen/Qwen2.5-14B)
declare -a models=(Qwen/Qwen2.5-14B)

for model in "${models[@]}"; do
    CUDA_VISIBLE_DEVICES=0,1 python src/eval.py --model $model --device auto
done
