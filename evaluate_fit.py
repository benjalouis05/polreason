import pandas as pd
import glob
import numpy as np

# Load true GSS data
gss_df = pd.read_csv("generation/data/gss2024_dellaposta_extract.csv")

for col in ['colath', 'colrac', 'colmslm']:
    if col in gss_df.columns:
        gss_df[col] = gss_df[col].replace({4.0: 1.0, 5.0: 2.0})

csv_files = glob.glob("generation/synthetic_data/year_2024/*.csv")

results = []

def get_proportions(series):
    series = series.dropna()
    if len(series) == 0:
        return {}
    props = series.value_counts(normalize=True).to_dict()
    return props

def tvd(prop1, prop2):
    # compute total variation distance between two dictionaries of proportions
    keys = set(prop1.keys()).union(set(prop2.keys()))
    distance = sum(abs(prop1.get(k, 0) - prop2.get(k, 0)) for k in keys) / 2.0
    return distance

for f in csv_files:
    model_df = pd.read_csv(f)
    if 'variable' not in model_df.columns:
        continue
    # we need `answer` or `raw_response` as numeric.
    model_df['answer_num'] = pd.to_numeric(model_df['answer'], errors='coerce')
    
    variables = model_df['variable'].unique()
    
    tvds = []
    for var in variables:
        if var in gss_df.columns:
            gss_prop = get_proportions(gss_df[var])
            model_prop = get_proportions(model_df[model_df['variable'] == var]['answer_num'])
            if len(model_prop) > 0 and len(gss_prop) > 0:
                dist = tvd(gss_prop, model_prop)
                tvds.append(dist)
                
    if len(model_df) > 0:
        if 'model' in model_df.columns and pd.notna(model_df['model'].iloc[0]):
            model_name = model_df['model'].iloc[0]
        else:
            model_name = f.split('/')[-1]
    else:
        model_name = f
        
    mean_tvd = np.mean(tvds) if tvds else None
    results.append({
        'Model': model_name,
        'Mean_TVD': mean_tvd,
        'Num_Variables': len(tvds)
    })

res_df = pd.DataFrame(results).sort_values("Mean_TVD")
res_df.to_csv("first_order_fit_results.csv", index=False)
print("=== First Order Fit (Mean Total Variation Distance) ===")
print("Lower is better (0 = perfect match with GSS marginals)")
print()
print(res_df.to_string(index=False))
