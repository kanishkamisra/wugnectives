library(tidyverse)

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
  "lrm", "Q-2.5-14B-LRM", "Qwen2.5-LRM", FALSE, 14000000000,
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
                                     "O-2-1B", "O-2-1B-I", "O-2-7B", "O-2-7B-I", "O-2-13B", "O-2-13B-I", "Q-2.5-14B-LRM")),
    class = factor(class, levels = c("Llama-3.1-8B", "Qwen2.5", "Qwen2.5-LRM", "OLMo-2"))
  ) %>%
  mutate(
    training_mode = case_when(
      model == "lrm" ~ "LRM",
      instruct == FALSE ~ "base",
      instruct == TRUE ~ "instruct"
    )
  )

senses <- read_csv("data/stimuli-nonce/senses.csv")

stimuli <- read_csv("data/stimuli-nonce/all_prompts.csv") %>%
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
stimuli_old <- read_csv("data/stimuli-nonce/prompts.csv")

temporal_positions <- read_csv("data/stimuli-nonce/temporal-position-annotations.csv")

chance_performance <- stimuli %>%
  filter(prompt_template == "prompt_1") %>%
  mutate(
    prediction = case_when(
      stimuli_type %in% c("preference", "instantiation") ~ "Yes",
      TRUE ~ entity1
    )
  ) %>%
  group_by(stimuli_type, entailed) %>%
  summarize(
    chance_accuracy = mean(prediction == label)
  )

results <- fs::dir_ls("data/results/all/", regexp = "*.csv", recurse = TRUE) %>%
  map_df(read_csv, .id = "model") %>%
  mutate(
    model = str_remove(model, "data/results/all/"),
    model = str_remove(model, ".csv")
  ) %>%
  rename(prediction = label) %>%
  inner_join(stimuli) %>%
  filter(entailed == TRUE)

results %>% count(model)

results %>%
  filter(entailed == TRUE) %>%
  group_by(model, stimuli_type, prompt_template) %>%
  summarize(
    accuracy = mean(prediction == label)
  ) %>% 
  ungroup() %>%
  group_by(model, stimuli_type) %>%
  summarize(
    n = n(),
    sd = sd(accuracy),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  inner_join(model_meta) %>%
  ggplot(aes(params/1e9, mean, color = class, fill = class, shape = instruct, linetype = instruct)) +
  geom_point(size = 2.5) +
  geom_line() +
  facet_wrap(~stimuli_type) +
  geom_linerange(aes(ymin = mean-cb, ymax = mean+cb), linetype = "solid", linewidth = 0.3) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  scale_y_continuous(limits = c(0,1), labels = scales::percent_format()) +
  scale_x_log10(limits = c(0.5, 16), breaks = c(0.5,1,2,4,6,8,16), labels = c("1/2", "1", "2", "4", "6", "8", "16")) +
  scale_color_brewer(palette = "Dark2", aesthetics = c("color", "fill")) +
  theme_bw(base_size = 16) +
  theme(
    axis.text = element_text(color = "black")
  ) +
  labs(
    x = "Parameters (in billion)",
    y = "Accuracy"
  )

connective_wise <- results %>%
  group_by(model, stimuli_type, connective, prompt_template) %>%
  summarize(
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  group_by(model, stimuli_type, connective) %>%
  filter(accuracy == max(accuracy)) %>%
  summarize(
    # n = n(),
    # sd = sd(accuracy),
    # cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  inner_join(model_meta) %>%
  ungroup()

connective_wise %>%
  filter(stimuli_type=="instantiation") %>%
  group_by(stimuli_type) %>%
  mutate(
    connective = factor(connective),
    connective = fct_reorder(connective, mean),
    params = params/1e9,
    params = factor(params)
  ) %>%
  ungroup() %>%
  ggplot(aes(connective, mean,color = class, shape = instruct)) +
  geom_jitter(height = 0.01, width =0.15, alpha = 0.6)+
  facet_wrap(~stimuli_type, scales = "free_x", ncol=1) +
  # scale_size_manual(values = c(1, 1.5, 2, 2.5, 3)) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  scale_y_continuous(labels = scales::percent_format()) +
  # scale_x_log10(limits = c(0.5, 8), breaks = c(0.5,1,2,4,6,8), labels = c("1/2", "1", "2", "4", "6", "8")) +
  scale_color_brewer(palette = "Dark2", aesthetics = c("color", "fill")) +
  theme_bw(base_size = 15) +
  theme(
    legend.position = "top",
    panel.grid = element_blank(),
    axis.text = element_text(color = "black"),
    axis.text.x = element_text(angle = 90, vjust = 0.5)
  )

instruct_base <- connective_wise %>%
  mutate(
    instruct = case_when(
      instruct == TRUE ~ "instruct",
      TRUE ~ "base"
    )
  ) %>%
  select(-short, -model) %>%
  pivot_wider(names_from = instruct, values_from = mean) %>%
  mutate(
    diff = instruct-base
  )

instruct_base %>%
  inner_join(chance_performance %>% filter(entailed == TRUE)) %>%
  mutate(
    params = params/1e9,
    size = case_when(
      params < 1 ~ "< 1B",
      params >= 1 & params < 5 ~ "1B-5B",
      params >= 5 & params < 10 ~ "5B-10B",
      params >= 10 ~ "> 10B"
    ),
    size = factor(size, c("< 1B", "1B-5B", "5B-10B", "> 10B"))
  ) %>%
  filter(!str_detect(class, "LRM")) %>%
  ggplot(aes(base, instruct, color = class, shape = class, size = size)) +
  geom_point(alpha = 0.7) +
  geom_abline(slope = 1, linetype = "dashed", linewidth = 0.2) +
  geom_hline(aes(yintercept = chance_accuracy), linetype = "dotted", linewidth = 0.5) +
  geom_vline(aes(xintercept = chance_accuracy), linetype = "dotted", linewidth = 0.5) +
  scale_color_brewer(palette = "Dark2") +
  scale_size_manual(values = c(1.5,2,3,4)) +
  scale_x_continuous(labels = scales::percent_format()) +
  scale_y_continuous(labels = scales::percent_format()) +
  # facet_wrap(~ stimuli_type) +
  facet_grid(class ~ stimuli_type) +
  theme_bw(base_size = 16) + 
  theme(
    panel.grid = element_blank(),
    # legend.position = "top"
  )


#-----

sense_wise <- results %>%
  inner_join(senses) %>%
  group_by(model, stimuli_type, sense, prompt_template) %>%
  summarize(
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  group_by(model, stimuli_type, sense) %>%
  # filter(accuracy == max(accuracy)) %>%
  summarize(
    n = n(),
    sd = sd(accuracy),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  inner_join(model_meta) %>%
  ungroup()

sense_wise %>%
  group_by(stimuli_type) %>%
  mutate(
    connective = factor(sense),
    params = params/1e9,
  ) %>%
  ungroup() %>%
  mutate(
    connective = case_when(
      connective == "Comparison.Concession.Arg1-as-denier" ~ "Comparison\nConcession (Arg1)",
      connective == "Comparison.Concession.Arg2-as-denier" ~ "Comparison\nConcession (Arg2)",
      connective == "Contingency.Cause.Reason" ~ "Contingency\nCause (Reason)",
      connective == "Contingency.Cause.Result" ~ "Contingency\nCause (Result)",
      connective == "Expansion.Instantiation.Arg2-as-instance" ~ "Instantiation",
      connective == "Temporal.Asynchronous.Precedence" ~ "Temporal\n(Precedence)",
      connective == "Temporal.Asynchronous.Succession" ~ "Temporal\n(Succession)",
      TRUE ~ connective
    ),
    connective = factor(
      connective, 
      levels = c("Instantiation", "Comparison\nConcession (Arg1)", "Comparison\nConcession (Arg2)", 
                 "Contingency\nCause (Reason)", "Contingency\nCause (Result)", "Temporal\n(Precedence)", 
                 "Temporal\n(Succession)")
    )
  ) %>%
  ggplot(aes(params, mean, color = class, fill = class, shape = training_mode, linetype = training_mode)) +
  geom_point(size = 2) +
  # geom_linerange(aes(ymin = mean-cb, ymax = mean+cb), linetype = "solid") +
  geom_line(linewidth = 0.6) +
  facet_wrap(~connective, scales = "free_x", nrow=1) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  scale_y_continuous(labels = scales::percent_format(), limits = c(0, 1.02)) +
  scale_x_log10(limits = c(0.5, 16), breaks = c(0.5,1,2,4,8,16), labels = c("1/2", "1", "2", "4", "8", "16")) +
  # scale_color_brewer(palette = "Dark2", aesthetics = c("color", "fill")) +
  scale_color_manual(aesthetics = c("color", "fill"), values = c("#1f78b4", "#e6ab02", "#66a61e", "#e7298a")) +
  theme_bw(base_size = 16, base_family = "Times") +
  theme(
    legend.position = "top",
    # panel.grid = element_blank(),
    axis.text = element_text(color = "black")
  ) +
  labs(
    x = "Parameters (in Billion)",
    y = "Accuracy (95% CI)",
    color = "Model Family",
    fill = "Model Family",
    shape = "Training Type",
    linetype = "Training Type"
  )

ggsave("plots/param-overall.pdf", height = 3.9, width = 12.40, dpi = 300, device = cairo_pdf)


results %>%
  group_by(model, stimuli_type, connective, sense, prompt_template) %>%
  summarize(
    n = n(),
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  group_by(model, stimuli_type, sense, connective) %>%
  # filter(accuracy == max(accuracy)) %>%
  summarize(
    n = n(),
    sd = sd(accuracy),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  inner_join(model_meta) %>%
  ungroup() %>%
  filter(stimuli_type == "instantiation") %>%
  mutate(
    sense = factor(sense),
    params = params/1e9,
  ) %>%
  ggplot(aes(connective, mean, color = class, fill = class, shape = training_mode, linetype = training_mode)) +
  geom_point(size = 2, position = position_jitter(width = 0.15, seed =1024)) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  scale_y_continuous(labels = scales::percent_format(), limits = c(0, 1.02)) +
  scale_color_manual(aesthetics = c("color", "fill"), values = c("#1f78b4", "#e6ab02", "#66a61e", "#e7298a")) +
  theme_bw(base_size = 16, base_family = "Times") +
  theme(
    # legend.position = "top",
    panel.grid = element_blank(),
    axis.text = element_text(color = "black"),
    axis.text.x = element_text(angle = 30, vjust =0.7, hjust = 0.5)
  ) +
  labs(
    x = "Connective",
    y = "Accuracy",
    color = "Model Family",
    fill = "Model Family",
    shape = "Training Type",
    linetype = "Training Type"
  )

ggsave("plots/instantiation-breakdown.pdf", height = 3.87, width = 5.75, dpi = 300, device=cairo_pdf)


results %>%
  inner_join(senses) %>%
  group_by(model, stimuli_type, connective, sense, prompt_template) %>%
  summarize(
    n = n(),
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  group_by(model, stimuli_type, sense, connective) %>%
  # filter(accuracy == max(accuracy)) %>%
  summarize(
    n = n(),
    sd = sd(accuracy),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  inner_join(model_meta) %>%
  ungroup() %>%
  filter(stimuli_type == "preference") %>%
  mutate(
    sense = case_when(
      sense == "Comparison.Concession.Arg1-as-denier" ~ "Comparison\nConcession (Arg1)",
      sense == "Comparison.Concession.Arg2-as-denier" ~ "Comparison\nConcession (Arg2)",
      sense == "Contingency.Cause.Reason" ~ "Contingency\nCause (Reason)",
      sense == "Contingency.Cause.Result" ~ "Contingency\nCause (Result)",
      sense == "Expansion.Instantiation.Arg2-as-instance" ~ "Instantiation",
      sense == "Temporal.Asynchronous.Precedence" ~ "Temporal\n(Precedence)",
      sense == "Temporal.Asynchronous.Succession" ~ "Temporal\n(Succession)",
      TRUE ~ sense
    ),
    sense = factor(
      sense, 
      levels = c("Instantiation", "Comparison\nConcession (Arg1)", "Comparison\nConcession (Arg2)", 
                 "Contingency\nCause (Reason)", "Contingency\nCause (Result)", "Temporal\n(Precedence)", 
                 "Temporal\n(Succession)")
    )
  ) %>%
  mutate(
    sense = factor(sense),
    params = params/1e9,
  ) %>%
  ggplot(aes(connective, mean, color = class, fill = class, shape = training_mode, linetype = training_mode)) +
  geom_point(size = 2, position = position_jitter(width = 0.15, seed =1024)) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  facet_wrap(~sense, scales="free_x") +
  scale_y_continuous(labels = scales::percent_format(), limits = c(0, 1.02)) +
  scale_color_manual(aesthetics = c("color", "fill"), values = c("#1f78b4", "#e6ab02", "#66a61e", "#e7298a")) +
  theme_bw(base_size = 16, base_family = "Times") +
  theme(
    # legend.position = "top",
    panel.grid = element_blank(),
    axis.text = element_text(color = "black"),
    axis.text.x = element_text(angle = 30, vjust =0.7, hjust = 0.5)
  ) +
  labs(
    x = "Connective",
    y = "Accuracy",
    color = "Model Family",
    fill = "Model Family",
    shape = "Training Type",
    linetype = "Training Type"
  )

ggsave("plots/preference-breakdown.pdf", height = 7.13, width = 8.85, dpi = 300, device = cairo_pdf)


# temporal <- results %>%
#   inner_join(senses) %>% 
#   filter(stimuli_type == "temporal") %>%
#   mutate(
#     entity = case_when(
#       label == entity1 ~ "1",
#       label == entity2 ~ "2"
#     )
#   )

temporal <- results %>%
  inner_join(senses) %>% 
  filter(stimuli_type == "temporal") %>%
  inner_join(temporal_positions) %>%
  filter(model == "lrm") %>%
  select(-model)

results %>%
  inner_join(senses) %>% 
  filter(stimuli_type == "temporal") %>%
  inner_join(temporal_positions) %>%
  mutate(
    choose_first = prediction == first
  ) %>%
  group_by(model, connective, prompt_template) %>%
  summarize(
    choose_first = mean(choose_first)
  ) %>%
  ungroup() %>%
  group_by(model) %>%
  summarize(
    n = n(),
    sd = sd(choose_first),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    choose_first = mean(choose_first)
  ) %>%
  ungroup() %>%
  inner_join(model_meta) %>%
  ggplot(aes(params/1e9, choose_first,  color = class, fill = class, shape = training_mode)) +
  geom_point(size = 3) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  scale_y_continuous(limits = c(0, 1))


temporal %>%
  count(entity2 == first)

temporal %>%
  mutate(prediction = entity2, model = "ccf") %>%
  mutate(
    choose_first = prediction == first
  ) %>%
  group_by(model, connective, prompt_template) %>%
  summarize(
    choose_first = mean(choose_first)
  ) %>%
  ungroup() %>%
  group_by(model) %>%
  summarize(
    n = n(),
    sd = sd(choose_first),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    choose_first = mean(choose_first)
  )



heuristics <- bind_rows(
  temporal %>% 
    mutate(prediction = first, model = "Choose First"),
  temporal %>%
    mutate(prediction = second, model = "Choose Recent")
)

heuristic_result <- heuristics %>%
  group_by(model, sense) %>%
  summarize(
    acc = mean(prediction == label)
  ) %>%
  select(heuristic = model, sense, mean = acc) %>%
  mutate(
    connective = case_when(
      sense == "Comparison.Concession.Arg1-as-denier" ~ "Comparison\nConcession (Arg1)",
      sense == "Comparison.Concession.Arg2-as-denier" ~ "Comparison\nConcession (Arg2)",
      sense == "Contingency.Cause.Reason" ~ "Contingency\nCause (Reason)",
      sense == "Contingency.Cause.Result" ~ "Contingency\nCause (Result)",
      sense == "Expansion.Instantiation.Arg2-as-instance" ~ "Instantiation",
      sense == "Temporal.Asynchronous.Precedence" ~ "Temporal\n(Precedence)",
      sense == "Temporal.Asynchronous.Succession" ~ "Temporal\n(Succession)",
      TRUE ~ sense
    ),
    connective = factor(
      connective, 
      levels = c("Instantiation", "Comparison\nConcession (Arg1)", "Comparison\nConcession (Arg2)", 
                 "Contingency\nCause (Reason)", "Contingency\nCause (Result)", "Temporal\n(Precedence)", 
                 "Temporal\n(Succession)")
    )
  ) %>%
  filter(connective %in% c("Temporal\n(Precedence)", 
                           "Temporal\n(Succession)"))
  

sense_wise %>%
  group_by(stimuli_type) %>%
  mutate(
    connective = factor(sense),
    params = params/1e9,
  ) %>%
  ungroup() %>%
  mutate(
    connective = case_when(
      connective == "Comparison.Concession.Arg1-as-denier" ~ "Comparison\nConcession (Arg1)",
      connective == "Comparison.Concession.Arg2-as-denier" ~ "Comparison\nConcession (Arg2)",
      connective == "Contingency.Cause.Reason" ~ "Contingency\nCause (Reason)",
      connective == "Contingency.Cause.Result" ~ "Contingency\nCause (Result)",
      connective == "Expansion.Instantiation.Arg2-as-instance" ~ "Instantiation",
      connective == "Temporal.Asynchronous.Precedence" ~ "Temporal\n(Precedence)",
      connective == "Temporal.Asynchronous.Succession" ~ "Temporal\n(Succession)",
      TRUE ~ connective
    ),
    connective = factor(
      connective, 
      levels = c("Instantiation", "Comparison\nConcession (Arg1)", "Comparison\nConcession (Arg2)", 
                 "Contingency\nCause (Reason)", "Contingency\nCause (Result)", "Temporal\n(Precedence)", 
                 "Temporal\n(Succession)")
    )
  ) %>%
  filter(connective %in% c("Temporal\n(Precedence)", 
                           "Temporal\n(Succession)")) %>%
  ggplot(aes(params, mean, color = class, fill = class, shape = training_mode, linetype = training_mode)) +
  geom_point(size = 2) +
  geom_line(linewidth = 0.6) +
  facet_wrap(~connective, scales = "free_x", nrow=1) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  geom_hline(data = heuristic_result, aes(yintercept = mean), linetype = "dotted") +
  scale_y_continuous(labels = scales::percent_format(), limits = c(0, 1.02)) +
  scale_x_log10(limits = c(0.5, 16), breaks = c(0.5,1,2,4,8,16), labels = c("1/2", "1", "2", "4", "8", "16")) +
  scale_color_manual(aesthetics = c("color", "fill"), values = c("#1f78b4", "#e6ab02", "#66a61e", "#e7298a")) +
  theme_bw(base_size = 16, base_family = "Times") +
  theme(
    # legend.position = "top",
    # panel.grid = element_blank(),
    axis.text = element_text(color = "black")
  ) +
  labs(
    x = "Parameters (in Billion)",
    y = "Accuracy (95% CI)",
    color = "Model Family",
    fill = "Model Family",
    shape = "Training Type",
    linetype = "Training Type"
  )

# temporal %>%
#   filter(str_detect(sense, "Precedence")) %>%
#   mutate(
#     choice = case_when(
#       label == second ~ "second",
#       TRUE ~ "first"
#     )
#   ) %>%
#   count(connective, choice)


thresholds <- heuristics %>%
  # filter(connective == "even though") %>%
  filter(sense == "Temporal.Asynchronous.Succession") %>%
  group_by(model, sense, connective) %>%
  summarize(
    acc = mean(prediction == label)
  ) %>%
  ungroup() %>%
  group_by(sense, connective) %>%
  slice_max(acc, n = 1, with_ties = FALSE) %>%
  ungroup() %>%
  rename(heuristic = model)


results %>%
  inner_join(senses) %>%
  group_by(model, stimuli_type, connective, sense, prompt_template) %>%
  summarize(
    n = n(),
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  group_by(model, stimuli_type, sense, connective) %>%
  # filter(accuracy == max(accuracy)) %>%
  summarize(
    n = n(),
    sd = sd(accuracy),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  ungroup() %>%
  inner_join(thresholds) %>%
  filter(acc != 1) %>%
  mutate(
    above = mean > acc
  ) %>%
  group_by(connective) %>%
  summarize(
    above = mean(above)
  )



results %>%
  inner_join(senses) %>%
  group_by(model, stimuli_type, connective, sense, prompt_template) %>%
  summarize(
    n = n(),
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  group_by(model, stimuli_type, sense, connective) %>%
  # filter(accuracy == max(accuracy)) %>%
  summarize(
    n = n(),
    sd = sd(accuracy),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  inner_join(model_meta) %>%
  ungroup() %>%
  filter(stimuli_type == "temporal") %>%
  mutate(
    sense = case_when(
      sense == "Comparison.Concession.Arg1-as-denier" ~ "Comparison\nConcession (Arg1)",
      sense == "Comparison.Concession.Arg2-as-denier" ~ "Comparison\nConcession (Arg2)",
      sense == "Contingency.Cause.Reason" ~ "Contingency\nCause (Reason)",
      sense == "Contingency.Cause.Result" ~ "Contingency\nCause (Result)",
      sense == "Expansion.Instantiation.Arg2-as-instance" ~ "Instantiation",
      sense == "Temporal.Asynchronous.Precedence" ~ "Temporal\n(Precedence)",
      sense == "Temporal.Asynchronous.Succession" ~ "Temporal\n(Succession)",
      TRUE ~ sense
    ),
    sense = factor(
      sense, 
      levels = c("Instantiation", "Comparison\nConcession (Arg1)", "Comparison\nConcession (Arg2)", 
                 "Contingency\nCause (Reason)", "Contingency\nCause (Result)", "Temporal\n(Precedence)", 
                 "Temporal\n(Succession)")
    )
  ) %>%
  mutate(
    sense = factor(sense),
    params = params/1e9,
    connective = fct_reorder(connective, mean)
  ) %>%
  ggplot(aes(connective, mean, color = class, fill = class, shape = training_mode, linetype = training_mode)) +
  geom_point(size = 2, position = position_jitter(width = 0.15, seed =1024)) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  facet_wrap(~sense, scales="free_x",nrow=2) +
  scale_y_continuous(labels = scales::percent_format(), limits = c(-0.3, 1.05)) +
  scale_color_manual(aesthetics = c("color", "fill"), values = c("#1f78b4", "#e6ab02", "#66a61e", "#e7298a")) +
  theme_bw(base_size = 16, base_family = "Times") +
  theme(
    # legend.position = "top",
    panel.grid = element_blank(),
    axis.text = element_text(color = "black"),
    axis.text.x = element_text(angle = 30, vjust =0.7, hjust = 0.5)
  ) +
  labs(
    x = "Parameters (in Billion)",
    y = "Accuracy",
    color = "Model Family",
    fill = "Model Family",
    shape = "Training Type",
    linetype = "Training Type"
  )

ggsave("plots/temporal-breakdown.pdf", height = 6.99, width = 7.82, dpi = 300, device = cairo_pdf)


stimuli %>%
  inner_join(senses) %>% View()

dolma_freqs <- read_csv("data/connective-freqs-dolma.csv") %>%
  mutate(
    logfreq = log10(frequency)
  )

dolma_freqs %>%
  full_join(stimuli %>%
              distinct(connective) %>% mutate(selected = TRUE)) %>%
  View()

results %>%
  inner_join(senses) %>%
  group_by(model, sense, connective, prompt_template) %>%
  summarize(
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  group_by(model, sense, connective) %>%
  filter(accuracy == max(accuracy)) %>%
  summarize(
    # n = n(),
    # sd = sd(accuracy),
    # cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  inner_join(model_meta) %>%
  ungroup() %>%
  filter(str_detect(model, "OLMo-2")) %>%
  inner_join(model_meta) %>%
  inner_join(dolma_freqs) %>%
  ggplot(aes(logfreq, mean)) +
  geom_point() +
  facet_grid(short ~ sense)
