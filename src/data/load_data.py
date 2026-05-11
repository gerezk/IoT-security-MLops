import pandas as pd
from sklearn.model_selection import train_test_split
from typing import Tuple

from src.utils import find_repo_root
from src.config_loader import Config


def drop_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns from processed data according to recommendations from the original paper.
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


def load_training_data(config: Config) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create training and testing data from train.csv using random shuffling.
    :param config: Config object
    :return: X_train, X_test, y_train, y_test
    """
    data_file = find_repo_root() / config.paths.train_data
    df = pd.read_csv(data_file)
    df = drop_cols(df)

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        test_size=config.train.test_size,
                                                        random_state=config.train.random_state)

    return X_train, X_test, y_train, y_test