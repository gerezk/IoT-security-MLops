import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from metaflow import FlowSpec, step, pypi
from iot_security_mlops.utils_core import load_requirements


class IoTSecurityFlow(FlowSpec):

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/start.txt')
    )
    @step
    def start(self):

        from iot_security_mlops.config_loader import load_config

        config_path = ROOT / "config.yaml"
        self.config = load_config(config_path)

        self.next(self.pre_training_tests)

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/pre_training_tests.txt')
    )
    @step
    def pre_training_tests(self):

        from iot_security_mlops.tests.pre_training_tests import run_pre_train_tests

        run_pre_train_tests(self.config)

        self.next(self.train)

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/training.txt')
    )
    @step
    def train(self):

        from iot_security_mlops.data.load_data import load_training_data
        from iot_security_mlops.models.train_model import train_random_forest
        from iot_security_mlops.models.save_model import save_model

        x_train, y_train = load_training_data(self.config.paths.train_data)

        model = train_random_forest(x_train, y_train, self.config.train)

        save_model(model, self.config.paths.model_dir / 'random_forest.skops')

        self.next(self.end)
      #  self.next(self.robustness)

    # @docker(image="iot-robustness:latest")
    # @step
    # def robustness(self):
    #
    #     from src.validation.robustness_validation import validate_model
    #
    #     validate_model(self.model_path)
    #
    #     self.next(self.end)

    @step
    def end(self):
        print("Pipeline complete")

if __name__ == "__main__":
    IoTSecurityFlow()