# # --- Clean Workspace --- # #
rm(list = ls())
gc()
options(scipen = 999)
options(timeout = 10000)
options(warn = 1)

# # --- Setup --- # #
YEAR <- 2024
DIR_SCRIPTS <- 'analysis/scripts'

if (!dir.exists("analysis") || !dir.exists("generation")) {
  stop("Please run this script from the polreason/ root directory")
}

# # --- Source Configs & Utils --- # #
source(file = file.path(DIR_SCRIPTS, '0.config.R'))
source(file = file.path(DIR_SCRIPTS, 'v.common_utils.R'))

message("\n====================================================================")
message("RUNNING CONSTRAINT VIOLIN PLOTS ONLY")
message("Year: ", YEAR)
message("====================================================================\n")

# # --- Step 1: Constraint Statistics (v2_a) --- # #
message("\n[1/2] Plotting Constraint Statistics (v2_a.constraint_stats.R) ...")
# This creates:
# - constraint_pc1_var_explained_by_edu_2024.pdf
# - constraint_effective_dependence_by_edu_2024.pdf
source(file = file.path(DIR_SCRIPTS, 'v2_a.constraint_stats.R'))

# # --- Step 2: Constraint Statistics Deltas (v2_b) --- # #
message("\n[2/2] Plotting Constraint Statistics Deltas (v2_b.constraint_stats_delta.R) ...")
# This creates:
# - pc1_beliefs_conditional_2024.pdf
# - effective_dependence_beliefs_conditional_2024.pdf
# - nonpersona_cumulative_pc_share_2024.pdf
source(file = file.path(DIR_SCRIPTS, 'v2_b.constraint_stats_delta.R'))

message("\n✅ Constraint violin plots completed successfully!")
message("Check output in: analysis/viz/constraint_violins_", YEAR, "/")
