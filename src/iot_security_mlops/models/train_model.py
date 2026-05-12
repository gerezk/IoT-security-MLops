from sklearn.ensemble import RandomForestClassifier
import pandas as pd

from iot_security_mlops.config_loader import TrainConfig


def train_random_forest(x_train: pd.DataFrame, y_train: pd.Series, config: TrainConfig) -> RandomForestClassifier:
    """
    Train a random forest classifier using sklearn Random ForestClassifier based on the config given.
    :param x_train: from load_training_data()
    :param y_train: from load_training_data()
    :param config: TrainConfig object
    :return: RandomForestClassifier
    """

    classifier = RandomForestClassifier(
        criterion=config.criterion,
        max_depth=config.max_depth,
        min_samples_split=config.min_samples_split,
        min_samples_leaf=config.min_samples_leaf,
        random_state=config.random_state
    )

    classifier.fit(x_train, y_train)

    return classifier