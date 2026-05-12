"""
Split legitimate_1w.csv into three files:
    reference.csv - a slice of normal packets at the beginning that will be used to derive tests
    training.csv - a slice of mixed packets after reference.csv that will be used to train the model
    post-deployment.csv - a slice of mixed packets after training.csv that will be used for post-deployment testing
"""

import pandas as pd
import numpy.random as np
from typing import Dict

from iot_security_mlops.utils_core import find_repo_root


def randomly_inject_attacks(normal_df: pd.DataFrame,
                            attack_dfs: Dict[str, pd.DataFrame],
                            rng: np.Generator) -> pd.DataFrame:
    """
    Inject attacks in between normal packets with a probability of 5%.
    :param normal_df: df of normal packets
    :param attack_dfs: dict with attack_type: attack_df pairs
    :param rng: np.random Generator object
    :return: normal_df with attacks injected between normal packets
    """
    time_col = 'frame.time_epoch'
    precision = 6  # for rounding floats
    min_gap_size = 1e-6  # in seconds
    attack_prob = 0.05

    attack_types = list(attack_dfs.keys())
    # shuffle each attack dataframe once
    attack_pools = {
        k: v.sample(frac=1, random_state=rng).reset_index(drop=True)
        for k, v in attack_dfs.items()
    }
    attack_indices = {k: 0 for k in attack_types}
    t_initial = normal_df.iloc[0][time_col]
    rows = []
    for i in range(len(normal_df) - 1):
        current = normal_df.iloc[i]
        next_row = normal_df.iloc[i + 1]

        rows.append(current)

        t_start = current[time_col]
        t_end = next_row[time_col]
        gap = t_end - t_start

        # decide whether to inject
        if gap > min_gap_size and rng.random() < attack_prob:
            # sample attack type uniformly
            attack_type = rng.choice(attack_types)

            # get next row from that attack type
            idx = attack_indices[attack_type]
            attack_df = attack_pools[attack_type]

            attack_row = attack_df.iloc[idx % len(attack_df)].copy()
            attack_indices[attack_type] += 1

            # assign synthetic timestamp inside gap
            t_new = round(t_start + rng.random() * gap, precision)
            attack_row['frame.time_delta'] = round(t_new - t_start, precision)
            attack_row['frame.time_delta_displayed'] = attack_row['frame.time_delta']
            attack_row[time_col] = t_new
            attack_row['class'] = attack_type
            attack_row['frame.time_relative'] = round(t_new - t_initial, precision)

            rows.append(attack_row)
    # add last normal row
    rows.append(normal_df.iloc[-1])
    df_final = (
        pd.DataFrame(rows)
        .reset_index(drop=True)
    )

    return df_final


root = find_repo_root()
raw_dir_path = root / 'data/raw' # must exist
processed_data_dir = root / 'data/processed'
processed_data_dir.mkdir(exist_ok=True, parents=True)
specify_col_dtype = {'mqtt.clientid': str,
                     'mqtt.conack.flags': str,
                     'mqtt.conflags': str,
                     'mqtt.msg': str,
                     'mqtt.protoname': str}
df_normal = pd.read_csv(raw_dir_path / 'legitimate_1w.csv', dtype=specify_col_dtype)

# --- create reference.csv ---
# first 100k normal packets
df_ref = df_normal.iloc[:100_000].copy()
df_ref['class'] = 'legitimate'
df_ref.to_csv(processed_data_dir / 'reference.csv', index=False)

# --- load attack csv files ---
dfs_attack = {}
for file in raw_dir_path.iterdir():
    filename = file.name.split('.')[0]
    packet_class = filename.split('_')[0]

    if file.suffix == '.csv':
        if packet_class != 'legitimate':
            df = pd.read_csv(file, dtype=specify_col_dtype)
            df['class'] = packet_class
            dfs_attack[packet_class] = df

df_end = df_normal.iloc[-200_000:].copy() # take last 200k normal packets
df_end['class'] = 'legitimate'
rng_training = np.default_rng(1)
# --- create train.csv ---
# first half of df_end, take 80%, then randomly inject attack packets
df_train = df_end.iloc[0:80_000]
df_train = randomly_inject_attacks(df_train, dfs_attack, rng_training)
df_train.to_csv(processed_data_dir / 'train.csv', index=False)

# --- create test.csv ---
# first half of df_end, take last 20%, then randomly inject attack packets
df_test = df_end.iloc[80_000:100_000]
df_test = randomly_inject_attacks(df_test, dfs_attack, rng_training)
df_test.to_csv(processed_data_dir / 'test.csv', index=False)

# --- create post-deployment.csv ---
# second half of df_end then randomly inject attack packets
df_post_deploy = df_end.iloc[100_000:]
rng_deploy = np.default_rng(2)
df_post_deploy = randomly_inject_attacks(df_post_deploy, dfs_attack, rng_deploy)
df_post_deploy.to_csv(processed_data_dir / 'post-deployment.csv', index=False)