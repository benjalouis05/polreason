# clean workspace
rm(list = ls())
# clean garbadge
gc()
# clear graphics device
# dev.off()
# set decimals to digits instead of scientific
options(scipen = 999)
# set timeout limit (laxed)
options(timeout = 10000)
# ensure warnings are not converted into errors
options(warn = 1)
# set work directory - assumes script is run from polreason/ root
# If running from elsewhere, set working directory to polreason/ first
if (!dir.exists("analysis") || !dir.exists("generation")) {
  stop("Please run this script from the polreason/ root directory")
}

# # --- Source Configs ----------------------------------------------------- # #
YEAR  <- 2024

DIR_SCRIPTS <- 'analysis/scripts'
source(file = file.path(DIR_SCRIPTS,'0.config.R'))

# # --- Define Experiment Details ------------------------------------------ # #
rater_files <- list.files(
  path    = sprintf("generation/synthetic_data/year_%d", YEAR),
  pattern = "\\.csv$",
  full.names = FALSE
)

RATERrs_list <- c("gss", tools::file_path_sans_ext(rater_files))

# # --- SKIP DATA SHAPING + BOOTSTRAP LOOPS --- # #
# This script directly runs the visualization and plotting using existing cached RDS files.

message("\n[1/6] Loading visualization utilities...")
# Source viz utils
source(file = file.path(DIR_SCRIPTS,'v.common_utils.R'))

message("\n[2/6] Plotting Multivariate Normal draws (v1_a.mvn_plot.R) ...")
# Plotting draws from MVN loop
source(file = file.path(DIR_SCRIPTS,'v1_a.mvn_plot.R'))

message("\n[3/6] Generating Saturn Plots and Belief Grids (v1_b.saturn_plot.R) ...")
# Saturn plot: Global constraint visualization via MAC (faceted)
source(file = file.path(DIR_SCRIPTS,'v1_b.saturn_plot.R'))

# Saturn animation: Cycling through quantiles Q95 → Q5 (optional, takes ~2-5 min)
# Uncomment to generate animated GIF:
# source(file = file.path(DIR_SCRIPTS,'v1_c.saturn_animation.R'))

message("\n[4/6] Plotting Constraint Statistics (v2_a.constraint_stats.R) ...")
# Plot constraint statistics
source(file = file.path(DIR_SCRIPTS,'v2_a.constraint_stats.R'))

message("\n[5/6] Plotting Constraint Statistics Deltas (v2_b.constraint_stats_delta.R) ...")
source(file = file.path(DIR_SCRIPTS,'v2_b.constraint_stats_delta.R'))

message("\n[6/6] Plotting Missing Dimensions (v3.missing_dimensions.R) ...")
source(file = file.path(DIR_SCRIPTS,'v3.missing_dimensions.R'))

message("\n✅ All visualization scripts completed successfully!")
