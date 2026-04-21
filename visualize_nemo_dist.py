import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import textwrap

# 1. Setup Data
gss = pd.read_csv('generation/data/gss2024_dellaposta_extract.csv')
for col in ['colath', 'colrac', 'colmslm']:
    if col in gss.columns:
        gss[col] = gss[col].replace({4.0: 1.0, 5.0: 2.0})

csv_files = glob.glob('generation/synthetic_data/year_2024/*.csv')
nemo_f = [f for f in csv_files if 'mistral-nemo' in f][0]
nemo_df = pd.read_csv(nemo_f)
nemo_df['answer_num'] = pd.to_numeric(nemo_df['answer'], errors='coerce')

def get_proportions(series):
    series = series.dropna()
    if len(series) == 0: return {}
    return series.value_counts(normalize=True).to_dict()

def tvd(prop1, prop2):
    keys = set(prop1.keys()).union(set(prop2.keys()))
    return sum(abs(prop1.get(k, 0) - prop2.get(k, 0)) for k in keys) / 2.0

# 2. Find Top 4 and Bottom 4
res = []
var_texts = {}
for var in nemo_df['variable'].unique():
    if var in gss.columns:
        g1 = get_proportions(gss[var])
        m1 = get_proportions(nemo_df[nemo_df['variable'] == var]['answer_num'])
        if g1 and m1:
            res.append({'var': var, 'tvd': tvd(g1, m1)})
            # Get question text
            q_text = nemo_df[nemo_df['variable'] == var]['question_short'].iloc[0]
            var_texts[var] = q_text

res_df = pd.DataFrame(res).sort_values('tvd')
top_4 = res_df.head(4)['var'].tolist()
bottom_4 = res_df.tail(4)['var'].tolist()

target_vars = top_4 + bottom_4

# 3. Plotting
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for i, var in enumerate(target_vars):
    ax = axes[i]
    
    g_prop = get_proportions(gss[var])
    n_prop = get_proportions(nemo_df[nemo_df['variable'] == var]['answer_num'])
    
    # Sort keys for consistent category ordering
    keys = sorted(list(set(g_prop.keys()).union(set(n_prop.keys()))))
    g_vals = [g_prop.get(k, 0) for k in keys]
    n_vals = [n_prop.get(k, 0) for k in keys]
    
    x = np.arange(len(keys))
    width = 0.35
    
    ax.bar(x - width/2, g_vals, width, label='GSS (True)', color='gray', alpha=0.7)
    ax.bar(x + width/2, n_vals, width, label='Nemo (LLM)', color='blue', alpha=0.6)
    
    ax.set_title(f"{var} (TVD: {res_df[res_df['var']==var]['tvd'].iloc[0]:.3f})", fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([int(k) for k in keys])
    ax.set_ylim(0, 1.1)
    
    # Wrap title/text
    # text = var_texts[var]
    # ax.set_xlabel("\n".join(textwrap.wrap(text, width=40)), fontsize=8)

    if i == 0:
        ax.legend()

plt.suptitle('Mistral Nemo vs GSS Answer Distributions\nMost Accurate (Top Row) vs Least Accurate (Bottom Row)', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

output_path = "/Users/benjaminsiegel/.gemini/antigravity/brain/9a21f01d-29fa-4cf3-aec9-2186b4e0aa4a/nemo_distribution_comparison.png"
plt.savefig(output_path, dpi=300)
print(f"Plot saved to {output_path}")
