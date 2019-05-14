# %%
import pandas as pd
import numpy as np
import seaborn as sns
import scipy
import scipy.stats as stats
import matplotlib.pyplot as plt
plt.style.use('tableau-colorblind10')
sns.set(style="ticks")

# %%
df = pd.read_csv("data.csv", sep=",", dtype={
    'name': str,
    'gender': str,
    'email': str,
    'first_time_tasting': str,
    'hours since last eat': np.float64,
    'sweetness_A': np.float64,
    'texture_A': np.float64,
    'flavour_A': np.float64,
    'visual_A': np.float64,
    'overall_A': np.float64,
    'sweetness_B': np.float64,
    'texture_B': np.float64,
    'flavour_B': np.float64,
    'visual_B': np.float64,
    'overall_B': np.float64,
    'guess_expensive': str,
})
df
#%%
melted = pd.melt(df, id_vars=['name', 'gender', 'first_time_tasting', 'correct_guess', 'hours since last eat'], value_vars=[
    # 'hours since last eat',
    'sweetness_A',
    'texture_A',
    'flavour_A',
    'visual_A',
    'overall_A',
    'sweetness_B',
    'texture_B',
    'flavour_B',
    'visual_B',
    'overall_B',
]).dropna()
melted
def get_turron_name(row):
    if "_A" in row['variable']:
        row['turron'] = 'A'
    else:
        row['turron'] = 'B'
    return row
melted = melted.apply(get_turron_name, axis=1)
def rename_variables(row):
    params = ['texture', 'sweetness', 'flavour', 'visual', 'overall']
    for param in params:
        if param in row.variable:
            row.variable = param
    return row
melted = melted.apply(rename_variables, axis=1)
melted



#%%



# melted['variable'].str.contains("_A")
# melted.apply(lambda x: 1)

#%%
# param="texture"
# mask = (melted['variable'] == param) & (melted['turron'])
# melted[mask]
melted['composite_variable'] = melted['variable'] + melted['turron']
melted
#%% [markdown]
# ## Comparing attributes between groups
#
#%%
for param  in ['texture', 'flavour', 'visual', 'sweetness', 'overall']:
    melted['composite_variable'] = melted['variable'] + melted['turron']
    param_a = param+"A"
    param_b = param+"B"
    mask = melted['composite_variable'].str.contains('|'.join([param_a, param_b]))
    sns.catplot(x="composite_variable", y="value", hue="gender", kind="point", data=melted[mask])

####################################################################################################
#%% [markdown]
# ### Gender (t-test)
#%%
comparissons = (
    ('sweetness_A', 'sweetness_B'),
    ('flavour_A', 'flavour_B'),
    ('visual_A', 'visual_B'),
    ('texture_A', 'texture_B'),
    ('overall_A', 'overall_B'),
)

for param  in ['texture', 'flavour', 'visual', 'sweetness', 'overall']:
    # melted['composite_variable'] = melted['variable'] + melted['turron']
    # param_a = param+"A"
    # param_b = param+"B"
    # mask = melted['composite_variable'].str.contains('|'.join([param_a, param_b]))
    females = melted[(melted['variable'] == param) & (melted['gender'] == 'f')]
    males = melted[(melted['variable'] == param) & (melted['gender'] == 'm')]
    statistic, pvalue = stats.ttest_ind(females['value'], males['value'])
    print(f"P Value {param} = {pvalue}")

#melted[(melted['variable'] == param) & (melted['gender'] == 'f')]
sns.catplot(x="variable", y="value", hue="gender", kind="bar", data=melted)

####################################################################################################
#%% [markdown]
# ### Gender by turron
#%%


melted['turron:gender'] = melted['turron'] + ':' + melted['gender']

#melted

palette = {'A:f': 'royalblue', 'A:m':'lightsteelblue', 'B:f': 'burlywood', 'B:m': 'bisque'}

sns.catplot(x="variable", y="value", hue="turron:gender", kind="bar", data=melted, palette = palette)

#%% [markdown]
# ## By Turron
#%%
sns.catplot(x="variable", y="value", hue="turron", kind="bar", data=melted)

#%%
sns.catplot(x="variable", y="value", hue="first_time_tasting", kind="bar", data=melted)
sns.catplot(x="variable", y="value", hue="correct_guess", kind="bar", data=melted)

#%%

def rename_first_time_tasting(row):
    if row['first_time_tasting'] == 'Y':
        return 'naive'
    elif row['first_time_tasting'] == 'N':
        return 'not naive'
    else:
        return Null

melted['first_time_tasting'] = melted.apply(rename_first_time_tasting, axis = 1)

melted['turron:first_time_tasting'] = melted['turron'] + ':' + melted['first_time_tasting']


#melted

palette = {'A:not naive': 'royalblue', 'A:naive':'lightsteelblue', 'B:not naive': 'burlywood', 'B:naive': 'bisque'}

sns.catplot(x="variable", y="value", hue="turron:first_time_tasting", kind="bar", data=melted, palette = palette)


#%%

def rename_correct_guess(row):
    if row['correct_guess'] == 'Y':
        return 'correct'
    elif row['correct_guess'] == 'N':
        return 'incorrect'
    else:
        return Null

melted['correct_guess'] = melted.apply(rename_correct_guess, axis = 1)

melted['turron:correct_guess'] = melted['turron'] + ':' + melted['correct_guess']


#melted

palette = {'A:correct': 'royalblue', 'A:incorrect':'lightsteelblue', 'B:correct': 'burlywood', 'B:incorrect': 'bisque'}

sns.catplot(x="variable", y="value", hue="turron:correct_guess", kind="bar", data=melted, palette = palette)



#melted['turron:first_time_tasting']
#%%

contingency = pd.crosstab(df.first_time_tasting, df.correct_guess)
oddsratio, pvalue = stats.fisher_exact(contingency)
print(f"p-value: ", pvalue)
non_naive = contingency.loc['N'].sum()
naive = contingency.loc['Y'].sum()
correct_non_naive = contingency.loc['N', 'Y']
correct_naive = contingency.loc['Y', 'Y']
sns.barplot(x=['naive','non-naive'], y=[ correct_naive/naive, correct_non_naive/non_naive ])
plt.title(f'success rate\nnaive: people that had never before tasted turron\nnon-naive: people who had tasted turron before\np-value: {pvalue}')

#%% [markdown]
# # Paired 2-way anova statistical analysis
# https://raphaelvallat.com/pingouin.html
# # Paired t-test
# https://pythonfordatascience.org/paired-samples-t-test-python/

####################################################################################################
#%% [markdown]
# # Statistical analysis
# ### Turron A vs B (paired t-test)
#%%
comparissons = (
    ('sweetness_A', 'sweetness_B'),
    ('flavour_A', 'flavour_B'),
    ('visual_A', 'visual_B'),
    ('texture_A', 'texture_B'),
    ('overall_A', 'overall_B'),
)

for param  in ['texture', 'flavour', 'visual', 'sweetness', 'overall']:
    melted['composite_variable'] = melted['variable'] + melted['turron']
    param_a = param+"A"
    param_b = param+"B"
    mask = melted['composite_variable'].str.contains('|'.join([param_a, param_b]))
    sns.catplot(x="composite_variable", y="value", hue="name", kind="point", data=melted[mask])

for (cat_A, cat_B) in comparissons:
    df_cat = df[[cat_A, cat_B]].dropna()
    df_cat['delta'] = df_cat[cat_A] - df_cat[cat_B]

    statistic, pvalue = stats.ttest_rel(df_cat[cat_A], df_cat[cat_B])
    print(f"P Value {cat_A} vs {cat_B} = {pvalue} / delta mean {df_cat['delta'].mean()}")



####################################################################################################
#%% [markdown]
# ### Turron A vs B by Gender (paired t-test)
#%%
comparissons = (
    ('sweetness_A', 'sweetness_B'),
    ('flavour_A', 'flavour_B'),
    ('visual_A', 'visual_B'),
    ('texture_A', 'texture_B'),
    ('overall_A', 'overall_B'),
)

# for param  in ['texture', 'flavour', 'visual', 'sweetness', 'overall']:
#     melted['composite_variable'] = melted['variable'] + melted['turron']
#     param_a = param+"A"
#     param_b = param+"B"
#     mask = melted['composite_variable'].str.contains('|'.join([param_a, param_b]))
#     sns.catplot(x="composite_variable", y="value", hue="name", kind="point", data=melted[mask])

for (cat_A, cat_B) in comparissons:
    for gender in ('m', 'f',):
        df_cat = df[[cat_A, cat_B, 'gender']].dropna()
        df_cat['delta'] = df_cat[cat_A] - df_cat[cat_B]
        df_cat = df_cat[df_cat['gender'] == gender]

        statistic, pvalue = stats.ttest_rel(df_cat[cat_A], df_cat[cat_B])
        print(f"P Value gender: {gender}; {cat_A} vs {cat_B} = {pvalue} / delta mean {df_cat['delta'].mean()}")

#%% [markdown]
# ### Effect of number of hours without eating
#%%
melted_hours = melted[['variable', 'turron', 'hours since last eat', 'value']].dropna()
melted_hours = melted_hours[melted_hours['variable'] == 'sweetness']
sns.swarmplot(x='hours since last eat', y='value', hue='turron', data=melted_hours)

#%% [markdown]
# ### Analysing preference coherence
#%%

def calculate_preference(row):
    if row.overall_A > row.overall_B:
        return 'A'
    elif row.overall_A < row.overall_B:
        return 'B'
    else:
        return 'tie'
df['preference'] = df.apply(calculate_preference, axis=1)
def calculate_coherence(row):
    if row.preference == 'tie':
        return 'Tie'
    elif row.preference == row.guess_expensive:
        return 'Coherent'
    else:
        return 'Not Coherent'
df['coherence'] = df.apply(calculate_coherence, axis=1)
coherence_df = df[['overall_A', 'overall_B', 'preference', 'guess_expensive', 'coherence']].dropna()
coherence_df

coherence_count = coherence_df.groupby('coherence').agg({'coherence': 'count'})
total = coherence_count.sum()
coherence_count['%'] = coherence_count / total
coherence_count


plt.bar(0, coherence_count['%'][0], width=0.1, color='lightsalmon', label='Coherent')
plt.bar(0, coherence_count['%'][1], width=0.1, bottom=coherence_count['%'][0], color='teal', label='Not Coherent')
plt.bar(0, coherence_count['%'][2], width=0.1, bottom=coherence_count['%'][0:2].sum(), color='skyblue', label='Tie')
fig=plt.figure(1)

fig.set_size_inches(1, 10, forward=True)
