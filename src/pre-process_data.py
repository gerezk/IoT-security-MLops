"""
Combines all packet classes into a single csv, with attack packets temporally interleaved into the normal packet stream
via random injection. Attack packets are given synthetic time information based on normal packets.
"""

import pandas as pd
from pathlib import Path
import numpy as np


def set_difference(list1, list2):
    """return list of elements in list1 that are not in list2"""
    return [element for element in list1 if element not in list2]

raw_dir_path = Path('../data/raw')
processed_dir_path = Path('../data/processed')
processed_dir_path.mkdir(exist_ok=True, parents=True)

time_col = 'frame.time_epoch'
precision = 6 #  for rounding floats
min_gap_size = 1e-6 #  in seconds
attack_prob = 0.05
np.random.seed(42)

n_records = 100_000

# load dfs - will take some time since >10 MM records
df_normal = pd.DataFrame()
dfs_attack = {}
for file in raw_dir_path.iterdir():
    filename = file.name.split('.')[0]
    packet_class = filename.split('_')[0]

    if file.suffix == '.csv':
        df = pd.read_csv(file, nrows=n_records, low_memory=False)
        df['class'] = packet_class
        if packet_class == 'legitimate':
            df_normal = df
        else:
            dfs_attack[packet_class] = df

attack_types = list(dfs_attack.keys())
# shuffle each attack dataframe once
attack_pools = {
    k: v.sample(frac=1).reset_index(drop=True)
    for k, v in dfs_attack.items()
}
attack_indices = {k: 0 for k in attack_types}

# randomly select packets from df_normal and attack_dfs
# temporal structure of df_normal is preserved, and attack packets given synthetic time columns based on normal packets
t_initial = df_normal.iloc[0][time_col]
rows = []
for i in range(len(df_normal) - 1):
    current = df_normal.iloc[i]
    next_row = df_normal.iloc[i + 1]

    rows.append(current)

    t_start = current[time_col]
    t_end = next_row[time_col]
    gap = t_end - t_start

    # decide whether to inject
    if gap > min_gap_size and np.random.rand() < attack_prob:
        # sample attack type uniformly
        attack_type = np.random.choice(attack_types)

        # get next row from that attack type
        idx = attack_indices[attack_type]
        attack_df = attack_pools[attack_type]

        attack_row = attack_df.iloc[idx % len(attack_df)].copy()
        attack_indices[attack_type] += 1

        # assign synthetic timestamp inside gap
        t_new = round(t_start + np.random.rand() * gap, precision)
        attack_row['frame.time_delta'] = round(t_new - t_start, precision)
        attack_row['frame.time_delta_displayed'] = attack_row['frame.time_delta']
        attack_row[time_col] = t_new
        attack_row['class'] = attack_type

        if len(rows) == 0:
            attack_row['frame.time_relative'] = 0.0
        else:
            attack_row['frame.time_relative'] = round(t_new - t_initial, precision)

        rows.append(attack_row)

# add last normal row
rows.append(df_normal.iloc[-1])

# --- Final dataframe ---
df_final = (
    pd.DataFrame(rows)
    .sort_values(time_col)
    .reset_index(drop=True)
)
cols_original = df_final.columns

# drop cols that are all na
df_final = df_final.dropna(axis='columns', how='all')
cols_kept = df_final.columns
print(f'Dropping {len(cols_original)-len(cols_kept)} columns: {set_difference(cols_original, cols_kept)}')

# drop records with na in key_col
n_na = df_final[time_col].isna().sum()
print(f'{n_na} records with NaN in {time_col}.')
df_final = df_final.dropna(axis='rows', subset=[time_col])

df_final.to_csv(processed_dir_path / 'processed.csv', index=False)