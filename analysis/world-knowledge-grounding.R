library(tidyverse)
library(ggrepel)
library(lmerTest)
library(emmeans)

model_meta <- tribble(
  ~model, ~short, ~class, ~instruct, ~params,
  "meta-llama_Meta-Llama-3.1-8B", "L-3.1-8B", "Llama-3.1-8B", FALSE, 8000000000,
  "meta-llama_Meta-Llama-3.1-8B-Instruct", "L-3.1-8B-I", "Llama-3.1-8B", TRUE, 8000000000,
  "Qwen_Qwen2.5-0.5B", "Q-2.5-500M", "Qwen2.5", FALSE, 500000000,
  "Qwen_Qwen2.5-0.5B-Instruct", "Q-2.5-500M-I", "Qwen2.5", TRUE, 500000000,
  "Qwen_Qwen2.5-1.5B", "Q-2.5-1.5B", "Qwen2.5", FALSE, 1500000000,
  "Qwen_Qwen2.5-1.5B-Instruct", "Q-2.5-1.5B-I", "Qwen2.5", TRUE, 1500000000,
  "Qwen_Qwen2.5-3B", "Q-2.5-3B", "Qwen2.5", FALSE, 3000000000,
  "Qwen_Qwen2.5-3B-Instruct", "Q-2.5-3B-I", "Qwen2.5", TRUE, 3000000000,
  "Qwen_Qwen2.5-7B", "Q-2.5-7B", "Qwen2.5", FALSE, 7000000000,
  "Qwen_Qwen2.5-7B-Instruct", "Q-2.5-7B-I", "Qwen2.5", TRUE, 7000000000,
  "Qwen_Qwen2.5-14B-Instruct", "Q-2.5-14B-I", "Qwen2.5", TRUE, 14000000000,
  "Qwen_Qwen2.5-14B", "Q-2.5-14B", "Qwen2.5", FALSE, 14000000000,
  "lrm", "Q-2.5-14B-DS", "Qwen2.5-DS", FALSE, 14000000000,
  "allenai_OLMo-2-0425-1B-Instruct", "O-2-1B-I", "OLMo-2", TRUE, 1000000000,
  "allenai_OLMo-2-0425-1B", "O-2-1B", "OLMo-2", FALSE, 1000000000,
  "allenai_OLMo-2-1124-7B-Instruct", "O-2-7B-I", "OLMo-2", TRUE, 7000000000,
  "allenai_OLMo-2-1124-7B", "O-2-7B", "OLMo-2", FALSE, 7000000000,
  "allenai_OLMo-2-1124-13B-Instruct", "O-2-13B-I", "OLMo-2", TRUE, 13000000000,
  "allenai_OLMo-2-1124-13B", "O-2-13B", "OLMo-2", FALSE, 13000000000,
) %>%
  mutate(
    short = factor(short, levels = c("L-3.1-8B", "L-3.1-8B-I", "Q-2.5-500M", "Q-2.5-500M-I", 
                                     "Q-2.5-1.5B", "Q-2.5-1.5B-I", "Q-2.5-3B", "Q-2.5-3B-I", 
                                     "Q-2.5-7B", "Q-2.5-7B-I", "Q-2.5-14B", "Q-2.5-14B-I",
                                     "O-2-1B", "O-2-1B-I", "O-2-7B", "O-2-7B-I", "O-2-13B", "O-2-13B-I", "Q-2.5-14B-DS")),
    class = factor(class, levels = c("Llama-3.1-8B", "Qwen2.5", "Qwen2.5-DS", "OLMo-2"))
  ) %>%
  mutate(
    training_mode = case_when(
      model == "lrm" ~ "reasoning",
      instruct == FALSE ~ "base",
      instruct == TRUE ~ "instruct"
    )
  )

senses <- read_csv("data/stimuli-nonce/senses.csv")

stimuli <- read_csv("data/stimuli-nonce/grounded_prompts.csv") %>%
  mutate(
    unique_item = row_number()
  ) %>%
  inner_join(senses) %>%
  mutate(
    sense = case_when(
      connective == "even before" ~ "Temporal.Asynchronous.Precedence",
      TRUE ~ sense
    )
  )

chance_performance <- stimuli %>%
  filter(prompt_template == "prompt_1") %>%
  mutate(
    prediction = case_when(
      stimuli_type %in% c("preference", "instantiation") ~ "Yes",
      TRUE ~ entity1
    )
  ) %>%
  group_by(stimuli_type) %>%
  summarize(
    chance_accuracy = mean(prediction == label)
  )


results <- fs::dir_ls("data/results/all/", regexp = "*.csv", recurse = TRUE) %>%
  keep(str_detect(., "grounded")) %>%
  map_df(read_csv, .id = "model") %>%
  mutate(
    model = str_remove(model, "data/results/all/"),
    model = str_remove(model, ".csv"),
    model = str_remove(model, "grounded_")
  ) %>%
  rename(prediction = label) %>%
  inner_join(stimuli)


results %>% count(model)




