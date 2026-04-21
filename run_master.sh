#!/bin/bash

# ==============================================================================
# Slurm Submission Script for Polreason Analysis Pipeline
# ==============================================================================
#
# This script executes the 'master.R' analysis pipeline, which handles
# data shaping, multiple imputation, bootstrap correlations, and visualization.
#
# Usage:
#   sbatch run_master.sh
#
# ==============================================================================

#SBATCH --job-name=polreason_master
#SBATCH --output=logs/master_%j.out
#SBATCH --error=logs/master_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --account=pi_ju78
#SBATCH --partition=standard

# --- Environment Setup ---

# Create logs directory if it doesn't exist
mkdir -p logs

# Load R module (Adjust module name based on your cluster's naming convention)
# Some clusters use 'R/4.3.1', others just 'R'.
module load R || module load R/4.3.3 || echo "Warning: R module not found. Assuming R is in PATH."

# --- Execute Analysis ---

echo "Starting polreason analysis pipeline: master.R"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODENAME"
echo "Start time: $(date)"

# Run the master R script from the repository root
# master.R assumes it is run from the root directory
Rscript analysis/scripts/master.R

echo "Pipeline completed at: $(date)"
