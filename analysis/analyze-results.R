library(tidyverse)
library(patchwork)

model_meta <- tribble(
  ~model, ~short, ~class, ~instruct, ~params,
  "meta-llama_Meta-Llama-3-8B", "L-3-8B", "Llama-3-8B", FALSE, 8000000000,
  "meta-llama_Meta-Llama-3-8B-Instruct", "L-3-8B-I", "Llama-3-8B", TRUE, 8000000000,
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
  "allenai_OLMo-2-0425-1B-Instruct", "O-2-1B-I", "OLMo-2", TRUE, 1000000000,
  "allenai_OLMo-2-0425-1B", "O-2-1B", "OLMo-2", FALSE, 1000000000,
  "allenai_OLMo-2-1124-7B-Instruct", "O-2-7B-I", "OLMo-2", TRUE, 7000000000,
  "allenai_OLMo-2-1124-7B", "O-2-7B", "OLMo-2", FALSE, 7000000000,
  "allenai_OLMo-2-1124-13B-Instruct", "O-2-13B-I", "OLMo-2", TRUE, 13000000000,
  "allenai_OLMo-2-1124-13B", "O-2-13B", "OLMo-2", FALSE, 13000000000,
) %>%
  mutate(
    short = factor(short, levels = c("L-3-8B", "L-3-8B-I", "Q-2.5-500M", "Q-2.5-500M-I", 
                                     "Q-2.5-1.5B", "Q-2.5-1.5B-I", "Q-2.5-3B", "Q-2.5-3B-I", 
                                     "Q-2.5-7B", "Q-2.5-7B-I", "Q-2.5-14B", "Q-2.5-14B-I",
                                     "O-2-1B", "O-2-1B-I", "O-2-7B", "O-2-7B-I", "O-2-13B", "O-2-13B-I")),
    class = factor(class, levels = c("Llama-3-8B", "Qwen2.5", "OLMo-2"))
  )

classification <- read_csv("~/Downloads/Connectives Project Unique Template - cleaner.csv")

classification %>% count(connective, stimuli_type, `PDTB Category`)

stimuli <- read_csv("data/stimuli-nonce/prompts.csv")

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

dolma_freqs <- read_csv("data/connective-freqs-dolma.csv") %>%
  mutate(
    logfreq = log10(frequency)
  )

dolma_freqs %>%
  full_join(stimuli %>%
              distinct(connective) %>% mutate(selected = TRUE)) %>%
  View()

results <- fs::dir_ls("data/results/nonce/", regexp = "*.csv", recurse = TRUE) %>%
  map_df(read_csv, .id = "model") %>%
  mutate(
    model = str_remove(model, "data/results/nonce/"),
    model = str_remove(model, ".csv")
  ) %>%
  rename(prediction = label) %>%
  inner_join(stimuli)

results %>% count(model) %>%
  inner_join(model_meta)

results %>%
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
  filter(stimuli_type=="preference") %>%
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

plot_connective_wise <- function(st = "preference") {
  if(st == "preference"){
    chance_perf = 0.5
  }
  else{
    chance_perf = 0.5
  }
  connective_wise %>%
    filter(stimuli_type==st) %>%
    group_by(stimuli_type) %>%
    mutate(
      connective = factor(connective),
      connective = fct_reorder(connective, mean),
      params = params/1e9,
      size = case_when(
        params < 1 ~ "< 1B",
        params >= 1 & params < 5 ~ "1B-5B",
        params >= 5 & params < 10 ~ "5B-10B",
        params >= 10 ~ "> 10B"
      ),
      size = factor(size, c("< 1B", "1B-5B", "5B-10B", "> 10B"))
    ) %>%
    ungroup() %>%
    ggplot(aes(connective, mean, size = size, color = class, shape = instruct)) +
    # geom_jitter(height = 0.01, width =0.15, alpha = 0.6)+
    geom_point() +
    # geom_line(aes(group = model), linewidth = 0.75) +
    facet_wrap(~stimuli_type, scales = "free_x", ncol=1) +
    scale_size_manual(values = c(1.5,2,3,4)) +
    geom_hline(yintercept = chance_perf, linetype = "dashed") +
    scale_y_continuous(limits = c(-0.02,1.02), labels = scales::percent_format()) +
    # scale_x_log10(limits = c(0.5, 8), breaks = c(0.5,1,2,4,6,8), labels = c("1/2", "1", "2", "4", "6", "8")) +
    scale_color_brewer(palette = "Dark2", aesthetics = c("color", "fill")) +
    theme_bw(base_size = 15) +
    theme(
      legend.position = "top",
      panel.grid = element_blank(),
      axis.text = element_text(color = "black"),
      axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1)
    )
}


set.seed(1024)
pref_plot = plot_connective_wise("preference")
inst_plot = plot_connective_wise("instantiation")
temp_plot = plot_connective_wise("temporal")

((pref_plot + inst_plot) / temp_plot) + plot_layout(guides = "collect") & theme(legend.position="top")


# temporal deep dive

connective_wise %>%
  filter(stimuli_type=="temporal", class == "Qwen2.5") %>%
  group_by(stimuli_type) %>%
  mutate(
    connective = factor(connective),
    connective = fct_reorder(connective, mean),
    params = params/1e9,
    size = case_when(
      params < 1 ~ "< 1B",
      params >= 1 & params < 5 ~ "1B-5B",
      params >= 5 & params < 10 ~ "5B-10B",
      params >= 10 ~ "> 10B"
    ),
    size = factor(size, c("< 1B", "1B-5B", "5B-10B", "> 10B"))
  ) %>%
  ungroup() %>%
  ggplot(aes(connective, mean, size = size, color = class, shape = instruct)) +
  # geom_jitter(height = 0.01, width =0.15, alpha = 0.6)+
  geom_point() +
  geom_line(aes(group = model), linewidth = 0.75) +
  # facet_wrap(~class, scales = "free_x") +
  facet_wrap(~size) +
  scale_size_manual(values = c(1.5,2,3,4)) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  scale_y_continuous(limits = c(-0.02,1.02), labels = scales::percent_format()) +
  # scale_x_log10(limits = c(0.5, 8), breaks = c(0.5,1,2,4,6,8), labels = c("1/2", "1", "2", "4", "6", "8")) +
  scale_color_brewer(palette = "Dark2", aesthetics = c("color", "fill")) +
  theme_bw(base_size = 15) +
  theme(
    legend.position = "top",
    panel.grid = element_blank(),
    axis.text = element_text(color = "black"),
    axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1)
  )

connective_wise %>%
  ggplot(aes(params/1e9, mean, color = class, fill = class, shape = instruct, linetype = instruct)) +
  # geom_point(size = 2) +
  geom_jitter(size=2) +
  # geom_line() +
  facet_grid(instruct~stimuli_type) +
  # geom_linerange(aes(ymin = mean-cb, ymax = mean+cb), linetype = "solid", linewidth = 0.3) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  scale_y_continuous(labels = scales::percent_format()) +
  # scale_x_log10(limits = c(0.5, 8), breaks = c(0.5,1,2,4,6,8), labels = c("1/2", "1", "2", "4", "6", "8")) +
  scale_color_brewer(palette = "Dark2", aesthetics = c("color", "fill")) +
  theme_bw(base_size = 16) +
  theme(
    axis.text = element_text(color = "black")
  ) +
  labs(
    x = "Parameters (in billion)",
    y = "Accuracy"
  )



results %>%
  filter(connective == "even before", stimuli_type == "temporal", str_detect(model, "Llama-3-8B-Instruct")) %>%
  select(idx, prediction, prob, label, target, entity1, entity2, prompt) %>%
  View()

# no relation to frequency
connective_wise %>%
  filter(str_detect(model, "OLMo-2")) %>%
  inner_join(model_meta) %>%
  inner_join(dolma_freqs) %>%
  ggplot(aes(logfreq, mean)) +
  geom_point() +
  facet_grid(short ~ stimuli_type)

instruct_base <- connective_wise %>%
  mutate(
    instruct = case_when(
      instruct == TRUE ~ "instruct",
      TRUE ~ "base"
    )
  ) %>%
  select(-n, -sd, -cb, -short, -model) %>%
  pivot_wider(names_from = instruct, values_from = mean) %>%
  mutate(
    diff = instruct-base
  )

instruct_base %>%
  inner_join(chance_performance) %>%
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

# demo plot

ggplot() +
  geom_abline(slope = 1, linetype = "dashed", linewidth = 0.2) +
  geom_hline(yintercept = 0.5, linetype = "dotted", linewidth = 0.5) +
  geom_vline(xintercept = 0.5, linetype = "dotted", linewidth = 0.5) +
  scale_x_continuous(limits = c(0,1), labels = scales::percent_format()) +
  scale_y_continuous(limits = c(0,1), labels = scales::percent_format()) +
  theme_bw(base_size = 16) + 
  theme(
    panel.grid = element_blank(),
    axis.text = element_blank(),
    panel.background = element_rect(fill='transparent'), #transparent panel bg
    plot.background = element_rect(fill='transparent', color=NA), #transparent plot bg
    panel.grid.major = element_blank(), #remove major gridlines
    panel.grid.minor = element_blank(), #remove minor gridlines
    legend.background = element_rect(fill='transparent'), #transparent legend bg
    legend.box.background = element_rect(fill='transparent') #transparent legend panel
  )

ggsave("plots/legendplot.pdf", height=2, width=2, dpi=300, device=cairo_pdf)
ggsave("plots/legendplot.svg", height=2, width=2, dpi=300)
  