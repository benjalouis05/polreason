import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
df = pd.read_csv("first_order_fit_results.csv")
df = df.dropna(subset=['Mean_TVD'])
df = df.sort_values("Mean_TVD", ascending=False)

# Generate Plot
plt.figure(figsize=(10, 10))
bars = plt.barh(df['Model'], df['Mean_TVD'], color='skyblue')

plt.title('First-Order Fit: Mean Total Variation Distance vs. GSS Marginals')
plt.xlabel('Mean TVD (0 = Perfect Match)')
plt.ylabel('Model')

# Add values to bars
for bar in bars:
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height()/2, f' {width:.3f}', va='center')

plt.tight_layout()

# Save to artifact dir
output_path = "/Users/benjaminsiegel/.gemini/antigravity/brain/176d8b86-7b71-42a8-bf2c-bef49089e439/mean_tvd_plot.png"
plt.savefig(output_path, dpi=300)
print(f"Plot saved to {output_path}")
