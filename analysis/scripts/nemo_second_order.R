# Nemo-Specific Second Order Analysis
# This script generates Saturn Plots and Belief Pair Grids specifically for Mistral Nemo vs GSS.

# --- Config and Utilities ---
YEAR <- 2024
DIR_SCRIPTS <- 'analysis/scripts'
source(file.path(DIR_SCRIPTS, '0.config.R'))
source(file.path(DIR_SCRIPTS, 'v.common_utils.R'))
source(file.path(DIR_SCRIPTS, 'v1_b.saturn_plot.R'))

# --- Target Artifact Dir ---
ARTIFACT_DIR <- "/Users/benjaminsiegel/.gemini/antigravity/brain/91670977-3181-457d-90a9-f9993879ee22"

# --- 1. Global Saturn Plot for Nemo ---
# We want to see Nemo compared specifically to the GSS baseline.
# The standard create_saturn_plot handles all raters, but we can filter the data.

message("\n--- Generating Global Saturn Plot ---")
# Manually call the components to get a Nemo-only view if needed, 
# or just run the standard one and highlight Nemo.

# For a cleaner visual, let's create a "Nemo vs GSS" Saturn Plot
p_saturn <- create_saturn_plot(
  base_out_dir = BASE_OUT_DIR,
  base_viz_dir = BASE_VIZ_DIR,
  year = YEAR,
  relevant_q = c("Q90", "Q75", "Q50"),
  delta_min = 0.0, # Show Nemo everywhere
  top_n_per_q = NULL,
  raters_subset = c("gss", "Nemo_v3"),
  highlight_gss = TRUE,
  save_pdf = FALSE # We'll save as PNG manually
)

# Save as PNG to artifacts
ggsave(
  filename = file.path(ARTIFACT_DIR, "nemo_saturn_global.png"),
  plot = p_saturn,
  width = 12, height = 14, units = "in", dpi = 300, device = "png"
)

# --- 2. Custom Belief Pair Grid for Requested Variables ---
message("\n--- Generating Custom Belief Pair Grid ---")

# User requested subset: 4 accurate, 4 inaccurate
custom_vars <- c('colath', 'pornlaw', 'natroad', 'immameco', 'eqwlth', 'spkrac', 'god', 'premarsx')

# Create a single grid for these 8 variables (28 pairs total)
p_custom <- create_belief_pair_grid(
  base_out_dir = BASE_OUT_DIR,
  year = YEAR,
  vars_subset = custom_vars,
  raters_subset = c("gss", "Nemo_v3"),
  highlight_rater = "Nemo_v3",
  highlight_color = "steelblue", # Using a nice blue for Nemo
  highlight_width = 1.0,
  page_ncol = 5, page_nrow = 6, # 30 slots available, perfect for 28 pairs
  save_pdf = FALSE
)

ggsave(
  filename = file.path(ARTIFACT_DIR, "nemo_belief_grid_custom.png"),
  plot = p_custom[[1]],
  width = 16, height = 14, units = "in", dpi = 300, device = "png"
)

message("\n--- Finished generating Nemo Second-Order visuals ---")
