# Generate Scatter Plot of First-Order vs Second-Order Error

library(data.table)
library(ggplot2)
library(ggrepel)

YEAR <- 2024
DIR_SCRIPTS <- 'analysis/scripts'
source(file.path(DIR_SCRIPTS, '0.config.R'))
source(file.path(DIR_SCRIPTS, 'v.common_utils.R'))

#' Extract pairwise correlations from a correlation matrix
extract_pairwise_cors <- function(R) {
  if (is.null(R)) return(NULL)
  R <- as.matrix(R)
  vars <- colnames(R)
  if (is.null(vars) || length(vars) < 2) return(NULL)

  pairs <- which(upper.tri(R), arr.ind = TRUE)

  data.table(
    var1 = vars[pairs[, 1]],
    var2 = vars[pairs[, 2]],
    rho  = R[pairs]
  )
}

#' Compute median pairwise correlations across bootstrap samples
compute_median_pairwise_cors <- function(corr_list) {
  all_pairs <- rbindlist(lapply(corr_list, extract_pairwise_cors), fill = TRUE)
  if (nrow(all_pairs) == 0) return(NULL)

  median_pairs <- all_pairs[, .(median_rho = median(rho, na.rm = TRUE)),
                            by = .(var1, var2)]

  median_pairs[, pair_label := mapply(function(a, b) {
    paste(sort(c(a, b)), collapse = " × ")
  }, var1, var2)]

  median_pairs
}

ARTIFACT_DIR <- "/Users/benjaminsiegel/.gemini/antigravity/brain/91670977-3181-457d-90a9-f9993879ee22"

message("Loading TVD Data...")
tvd_data <- fread('nemo_tvd.csv')

message("Loading Correlation Data...")
gss_corr <- load_corr_for_rater('gss', year = YEAR)
nemo_corr <- load_corr_for_rater('Nemo_2', year = YEAR)

message("Computing pairwise medians...")
gss_pairs <- compute_median_pairwise_cors(gss_corr)
nemo_pairs <- compute_median_pairwise_cors(nemo_corr)

setnames(gss_pairs, "median_rho", "gss_rho")
setnames(nemo_pairs, "median_rho", "nemo_rho")

merged_pairs <- merge(gss_pairs, nemo_pairs, by=c("var1", "var2", "pair_label"))
merged_pairs[, error := abs(nemo_rho - gss_rho)]

# Aggregate error per variable
message("Aggregating error per variable...")
var_errors <- rbind(
  merged_pairs[, .(error = error, var = var1)],
  merged_pairs[, .(error = error, var = var2)]
)
var_mae <- var_errors[, .(mae = mean(error, na.rm=TRUE)), by=var]

setnames(var_mae, "var", "variable")
plot_dt <- merge(tvd_data, var_mae, by="variable")

# Plotting
message("Generating Plot...")
# Calculate correlation
corr_val <- cor(plot_dt$tvd, plot_dt$mae, method = "pearson")

p <- ggplot(plot_dt, aes(x = tvd, y = mae, label = variable)) +
  geom_point(color = "steelblue", size = 3, alpha = 0.8) +
  geom_text_repel(size = 3.5, max.overlaps = 15, box.padding = 0.4) +
  geom_smooth(method = "lm", se = FALSE, color = "black", linetype = "dashed") +
  labs(
    title = "Does accurate marginal distribution predict accurate structural connections?",
    subtitle = sprintf("Nemo 2 (Pearson r = %.2f)\nX: First-Order TVD (Error) | Y: Second-Order MAE (Error)", corr_val),
    x = "First-Order Error (TVD)",
    y = "Second-Order Error (Mean Abs Correlation Difference)"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face="bold", size=14),
    plot.subtitle = element_text(size=12, color="gray30", margin = margin(b=10)),
    axis.title = element_text(face="bold"),
    axis.text = element_text(size=10)
  )

ggsave(file.path(ARTIFACT_DIR, "nemo_error_scatter.png"), plot = p, width = 10, height = 8, dpi = 300, bg = "white")
message("Success! Plot saved to artifact directory.")
