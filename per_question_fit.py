import pandas as pd
import glob
import numpy as np

# Load true GSS data
gss_df = pd.read_csv("generation/data/gss2024_dellaposta_extract.csv")

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

print("=== MOST ACCURATE QUESTIONS (Lowest TVD) ===")
print(res_df.head(5).to_string(index=False))
print("\n=== LEAST ACCURATE QUESTIONS (Highest TVD) ===")
print(res_df.tail(5).to_string(index=False))
