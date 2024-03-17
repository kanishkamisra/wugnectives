library(tidyverse)

stimuli_raw <- fs::dir_ls("data/stimuli/", regexp = "*.csv") %>%
  map_df(read_csv)
