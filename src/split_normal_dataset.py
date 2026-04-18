"""
Split legitimate_1w.csv into three files:
    reference.csv - a slice of packets at the beginning that will be used to derive tests
    training.csv - a slice of packets after reference.csv that will be used to train the model
    post-deployment.csv - a slice of packets after training.csv that will be used for post-deployment testing
"""

import pandas as pd
from pathlib import Path


raw_data_path = Path('../data/raw/legitimate_1w.csv') # must exist
processed_data_dir = Path('../data/processed')
processed_data_dir.mkdir(exist_ok=True, parents=True)
df = pd.read_csv(raw_data_path)

# create reference.csv (first 100k packets)
df_ref = df.iloc[:100_000]
df_ref.to_csv(processed_data_dir / 'reference.csv', index=False)

df_end = df.iloc[-500_000:] # take last 500k packets
# create training.csv (first half of df_end)
df_train = df.iloc[0:250_000]
df_train.to_csv(processed_data_dir / 'training.csv', index=False)

# create post-deployment.csv (2nd half of df_end)
df_post_deploy = df_end.iloc[250_000:]
df_post_deploy.to_csv(processed_data_dir / 'post-deployment.csv', index=False)