# %%
import pandas as pd
import numpy as np
import seaborn as sns
import scipy
import scipy.stats as stats
import matplotlib.pyplot as plt
plt.style.use('tableau-colorblind10')
sns.set(style="ticks")
PALETTE = {
    'A (expensive)': 'darkturquoise',
    'B (cheap)': 'y',
    'male': 'dodgerblue',
    'female': 'tomato',
}
# %%

def read_csv_and_preprocess_data(filename):
    df = pd.read_csv(filename, sep=",", dtype={
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
    def rename_gender(row):
        if row['gender'] == 'f':
            return 'female'
        elif row['gender'] == 'm':
            return 'male'
        else:
            return None
    df['gender'] = df.apply(rename_gender, axis = 1)
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
            row['turron'] = 'A (expensive)'
        else:
            row['turron'] = 'B (cheap)'
        return row
    melted = melted.apply(get_turron_name, axis=1)
    def rename_variables(row):
        params = ['texture', 'sweetness', 'flavour', 'visual', 'overall']
        for param in params:
            if param in row.variable:
                row.variable = param
        return row
    melted = melted.apply(rename_variables, axis=1)
    melted['composite_variable'] = melted['variable'] + melted['turron']
    melted
    # Remove 'sweetness' as a variable form the dataset, because we believe it was
    # missinterpreted by many participants.
    melted = melted.drop(melted[melted.variable == 'sweetness'].index)
    df = df.drop('sweetness_A', axis=1)
    df = df.drop('sweetness_B', axis=1)
    return df, melted

df, melted = read_csv_and_preprocess_data("data.csv")
df
melted

#%% [markdown]
# ## Comparing attributes between groups
#
#%%
def gender_by_turron_per_category(melted):
    for param  in ['texture', 'flavour', 'visual', 'sweetness', 'overall']:
        melted['composite_variable'] = melted['variable'] + melted['turron']
        param_a = param+"A"
        param_b = param+"B"
        mask = melted['composite_variable'].str.contains('|'.join([param_a, param_b]))
        sns.catplot(x="composite_variable", y="value", hue="gender", kind="point", data=melted[mask])
# gender_by_turron_per_category(melted)

####################################################################################################
#%% [markdown]
# ### Gender (t-test)
#%%
def gender_general_effect(melted):
    df = melted.copy()
    p_values = []
    for param  in ['texture', 'flavour', 'visual', 'overall']:
        females = df[(df['variable'] == param) & (df['gender'] == 'female')]
        males = df[(df['variable'] == param) & (df['gender'] == 'male')]
        statistic, pvalue = stats.ttest_ind(females['value'], males['value'])
        print(f"P Value {param} = {pvalue}")
        p_values.append(f"{param}: {pvalue:1.3f}")

    g = sns.catplot(x="variable", y="value", hue="gender", kind="bar", data=df, palette=PALETTE)
    plt.subplots_adjust(top=0.85)
    g.fig.suptitle(f"\nGender general effect.")
    g.axes[0,0].set_ylabel('mean score')
    g.axes[0,0].xaxis.label.set_visible(False)
    g.axes[0,0].text(4, 1.5, f"p-values:", fontweight='bold')
    g.axes[0,0].text(4, 0, '\n'.join(p_values))
    return g

g = gender_general_effect(melted)
g.savefig("results/gender_general_effect.png", facecolor=g.fig.get_facecolor())
####################################################################################################
#%% [markdown]
# ### Turron by Gender
#%%

# def turron_by_gender(melted):
#     df = melted.copy()

#     df['turron:gender'] = df['turron'] + ':' + df['gender']
#     palette = {'A:f': 'royalblue', 'A:m':'lightsteelblue', 'B:f': 'burlywood', 'B:m': 'bisque'}
#     return sns.catplot(x="variable", y="value", hue="turron:gender", kind="bar", data=df, palette = palette)
# turron_by_gender(melted)
#%%
def turron_by_gender2(melted):
    g = sns.FacetGrid(melted, col="variable", height=5, aspect=0.4)
    g.map(sns.barplot, "gender", "value", "turron", palette=PALETTE, errwidth="2")
    g.add_legend(title="turron")

    g.axes[0,0].set_ylabel('mean score')
    g.axes[0,0].xaxis.label.set_visible(False)
    g.axes[0,1].set_xlabel('Gender')
    g.axes[0,2].xaxis.label.set_visible(False)
    g.axes[0,3].xaxis.label.set_visible(False)
    # set figure title
    plt.subplots_adjust(top=0.85)
    g.fig.suptitle('turron:gender')

    return g
g = turron_by_gender2(melted)
g.savefig("results/turron_by_gender.png", facecolor=g.fig.get_facecolor())

#%% [markdown]
# ### Turron A vs B by Gender (paired t-test)
#%%
comparissons = (
    ('flavour_A', 'flavour_B'),
    ('visual_A', 'visual_B'),
    ('texture_A', 'texture_B'),
    ('overall_A', 'overall_B'),
)

for (cat_A, cat_B) in comparissons:
    for gender in ('male', 'female',):
        df_cat = df[[cat_A, cat_B, 'gender']].dropna()
        df_cat['delta'] = df_cat[cat_A] - df_cat[cat_B]
        df_cat = df_cat[df_cat['gender'] == gender]

        statistic, pvalue = stats.ttest_rel(df_cat[cat_A], df_cat[cat_B])
        print(f"P Value gender: {gender};\t{cat_A} vs {cat_B}\t= {pvalue:1.4f} / delta mean {df_cat['delta'].mean():1.4f}")


#%% [markdown]
# ## By Turron
#%%
def turron_general(melted):
    g = sns.catplot(x="variable", y="value", hue="turron", kind="bar", data=melted, palette=PALETTE)
    plt.subplots_adjust(top=0.85)
    g.fig.suptitle(f"\nTurron A vs B")
    g.axes[0,0].set_ylabel('mean score')
    g.axes[0,0].xaxis.label.set_visible(False)
    return g
g = turron_general(melted)
g.savefig("results/turron_general.png", facecolor=g.fig.get_facecolor())
#%%
sns.catplot(x="variable", y="value", hue="first_time_tasting", kind="bar", data=melted)
sns.catplot(x="variable", y="value", hue="correct_guess", kind="bar", data=melted)

#%%

# def turron_by_first_time_tasting(melted):
#     def rename_first_time_tasting(row):
#         if row['first_time_tasting'] == 'Y':
#             return 'naive'
#         elif row['first_time_tasting'] == 'N':
#             return 'not naive'
#         else:
#             return None

#     df = melted.copy()
#     df['first_time_tasting'] = df.apply(rename_first_time_tasting, axis = 1)
#     df['turron:first_time_tasting'] = df['turron'] + ':' + df['first_time_tasting']
#     palette = {
#         'A:not naive': 'royalblue',
#         'A:naive':'lightsteelblue',
#         'B:not naive': 'burlywood',
#         'B:naive': 'bisque'
#     }

#     return sns.catplot(x="variable", y="value", hue="turron:first_time_tasting", kind="bar", data=df, palette = palette)
# turron_by_first_time_tasting(melted)

#%%
def turron_by_first_time_tasting2(melted):
    def rename_first_time_tasting(row):
        if row['first_time_tasting'] == 'Y':
            return 'naive'
        elif row['first_time_tasting'] == 'N':
            return 'not naive'
        else:
            return None

    df = melted.copy()
    df['first_time_tasting'] = df.apply(rename_first_time_tasting, axis = 1)
    g = sns.FacetGrid(df, col="variable", height=5, aspect=0.4)
    g.map(sns.barplot, "first_time_tasting", "value", "turron", palette=PALETTE, errwidth="2")
    g.add_legend(title="turron")

    g.axes[0,0].set_ylabel('mean score')
    g.axes[0,0].xaxis.label.set_visible(False)
    g.axes[0,1].set_xlabel('Was is the first time to taste turron?')
    g.axes[0,2].xaxis.label.set_visible(False)
    g.axes[0,3].xaxis.label.set_visible(False)
    # set figure title
    plt.subplots_adjust(top=0.85)
    g.fig.suptitle('turron:first_time_tasting')

    return g
g = turron_by_first_time_tasting2(melted)
g.savefig("results/turron_by_first_time_tasting.png", facecolor=g.fig.get_facecolor())


#%%
def turron_by_correct_guess2(melted):
    def rename_correct_guess(row):
        if row['correct_guess'] == 'Y':
            return 'correct'
        elif row['correct_guess'] == 'N':
            return 'incorrect'
        else:
            return Null

    df = melted.copy()
    df['correct_guess'] = df.apply(rename_correct_guess, axis = 1)
    g = sns.FacetGrid(df, col="variable", height=5, aspect=0.4)
    g.map(sns.barplot, "correct_guess", "value", "turron", palette=PALETTE, errwidth="2")
    g.add_legend(title="turron")

    g.axes[0,0].set_ylabel('mean score')
    g.axes[0,0].xaxis.label.set_visible(False)
    g.axes[0,1].set_xlabel('Guessed which turron was expensive')
    g.axes[0,2].xaxis.label.set_visible(False)
    g.axes[0,3].xaxis.label.set_visible(False)
    # set figure title
    plt.subplots_adjust(top=0.85)
    g.fig.suptitle('turron:correct_guess')

    return g
g = turron_by_correct_guess2(melted)
g.savefig("results/turron_by_correct_guess.png", facecolor=g.fig.get_facecolor())
#%%
def success_rate_by_naiveness(df):
    contingency = pd.crosstab(df.first_time_tasting, df.correct_guess)
    oddsratio, pvalue = stats.fisher_exact(contingency)
    print(f"p-value: ", pvalue)
    non_naive = contingency.loc['N'].sum()
    naive = contingency.loc['Y'].sum()
    correct_non_naive = contingency.loc['N', 'Y']
    correct_naive = contingency.loc['Y', 'Y']
    fig, ax = plt.subplots()
    sns.barplot(
        x=['naive','non-naive'],
        y=[ correct_naive/naive, correct_non_naive/non_naive ],
        palette={
            'naive': 'slategrey',
            'non-naive': 'slategrey',
        },
    )
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.title(f'Success Rate\np: {pvalue:1.3f}')
    return fig, ax

fig, ax = success_rate_by_naiveness(df)
fig.savefig("results/success_rate_by_naiveness.png", facecolor=fig.get_facecolor())
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
    # ('sweetness_A', 'sweetness_B'),
    ('flavour_A', 'flavour_B'),
    ('visual_A', 'visual_B'),
    ('texture_A', 'texture_B'),
    ('overall_A', 'overall_B'),
)

for param  in ['texture', 'flavour', 'visual', 'overall']:
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



#%% [markdown]
# ### Effect of number of hours without eating
#%%

def influence_of_fasting(melted):
    melted_hours = melted[['variable', 'turron', 'hours since last eat', 'value']].dropna()
    fig, ax = plt.subplots()
    sns.swarmplot(x='hours since last eat', y='value', hue='turron', data=melted_hours, palette=PALETTE, size=8, edgecolor='gray', linewidth=0.5)
    fig.set_size_inches(11.7, 8.27)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.axes.set_ylabel('score')
    plt.title(f'Influence of fasting')
    return fig, ax

fig, ax = influence_of_fasting(melted)
fig.savefig("results/influence_of_fasting.png", facecolor=fig.get_facecolor())

#%% [markdown]
# ### Analysing preference coherence
#%%

def preference_coherence(df):
    df = df.copy()
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
    print(coherence_count)

    plt.bar(0                              , 1, width=coherence_count['%'][0], align='edge', color='mediumseagreen', label='Coherent')
    plt.bar(coherence_count['%'][0]        , 1, width=coherence_count['%'][1], align='edge', color='darksalmon'       , label='Not Coherent')
    plt.bar(coherence_count['%'][0:2].sum(), 1, width=coherence_count['%'][2], align='edge', color='lightgray'    , label='Tie')

    fig=plt.figure(1)
    plt.title(f'Preference coherence')
    ax = fig.gca()
    ax.legend([
            f"Coherent ({coherence_count['coherence'][0]})",
            f"Not Coherent ({coherence_count['coherence'][1]})",
            f"Tie ({coherence_count['coherence'][2]})",
        ],
        bbox_to_anchor=(1, 1),
        frameon=False,
    )
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.xaxis.set_ticks([0, 0.75, 0.9, 1])
    ax.tick_params(length=0)

    fig.set_size_inches(10, 2, forward=True)
    return fig, ax
fig, ax = preference_coherence(df)
fig.savefig("results/preference_coherence.png", facecolor=fig.get_facecolor(), bbox_inches='tight')

#%%

def influence_of_naiveness_on_score(df, with_individuals=True):
    total_participants = len(df)

    naive = df[df['first_time_tasting'] == 'Y']
    not_naive = df[df['first_time_tasting'] == 'N']
    unknown = df[df['first_time_tasting'].isnull()]

    naive_right_guess = naive[naive['correct_guess'] == 'Y']
    naive_wrong_guess = naive[naive['correct_guess'] == 'N']
    not_naive_right_guess = not_naive[not_naive['correct_guess'] == 'Y']
    not_naive_wrong_guess = not_naive[not_naive['correct_guess'] == 'N']
    unknown_right_guess = unknown[unknown['correct_guess'] == 'Y']
    unknown_wrong_guess = unknown[unknown['correct_guess'] == 'N']

    print(f"total participants: {total_participants}")
    print(f"\tnaive: {len(naive)}")
    print(f"\t\tguessed correctly: {len(naive_right_guess)}")
    print(f"\t\t\t {', '.join(naive_right_guess['name'])}")
    print(f"\t\tguessed wrong: {len(naive_wrong_guess)}")
    print(f"\t\t\t {', '.join(naive_wrong_guess['name'])}")

    print(f"\tnot naive: {len(not_naive)}")
    print(f"\t\tguessed correctly: {len(not_naive_right_guess)}")
    print(f"\t\t\t {', '.join(not_naive_right_guess['name'])}")
    print(f"\t\tguessed wrong: {len(not_naive_wrong_guess)}")
    print(f"\t\t\t {', '.join(not_naive_wrong_guess['name'])}")

    print(f"\tunkown: {len(unknown)}")
    print(f"\t\tguessed correctly: {len(unknown_right_guess)}")
    print(f"\t\tguessed wrong: {len(unknown_wrong_guess)}")
    print(f"\t\t\t {', '.join(unknown_wrong_guess['name'])}")


    sankey_data = []
    sankey_data.append(('total', len(naive), 'naive'))
    sankey_data.append(('total', len(not_naive), 'not_naive'))
    sankey_data.append(('total', len(unknown), 'unknown'))

    sankey_data.append(('naive', len(naive_right_guess), 'guessed correctly (Naive)'))
    sankey_data.append(('naive', len(naive_wrong_guess), 'guessed wrong (Naive)'))

    sankey_data.append(('not_naive', len(not_naive_right_guess), 'guessed correctly (Not Naive)'))
    sankey_data.append(('not_naive', len(not_naive_wrong_guess), 'guessed wrong (Not Naive)'))

    sankey_data.append(('unknown', len(unknown_right_guess), 'guessed correctly (ukn)'))
    sankey_data.append(('unknown', len(unknown_wrong_guess), 'guessed wrong (ukn)'))

    if (with_individuals):
        for _, row in naive_right_guess.iterrows():
            sankey_data.append(('guessed correctly (Naive)', 1, row['name']))
        for _, row in naive_wrong_guess.iterrows():
            sankey_data.append(('guessed wrong (Naive)', 1, row['name']))
        for _, row in not_naive_right_guess.iterrows():
            sankey_data.append(('guessed correctly (Not Naive)', 1, row['name']))
        for _, row in not_naive_wrong_guess.iterrows():
            sankey_data.append(('guessed wrong (Not Naive)', 1, row['name']))
        for _, row in unknown_right_guess.iterrows():
            sankey_data.append(('guessed correctly (ukn)', 1, row['name']))
        for _, row in unknown_wrong_guess.iterrows():
            sankey_data.append(('guessed wrong (ukn)', 1, row['name']))

    return sankey_data

def format_for_sankeymatic(data):
    """
    Formats sankey data to be directly pasted on
    http://sankeymatic.com/build/
    """
    format_row = lambda row: f"{row[0]} [{row[1]}] {row[2]}"
    return '\n'.join(list(map(format_row, data)))

sankey_data = influence_of_naiveness_on_score(df, with_individuals=True)
print("\n#######################################################")
print("\n\nTo generate a sankey chart: copy the following in")
print("http://sankeymatic.com/build/\n")

print(format_for_sankeymatic(sankey_data))


#%%
def guess_rate(df):
    df = df.copy()
    rename_values = lambda x: 'Correct' if x['correct_guess'] == 'Y' else 'Incorrect'
    df['correct_guess'] = df.apply(rename_values, axis=1)

    fig, ax = plt.subplots()
    sns.countplot(
        x='correct_guess',
        data=df,
        order=['Correct', 'Incorrect'],
        palette={
            'Incorrect': 'darksalmon',
            'Correct': 'mediumseagreen',
        },
    )


    plt.title(f'Participants who correctly guessed \nwhich turron was the most expensive')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    # ax.get_yaxis().set_visible(False)
    plt.grid(color='lightgray', linestyle=':', linewidth=1, axis='y')
    ax.yaxis.set_ticks([])
    ax.text(0 - 0.215, 1, "12", alpha=0.7, color='white', fontsize=50, fontweight='bold')
    ax.text(1 - 0.215, 1, "13", alpha=0.7, color='white', fontsize=50, fontweight='bold')
    ax.tick_params(length=0)
    ax.yaxis.label.set_visible(False)
    ax.xaxis.label.set_visible(False)
    fig.set_size_inches(5, 5, forward=True)

    return fig, ax
fig, ax = guess_rate(df)
fig.savefig("results/guess_rate.png", facecolor=fig.get_facecolor(), bbox_inches='tight')
