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

# stimuli %>%
#   filter(entailed == TRUE) %>%
#   count(sense) %>%
#   mutate(n = n/12)
# 
# stimuli_old <- read_csv("data/stimuli-nonce/prompts.csv")

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
  mutate(
    prediction = case_when(
      prediction == "\\\\text{No}" ~ "No",
      prediction == "\\\\text{Yes}" ~ "Yes",
      prediction %in% c("\\\\text{blicketbash}", "b", "bickelbash", "bicketbash", "blicktash") ~ "blicketbash",
      TRUE ~ prediction
    )
  ) %>%
  inner_join(stimuli) %>%
  filter(entailed == TRUE)

results %>% count(model)

# results %>%
#   filter(entailed == TRUE) %>%
#   group_by(model, stimuli_type, prompt_template) %>%
#   summarize(
#     accuracy = mean(prediction == label)
#   ) %>% 
#   ungroup() %>%
#   group_by(model, stimuli_type) %>%
#   summarize(
#     n = n(),
#     sd = sd(accuracy),
#     cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
#     mean = mean(accuracy)
#   ) %>%
#   inner_join(model_meta) %>%
#   ggplot(aes(params/1e9, mean, color = class, fill = class, shape = instruct, linetype = instruct)) +
#   geom_point(size = 2.5) +
#   geom_line() +
#   facet_wrap(~stimuli_type) +
#   geom_linerange(aes(ymin = mean-cb, ymax = mean+cb), linetype = "solid", linewidth = 0.3) +
#   geom_hline(yintercept = 0.5, linetype = "dashed") +
#   scale_y_continuous(limits = c(0,1), labels = scales::percent_format()) +
#   scale_x_log10(limits = c(0.5, 16), breaks = c(0.5,1,2,4,6,8,16), labels = c("1/2", "1", "2", "4", "6", "8", "16")) +
#   scale_color_brewer(palette = "Dark2", aesthetics = c("color", "fill")) +
#   theme_bw(base_size = 16) +
#   theme(
#     axis.text = element_text(color = "black")
#   ) +
#   labs(
#     x = "Parameters (in billion)",
#     y = "Accuracy"
#   )
# 
# connective_wise <- results %>%
#   group_by(model, stimuli_type, connective, prompt_template) %>%
#   summarize(
#     accuracy = mean(prediction == label)
#   ) %>%
#   ungroup() %>%
#   group_by(model, stimuli_type, connective) %>%
#   filter(accuracy == max(accuracy)) %>%
#   summarize(
#     # n = n(),
#     # sd = sd(accuracy),
#     # cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
#     mean = mean(accuracy)
#   ) %>%
#   inner_join(model_meta) %>%
#   ungroup()
# 
# connective_wise %>%
#   filter(stimuli_type=="instantiation") %>%
#   group_by(stimuli_type) %>%
#   mutate(
#     connective = factor(connective),
#     connective = fct_reorder(connective, mean),
#     params = params/1e9,
#     params = factor(params)
#   ) %>%
#   ungroup() %>%
#   ggplot(aes(connective, mean,color = class, shape = instruct)) +
#   geom_jitter(height = 0.01, width =0.15, alpha = 0.6)+
#   facet_wrap(~stimuli_type, scales = "free_x", ncol=1) +
#   # scale_size_manual(values = c(1, 1.5, 2, 2.5, 3)) +
#   geom_hline(yintercept = 0.5, linetype = "dashed") +
#   scale_y_continuous(labels = scales::percent_format()) +
#   # scale_x_log10(limits = c(0.5, 8), breaks = c(0.5,1,2,4,6,8), labels = c("1/2", "1", "2", "4", "6", "8")) +
#   scale_color_brewer(palette = "Dark2", aesthetics = c("color", "fill")) +
#   theme_bw(base_size = 15) +
#   theme(
#     legend.position = "top",
#     panel.grid = element_blank(),
#     axis.text = element_text(color = "black"),
#     axis.text.x = element_text(angle = 90, vjust = 0.5)
#   )
# 
# instruct_base <- connective_wise %>%
#   mutate(
#     instruct = case_when(
#       instruct == TRUE ~ "instruct",
#       TRUE ~ "base"
#     )
#   ) %>%
#   select(-short, -model) %>%
#   pivot_wider(names_from = instruct, values_from = mean) %>%
#   mutate(
#     diff = instruct-base
#   )
# 
# instruct_base %>%
#   inner_join(chance_performance %>% filter(entailed == TRUE)) %>%
#   mutate(
#     params = params/1e9,
#     size = case_when(
#       params < 1 ~ "< 1B",
#       params >= 1 & params < 5 ~ "1B-5B",
#       params >= 5 & params < 10 ~ "5B-10B",
#       params >= 10 ~ "> 10B"
#     ),
#     size = factor(size, c("< 1B", "1B-5B", "5B-10B", "> 10B"))
#   ) %>%
#   filter(!str_detect(class, "LRM")) %>%
#   ggplot(aes(base, instruct, color = class, shape = class, size = size)) +
#   geom_point(alpha = 0.7) +
#   geom_abline(slope = 1, linetype = "dashed", linewidth = 0.2) +
#   geom_hline(aes(yintercept = chance_accuracy), linetype = "dotted", linewidth = 0.5) +
#   geom_vline(aes(xintercept = chance_accuracy), linetype = "dotted", linewidth = 0.5) +
#   scale_color_brewer(palette = "Dark2") +
#   scale_size_manual(values = c(1.5,2,3,4)) +
#   scale_x_continuous(labels = scales::percent_format()) +
#   scale_y_continuous(labels = scales::percent_format()) +
#   # facet_wrap(~ stimuli_type) +
#   facet_grid(class ~ stimuli_type) +
#   theme_bw(base_size = 16) + 
#   theme(
#     panel.grid = element_blank(),
#     # legend.position = "top"
#   )


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
  geom_linerange(aes(ymin = mean-cb, ymax = mean+cb), linetype = "solid") +
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
    panel.grid = element_blank(),
    axis.text = element_text(color = "black")
  ) +
  labs(
    x = "Parameters (in Billion), log-scale",
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
  filter(stimuli_type == "preference", str_detect(sense, "Comparison")) %>%
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
  scale_y_continuous(labels = scales::percent_format(), limits = c(0, 1)) +
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

# ggsave("plots/preference-breakdown.pdf", height = 7.13, width = 8.85, dpi = 300, device = cairo_pdf)
ggsave("plots/comparison-breakdown.pdf", height = 4.04, width = 9.61, dpi = 300, device = cairo_pdf)

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
  filter(stimuli_type == "preference", str_detect(sense, "Contingency")) %>%
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
  scale_y_continuous(labels = scales::percent_format(), limits = c(0, 1)) +
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

# ggsave("plots/preference-breakdown.pdf", height = 7.13, width = 8.85, dpi = 300, device = cairo_pdf)
ggsave("plots/contingency-breakdown.pdf", height = 4.04, width = 9.61, dpi = 300, device = cairo_pdf)


results %>%
  inner_join(senses) %>%
  group_by(model, stimuli_type, sense, target, prompt_template) %>%
  summarize(
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  group_by(model, stimuli_type, sense, target) %>%
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
    connective = factor(sense),
    params = params/1e9,
  ) %>%
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
  # facet_wrap(~connective, scales = "free_x", nrow=1) +
  facet_grid(target ~ connective) +
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


# ratio of no to yes

results %>%
  filter(stimuli_type == "preference") %>%
  mutate(
    correct = prediction == label,
    yes = prediction == "Yes",
    no = prediction == "No"
  ) %>%
  group_by(model, stimuli_type, sense, correct) %>%
  summarize(
    ratio = mean(no)
  ) %>%
  ungroup() %>%
  inner_join(model_meta) %>%
  mutate(
    connective = factor(sense),
    params = params/1e9,
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
    ),
    correct = case_when(
      correct ==TRUE ~ "Correct",
      correct == FALSE ~ "Incorrect"
    )
  ) %>%
  ggplot(aes(correct, ratio, color = class, fill = class, shape = training_mode, linetype = training_mode)) +
  geom_point(size = 2, position = position_jitter(width = 0.2, seed =1024)) +
  facet_wrap(~connective, nrow = 1) +
  scale_y_continuous(labels = scales::percent_format(), limits = c(0, 1.02)) +
  # scale_x_log10(limits = c(0.5, 16), breaks = c(0.5,1,2,4,8,16), labels = c("1/2", "1", "2", "4", "8", "16")) +
  # scale_color_brewer(palette = "Dark2", aesthetics = c("color", "fill")) +
  scale_color_manual(aesthetics = c("color", "fill"), values = c("#1f78b4", "#e6ab02", "#66a61e", "#e7298a")) +
  theme_bw(base_size = 15, base_family = "Times") +
  theme(
    legend.position = "top",
    panel.grid = element_blank(),
    axis.text = element_text(color = "black")
  ) +
  labs(
    x = "Model Prediction",
    y = "Ratio of No to Yes",
    color = "Model Family",
    fill = "Model Family",
    shape = "Training Mode"
  )

ggsave("plots/No-bias-preference.pdf", height = 4.08, width = 10.84, dpi = 300, device = cairo_pdf)

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

# temporal %>% 
#   count(sense)

results %>%
  inner_join(senses) %>% 
  filter(stimuli_type == "temporal") %>% count(sense)


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

# Accuracy on succession for models that beat the baseline

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
    x = "Connective",
    y = "Accuracy",
    color = "Model Family",
    fill = "Model Family",
    shape = "Training Type",
    linetype = "Training Type"
  )

ggsave("plots/temporal-breakdown.pdf", height = 6.99, width = 7.82, dpi = 300, device = cairo_pdf)

# even though vs. rest of succession for top 5 models

# get top 5 models on succession (overall)
best_succ_models <- results %>%
  filter(str_detect(sense, "Succession")) %>% 
  group_by(model) %>%
  summarize(
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  arrange(-accuracy) %>%
  slice(1:5) %>%
  pull(model)

# jitter <- position_jitterdodge(jitter.width = 0.4, dodge.width = 0, seed = 1024)
jitter = NA

results %>%
  filter(str_detect(sense, "Succession")) %>%
  mutate(
    condition = case_when(
      connective == "even though" ~ "Even though",
      TRUE ~ "Rest of Succession"
    ),
    condition = factor(condition, levels = c("Rest of Succession", "Even though"))
  ) %>%
  group_by(model, condition, prompt_template) %>%
  summarize(
    accuracy = mean(label == prediction)
  ) %>%
  ungroup() %>%
  filter(model %in% best_succ_models) %>%
  group_by(model, condition) %>%
  summarize(
    n = n(),
    sd = sd(accuracy),
    cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
    mean = mean(accuracy)
  ) %>%
  ungroup() %>%
  inner_join(model_meta) %>%
  mutate(
    label = case_when(
      condition == "Even though" ~ short,
      TRUE ~ NA_character_
    )
  ) %>%
  ggplot(aes(condition, mean, group = short, color = short, fill = short, shape = short)) +
  geom_point(size = 2) +
  geom_ribbon(aes(ymin = mean-cb, ymax = mean+cb), alpha = 0.2, color = NA) +
  geom_line() +
  # geom_text_repel(
  #   aes(label = short)
  # ) +
  geom_label_repel(aes(label = label), fill = "white", seed = 1024, nudge_x = 0.1) +
  # scale_color_manual(values = c("#e6ab02", "#66a61e"), aesthetics = c("fill", "color")) +
  scale_y_continuous(labels = scales::percent_format()) +
  scale_shape_manual(values = c(21,22,23,24,25)) +
  theme_bw(base_size = 16, base_family = "Times") +
  theme(
    panel.grid = element_blank(),
    legend.position = "",
    axis.text = element_text(color = "black"),
    legend.title = element_blank()
  ) +
  labs(
    x = "Condition",
    y = "Accuracy (95% CI)",
  )

ggsave("plots/eventhough-succession.pdf", height = 3.31, width=4.05, dpi = 300, device=cairo_pdf)


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

# results %>%
#   inner_join(senses) %>%
#   group_by(model, sense, connective) %>%
#   summarize(
#     accuracy = mean(prediction == label)
#   ) %>%
#   ungroup() %>%
#   group_by(model, sense, connective) %>%
#   filter(accuracy == max(accuracy)) %>%
#   summarize(
#     # n = n(),
#     # sd = sd(accuracy),
#     # cb = qt(0.05/2, n-1, lower.tail = FALSE) * sd/sqrt(n),
#     mean = mean(accuracy)
#   ) %>%
#   inner_join(model_meta) %>%
#   ungroup() %>%
#   filter(str_detect(model, "OLMo-2")) %>%
#   inner_join(model_meta) %>%

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
  inner_join(dolma_freqs) %>%
  ggplot(aes(logfreq, mean)) +
  geom_point() +
  facet_grid(short ~ sense)

broken_down <- results %>%
  group_by(model, sense, prompt_template) %>%
  summarize(
    n = n(),
    accuracy = mean(prediction == label)
  ) %>%
  inner_join(model_meta) %>%
  ungroup() %>%
  mutate(
    base = str_replace(short, "-I", ""),
    instruct = as.numeric(instruct),
    instruct = factor(instruct),
    sense = factor(sense),
    params = params/1e9
  )

contrasts(broken_down$sense) <- "contr.sum"

fit.scale <- lmer(accuracy ~ 1 + params * sense + (1 | base) + (1 | prompt_template), data = broken_down %>% filter(model != "lrm"))
anova.scale <- car::Anova(fit.scale, type = 3, test.statistic = "F", ddf = "Satterthwaite")
anova.scale
summary(fit.scale)

fit.instruct <- lmer(accuracy ~ 1 + instruct * sense + (1 | base) + (1 | prompt_template), data = broken_down %>% filter(model != "lrm"))
car::Anova(fit.instruct, type = 3, test.statistic = "F", ddf = "Satterthwaite")

emm <- emmeans(fit.instruct, ~ instruct | sense)
emm

simple_effects <- pairs(emm, by = "sense", adjust = "Tukey")
summary(simple_effects)


qwen14b <- broken_down %>%
  filter(short %in% c("Q-2.5-14B", "Q-2.5-14B-I", "Q-2.5-14B-DS")) %>%
  mutate(
    training_mode = factor(training_mode)
  )

contrasts(qwen14b$training_mode) <- "contr.sum"
contrasts(qwen14b$sense) <- "contr.sum"
  

fit_ds <- lmer(accuracy ~ 1 + training_mode * sense + (1 | prompt_template), data = qwen14b)
emmeans(fit_ds, pairwise ~ training_mode, adjust = "Tukey")


fit_ds.short <- lmer(accuracy ~ 1 + (1 + short | prompt_template), data = qwen14b, REML = FALSE)

anova(fit_ds, fit_ds.short)
summary(fit_ds)

freq <- results %>%
  group_by(model, stimuli_type, connective, sense, prompt_template) %>%
  summarize(
    n = n(),
    accuracy = mean(prediction == label)
  ) %>%
  ungroup() %>%
  inner_join(dolma_freqs) 

fit <- lmer(accuracy ~ logfreq + (1 + logfreq | model) + (1 + logfreq | prompt_template), data=freq)

summary(fit)

results %>%
  group_by(model, connective) %>%
  summarize(
    n = n(),
    accuracy = mean(prediction == label)
  ) %>%
  inner_join(model_meta) %>%
  ungroup() %>%
  inner_join(dolma_freqs) %>%
  group_by(model) %>%
  nest() %>%
  mutate(
    cor = map(data, function(x) {
      cor.test(x$accuracy, x$logfreq) %>%
        broom::tidy()
    })
  ) %>%
  select(-data) %>%
  unnest(cor) %>%
  select(-parameter, -conf.low, -conf.high, -method, -alternative, -statistic) %>%
  mutate(
    model = str_replace(model, "lrm", "Qwen2.5-DS"),
    model = str_remove(model, "(Qwen_|allenai_|meta-llama_Meta-)"),
    model = str_remove(model, "(0425-|1124-)")
  ) %>%
  xtable::xtable()

model_meta %>%
  filter(!str_detect(model, "OLMo-2-1124-13B")) %>%
  select(class, model, params, training_mode) %>%
  mutate(params = params/1e9, model = str_replace(model, "_", "/")) %>%
  arrange(class, params) %>%
  xtable::xtable()

