import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt

# Load true GSS data
gss_df = pd.read_csv("generation/data/gss2024_dellaposta_extract.csv")

for col in ['colath', 'colrac', 'colmslm']:
    if col in gss_df.columns:
        gss_df[col] = gss_df[col].replace({4.0: 1.0, 5.0: 2.0})

csv_files = glob.glob("generation/synthetic_data/year_2024/*.csv")

def get_proportions(series):
    series = series.dropna()
    if len(series) == 0:
        return {}
    props = series.value_counts(normalize=True).to_dict()
    return props

def tvd(prop1, prop2):
    keys = set(prop1.keys()).union(set(prop2.keys()))
    distance = sum(abs(prop1.get(k, 0) - prop2.get(k, 0)) for k in keys) / 2.0
    return distance

variable_tvds = {}
variable_texts = {}

for f in csv_files:
    model_df = pd.read_csv(f)
    if 'variable' not in model_df.columns:
        continue
    if 'model' in model_df.columns and model_df['model'].iloc[0] != 'mistralai/mistral-nemo':
        continue
    
    model_df['answer_num'] = pd.to_numeric(model_df['answer'], errors='coerce')
    
    variables = model_df['variable'].unique()
    for var in variables:
        if var in gss_df.columns:
            gss_prop = get_proportions(gss_df[var])
            model_prop = get_proportions(model_df[model_df['variable'] == var]['answer_num'])
            if len(model_prop) > 0 and len(gss_prop) > 0:
                dist = tvd(gss_prop, model_prop)
                
                if var not in variable_tvds:
                    variable_tvds[var] = []
                variable_tvds[var].append(dist)
                
                # capture question text
                if var not in variable_texts and 'question_short' in model_df.columns:
                    texts = model_df[model_df['variable'] == var]['question_short'].dropna().unique()
                    if len(texts) > 0:
                        variable_texts[var] = texts[0]

# Aggregate
results = []
for var, tvd_list in variable_tvds.items():
    results.append({
        'variable': var,
        'question': variable_texts.get(var, var),
        'mean_tvd': np.mean(tvd_list)
    })

res_df = pd.DataFrame(results).sort_values("mean_tvd")

# Extract top 8 and bottom 8
top_8 = res_df.head(8).copy()
bottom_8 = res_df.tail(8).copy()
plot_df = pd.concat([top_8, bottom_8])

# Create combined labels with wrapping for readability
import textwrap
def format_label(row):
    text = row['question']
    # Aggressively clean up common survey fluff
    text = text.replace("Please tell me whether or not you think it should be possible for a pregnant woman to obtain a legal abortion if", "Abortion if:")
    text = text.replace("We are faced with many problems in this country, none of which can be solved easily or inexpensively. I'm going to name some of these problems, and for each one I'd like you to tell me whether you think we're spending too much money on it, too little money, or about the right amount. Are we spending too much, too little, or about the right amount on: ", "Spending on: ")
    text = text.replace("I am going to name some institutions in this country. As far as the people running these institutions are concerned, would you say you have a great deal of confidence, only some confidence, or hardly any confidence at all in them: ", "Confidence in: ")
    text = text.replace("There are different opinions about immigrants from other countries living in America. (By immigrants we mean people who come to settle in America.) How much do you agree or disagree with each of the following statement: ", "Immigrants: ")
    text = text.replace("Please read the following statement and indicate whether you strongly agree, agree, disagree, or strongly disagree: ", "")
    # Wrap text
    wrapped = "\\n".join(textwrap.wrap(text, width=55))
    return f"{row['variable']}\\n({wrapped})"

plot_df['label'] = plot_df.apply(format_label, axis=1)

# Ensure sorting for visualization (highest to lowest TVD so bottom is most accurate)
plot_df = plot_df.sort_values('mean_tvd', ascending=True)

# Generate Plot
plt.figure(figsize=(12, 12))
# Adjust spacing for long labels
plt.subplots_adjust(left=0.35)
bars = plt.barh(plot_df['label'], plot_df['mean_tvd'], color=['skyblue']*8 + ['salmon']*8)

plt.title('Most vs Least Accurate Variables: Mistral Nemo', fontsize=14)
plt.xlabel('TVD (0 = Perfect Match, 1 = Completely Disjoint)', fontsize=12)

# Add values to bars
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, f'{width:.3f}', va='center', fontsize=11, fontweight='bold')

plt.xlim(0, 1.1)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()

# Save to artifact dir
output_path = "/Users/benjaminsiegel/.gemini/antigravity/brain/9a21f01d-29fa-4cf3-aec9-2186b4e0aa4a/nemo_per_question_tvd_plot.png"
plt.savefig(output_path, dpi=300)
print(f"Plot saved to {output_path}")
