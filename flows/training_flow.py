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
        import mlflow

        from iot_security_mlops.data.load_data import load_training_data
        from iot_security_mlops.models.train_model import train_random_forest


        # set up directories and db for dumping mlflow outputs
        tracking_dir = ROOT / self.config.paths.mlflow_dir
        tracking_dir.mkdir(parents=True, exist_ok=True)

        artifact_dir = tracking_dir / "artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)

        db_path = tracking_dir / "mlflow.db"

        mlflow.set_tracking_uri(f"sqlite:///{db_path}")

        experiment = mlflow.get_experiment_by_name("iot-security-rf")
        if experiment is None:
            mlflow.create_experiment(
                name="iot-security-rf",
                artifact_location=artifact_dir.resolve().as_uri()
            )

        mlflow.set_experiment(
            experiment_name="iot-security-rf"
        )

        with mlflow.start_run():
            x_train, y_train = load_training_data(self.config.paths.train_data)

            model = train_random_forest(x_train, y_train, self.config.train)

            mlflow.sklearn.log_model(
                sk_model=model,
                name="random_forest",
                serialization_format="skops"
            )

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