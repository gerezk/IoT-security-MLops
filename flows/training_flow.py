import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from metaflow import FlowSpec, step, pypi, Parameter
from iot_security_mlops.utils.utils_core import load_requirements


class IoTSecurityFlow(FlowSpec):
    # metaflow breaks with custom __init__
    config_name = Parameter(
        "config",
        help="Full config file name in configs dir",
        required=True,
        type=str,
    )

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/start.txt')
    )
    @step
    def start(self):

        import mlflow

        from iot_security_mlops.utils.utils_mlflow import initialize_flow_environment

        (
            self.config_path,
            self.config,
            self.artifact_dir,
            self.db_path,
        ) = initialize_flow_environment(ROOT, self.config_name)

        self.experiment_name = "iot_security_mlops"
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            mlflow.create_experiment(
                name=self.experiment_name,
                artifact_location=self.artifact_dir.resolve().as_uri()
            )
        mlflow.set_experiment(self.experiment_name)

        mlflow.log_artifact(str(self.config_path))
        mlflow.set_tag("config_version", self.config_name)

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
        from iot_security_mlops.data.load_data import load_data
        from iot_security_mlops.models.train_model import train_random_forest


        mlflow.set_tracking_uri(f"sqlite:///{self.db_path}")
        mlflow.set_experiment(self.experiment_name)
        with mlflow.start_run() as run:
            x_train, y_train = load_data(self.config.paths.train_data)

            # artificially induce train smaller than required train set size
            if self.config.train.use_subset:
                x_train = x_train.sample(max(1, self.config.train.min_samples - 5))
                y_train = y_train.loc[x_train.index]

            if len(x_train) < self.config.train.min_samples:
                mlflow.set_tag("status", "failed")
                mlflow.set_tag("failure_reason", "insufficient_data")
                raise RuntimeError(f"Training aborted: too few samples ({len(x_train)})")

            model = train_random_forest(x_train, y_train, self.config.train)

            mlflow.sklearn.log_model(
                sk_model=model,
                name="random_forest",
                serialization_format="skops"
            )

            mlflow.log_params({
                "model_type": "RandomForestClassifier",
                "n_estimators": self.config.train.n_estimators,
                'criterion': self.config.train.criterion,
                "max_depth": self.config.train.max_depth,
                "min_samples_split": self.config.train.min_samples_split,
                "min_samples_leaf": self.config.train.min_samples_leaf,
                "random_state": self.config.train.random_state,

                "min_samples": self.config.train.min_samples,
                "use_subset": self.config.train.use_subset
            })

            self.run_id = run.info.run_id

        self.next(self.post_training_tests)

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/post_training_tests.txt')
    )
    @step
    def post_training_tests(self):

        import mlflow
        from iot_security_mlops.models.metrics import evaluate_model
        from iot_security_mlops.data.load_data import load_data


        mlflow.set_tracking_uri(f"sqlite:///{self.db_path}")
        mlflow.set_experiment(self.experiment_name)

        model_uri = f"runs:/{self.run_id}/random_forest"

        model = mlflow.sklearn.load_model(model_uri)

        x_test, y_test = load_data(self.config.paths.test_data)
        acc, f1 = evaluate_model(model, x_test, y_test)

        mlflow.log_metrics({
            "accuracy": acc,
            "f1_score": f1,
        })

        if acc < 0.95 or f1 < 0.95:
            mlflow.set_tag("status", "rejected")
            mlflow.set_tag("rejection_reason", "performance_below_threshold")
            raise RuntimeError("Model failed quality gate during evaluation.")
        else:
            mlflow.set_tag("status", "approved")

        self.next(self.end)

    @step
    def end(self):
        print("Pipeline complete")

if __name__ == "__main__":
    IoTSecurityFlow()