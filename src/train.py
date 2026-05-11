from config_loader import load_config
from pathlib import Path

from src.utils import find_repo_root
from src.data.load_data import load_training_data


def main(config_file):
    config = load_config(config_file)

    X_train, X_test, y_train, y_test = load_training_data(config)

if __name__ == '__main__':
    config_path = find_repo_root() / 'config.yaml'
    main(config_path)