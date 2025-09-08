library(tidyverse)

results <- read_csv("~/Downloads/Qwen_QwQ-32B_reason.csv") %>%
  mutate(
    answer = case_when(
      str_detect(answer, "Yes") ~ "Yes",
      str_detect(answer, "No") ~ "No"
    )
  )

stimuli <- read_csv("data/stimuli-nonce/prompts.csv")

stimuli %>%
  inner_join(results) %>%
  group_by(stimuli_type, connective) %>%
  summarize(
    acc = mean(label == answer)
  ) %>%
  ungroup() %>%
  mutate(
    connective = factor(connective),
    connective = fct_reorder(connective, acc)
  ) %>%
  ggplot(aes(connective, acc)) +
  geom_point() +
  theme_bw(base_size = 16) +
  theme(
    legend.position = "top",
    panel.grid = element_blank(),
    axis.text = element_text(color = "black"),
    axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1)
  )
