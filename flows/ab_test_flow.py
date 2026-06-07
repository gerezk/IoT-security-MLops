import sys
from pathlib import Path

from metaflow import FlowSpec, step, pypi, Parameter

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from iot_security_mlops.utils.utils_core import load_requirements


class ABTestFlow(FlowSpec):
    # metaflow breaks with custom __init__
    config_file = Parameter(
        "config",
        help="Full config file name in configs dir",
        required=True,
        type=str,
    )

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/ab_test_flow/start.txt')
    )
    @step
    def start(self):

        import mlflow

        from iot_security_mlops.utils.utils_mlflow import initialize_flow_environment
        from iot_security_mlops.config_loader import ABTestFlowConfig

        self.config_name = self.config_file.split(".")[0]
        (
            self.config_path,
            self.config,
            self.artifact_dir,
            self.db_path,
        ) = initialize_flow_environment(ROOT, self.config_file, ABTestFlowConfig)

        self.experiment_name = "ab_test"
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            mlflow.create_experiment(
                name=self.experiment_name,
                artifact_location=self.artifact_dir.resolve().as_uri()
            )
        mlflow.set_experiment(self.experiment_name)

        self.next(self.load_and_split_data)

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/ab_test_flow/load_and_split_data.txt')
    )
    @step
    def load_and_split_data(self):
        """Assumed that attacker ips are not the same as sensor ips, which applies for the MQTTset."""

        from random import Random
        from sklearn.model_selection import train_test_split

        from iot_security_mlops.data.load_data import load_data


        # --- split sensor ips ---
        rng = Random(self.config.AB_test.seed)

        # shuffle list of ips
        ips = rng.sample(
            self.config.AB_test.sensor_ips,
            len(self.config.AB_test.sensor_ips)
        )

        mid = len(ips) // 2
        group_a_ips = ips[:mid]
        group_b_ips = ips[mid:]

        # --- get sensor packet indices based on split ---
        deployment, y = load_data(self.config.paths.deployment_data, False, False)
        deployment["class"] = y

        a_sensor_idx = deployment.index[
            deployment["ip.src"].isin(group_a_ips)
            |
            deployment["ip.dst"].isin(group_a_ips)
        ]
        b_sensor_idx = deployment.index[
            deployment["ip.src"].isin(group_b_ips)
            |
            deployment["ip.dst"].isin(group_b_ips)
        ]

        # --- collect malicious packets ---
        malicious_df = deployment[
            deployment["class"] != "legitimate"
            ]

        # --- random stratified split of malicious packets ---
        a_mal_idx, b_mal_idx = train_test_split(
            malicious_df.index,
            test_size=0.5,
            random_state=self.config.AB_test.seed,
            stratify=malicious_df["class"],
        )

        # --- join indices ---
        a_idx = a_sensor_idx.union(a_mal_idx)
        b_idx = b_sensor_idx.union(b_mal_idx)

        self.a_idx = a_idx
        self.b_idx = b_idx

        self.next(self.predict_a, self.predict_b)

    # ---------------
    # A/B branch
    # ---------------

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/ab_test_flow/ab_predict.txt')
    )
    @step
    def predict_a(self):

        from iot_security_mlops.utils.utils_mlflow import pull_model
        from iot_security_mlops.data.load_data import load_data
        from iot_security_mlops.models.metrics import evaluate_model


        config_version = self.config.AB_test.config_versions.b
        model = pull_model(self.db_path, self.config.AB_test.experiment_name, config_version)

        x, y = load_data(self.config.paths.deployment_data, True, True)

        x = x.iloc[self.a_idx, :]
        y = y[self.a_idx]

        self.acc, self.f1 = evaluate_model(model, x, y)

        self.next(self.join)

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/ab_test_flow/ab_predict.txt')
    )
    @step
    def predict_b(self):

        from iot_security_mlops.utils.utils_mlflow import pull_model
        from iot_security_mlops.data.load_data import load_data
        from iot_security_mlops.models.metrics import evaluate_model


        config_version = self.config.AB_test.config_versions.b
        model = pull_model(self.db_path, self.config.AB_test.experiment_name, config_version)

        x, y = load_data(self.config.paths.deployment_data, True, True)

        x = x.iloc[self.b_idx, :]
        y = y[self.b_idx]

        self.acc, self.f1 = evaluate_model(model, x, y)

        self.next(self.join)

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/ab_test_flow/join.txt')
    )
    @step
    def join(self, inputs):

        self.next(self.end)

    @step
    def end(self):
        print("Pipeline complete")

if __name__ == "__main__":
    ABTestFlow()