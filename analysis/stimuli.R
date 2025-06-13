library(tidyverse)

stimuli_raw <- fs::dir_ls("data/stimuli/", regexp = "*.csv") %>%
  map_df(read_csv)

latest_stimuli <- read_csv("stimuli.csv")
hypotheses <- read_csv("hypotheses.csv")

bind_cols(
  latest_stimuli %>%
    select(premise, connective = Connective, inference_A, inference_B),
  hypotheses
) %>%
  select(item, category, connective, premise, inference_A, inference_B, choice) %>%
  write_csv("data/stimuli_all_0518.csv")
