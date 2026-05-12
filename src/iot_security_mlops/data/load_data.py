import pandas as pd
from pathlib import Path
from typing import Tuple

from iot_security_mlops.utils_core import find_repo_root


def drop_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns from processed data according to recommendations from the Kaggle page:
    https://www.kaggle.com/datasets/cnrieiit/mqttset.
    :param df: processed data
    :return: df with unneeded columns dropped
    """

    names = ['frame.time_invalid', 'frame.time_epoch', 'frame.time_relative', 'frame.number', 'frame.time_delta',
    'frame.time_delta_displayed', 'frame.cap_len', 'frame.len', 'tcp.window_size_value', 'eth.src', 'eth.dst', 'ip.src',
    'ip.dst', 'ip.proto', 'tcp.srcport', 'tcp.dstport', 'tcp.analysis.initial_rtt', 'tcp.stream', 'mqtt.topic',
    'tcp.checksum', 'mqtt.topic_len', 'mqtt.passwd_len', 'mqtt.passwd', 'mqtt.clientid', 'mqtt.clientid_len',
    'mqtt.username', 'mqtt.username_len']

    df_copy = df.copy()
    df_copy = df_copy.drop(names, axis=1)

    return df_copy


def load_training_data(path: Path) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Load training data and encode categorical columns.
    :param path: relative path to training data from project root
    :return: x, y
    """
    data_file = find_repo_root() / path
    df = pd.read_csv(data_file)
    df = drop_cols(df)

    # encode categorical columns
    df = df.astype('category')
    cat_columns = df.select_dtypes(['category']).columns
    df[cat_columns] = df[cat_columns].apply(lambda z: z.cat.codes)

    x = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    return x, y