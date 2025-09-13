library(tidyverse)

results <- read_csv("data/results/nonce/Qwen_QwQ-32B_reason.csv") %>%
  mutate(
    # answer = case_when(
    #   str_detect(answer, "Yes") ~ "Yes",
    #   str_detect(answer, "No") ~ "No",
    # )
    answer = str_extract(answer, "(?<=\\{)(.*)(?=\\})")
  )

stimuli <- read_csv("data/stimuli-nonce/prompts.csv")


bind_cols(
  stimuli,
  results %>% select(-idx)
) %>%
  filter(stimuli_type == "temporal") %>%
  filter(answer != label) %>% View()

bind_cols(
  stimuli,
  results %>% select(-idx)
) %>% 
  group_by(stimuli_type, connective, prompt_template) %>%
  summarize(
    accuracy = mean(answer == label)
  ) %>% 
  ungroup() %>%
  group_by(connective, stimuli_type) %>%
  summarize(
    n = n(),
    sd = sd(accuracy),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  ungroup() %>%
  filter(stimuli_type == "preference") %>%
  mutate(
    connective = factor(connective),
    connective = fct_reorder(connective, mean)
  ) %>%
  ggplot(aes(connective, mean)) +
  geom_point() +
  facet_wrap(~stimuli_type, scales="free") +
  theme_bw(base_size = 16) +
  theme(
    legend.position = "top",
    panel.grid = element_blank(),
    axis.text = element_text(color = "black"),
    axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1)
  )
