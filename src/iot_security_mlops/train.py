from config_loader import load_config

from iot_security_mlops.utils_core import find_repo_root
from iot_security_mlops.data.load_data import load_training_data
from iot_security_mlops.models.train_model import train_random_forest
from iot_security_mlops.models.save_model import save_model


def main(config_file):
    config = load_config(config_file)

    x_train, y_train = load_training_data(config.paths.train_data)

    model = train_random_forest(x_train, y_train, config.train)

    save_model(model, config.paths.model_dir / 'random_forest.skops')

if __name__ == '__main__':
    config_path = find_repo_root() / 'config.yaml'
    main(config_path)