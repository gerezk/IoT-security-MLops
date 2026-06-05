import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from metaflow import FlowSpec, step, pypi
from iot_security_mlops.utils_core import load_requirements


class MonitoringFlow(FlowSpec):
    # metaflow breaks with custom __init__

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/start.txt')
    )
    @step
    def start(self):

        import mlflow
        from iot_security_mlops.utils_mlflow import initialize_flow_environment


        (
            self.config_path,
            self.config,
            self.tracking_dir,
            self.db_path,
        ) = initialize_flow_environment(ROOT)

        self.experiment_name = "drift_tests"
        mlflow.set_experiment(self.experiment_name)

        self.next(self.detect_drift)

    @pypi(
        python='3.11',
        packages=load_requirements(ROOT / 'requirements/drift_tests.txt')
    )
    @step
    def detect_drift(self):

        import mlflow
        import json

        from iot_security_mlops.data.load_data import load_data
        from iot_security_mlops.tests.drift_detection import run_msg_freq_drift_detection
        from iot_security_mlops.utils_data import df_all_sensor_msg_freq


        reference, _ = load_data(self.config.paths.train_data, False, False)
        deployment, _ = load_data(self.config.paths.deployment_data, False, False)

        reference_msg_freq = df_all_sensor_msg_freq(reference, 3.0)
        deployment_msg_freq = df_all_sensor_msg_freq(deployment, 3.0)

        # first packet for a sensor will always have nan for msg_freq
        reference_msg_freq = reference_msg_freq.dropna(subset=["msg_freq"])
        deployment_msg_freq = deployment_msg_freq.dropna(subset=["msg_freq"])

        if self.config.drift.inject_drift:
            # double message frequency for the given sensor
            deployment_msg_freq.loc[deployment_msg_freq['ip.src'] == self.config.drift.sensor_ip, 'msg_freq'] *= 2

        mlflow.set_tracking_uri(f"sqlite:///{self.db_path}")
        mlflow.set_experiment(self.experiment_name)

        with mlflow.start_run():
            mlflow.log_artifact(str(self.config_path), artifact_path="config")

            msg_freq_drift_results = run_msg_freq_drift_detection(
                reference_df=reference_msg_freq,
                current_df=deployment_msg_freq,
                alpha=self.config.drift.alpha,
            )

            # log sensor metrics to MLflow
            for ip in msg_freq_drift_results["ips"].keys():
                ip_results = msg_freq_drift_results["ips"][ip]

                mlflow.log_metric(f"{ip}_ks_statistic", ip_results["ks_statistic"])
                mlflow.log_metric(f"{ip}_p_value", ip_results["p_value"])
                mlflow.log_metric(f"{ip}_drift_detected", ip_results["drift_detected"])

            # log overall monitoring metrics
            mlflow.set_tag("feature_tested", "Messaging frequency")
            mlflow.set_tag("drift_test", "Kolmogorov-Smirnov")
            mlflow.set_tag("monitoring_status", msg_freq_drift_results["monitoring_status"])
            mlflow.log_metric("total_ips", msg_freq_drift_results["total_ips"])
            mlflow.log_metric("drifted_ips", msg_freq_drift_results["drifted_ips"])

            drift_report_path = self.config.paths.test_results_dir / "msg_freq_drift_report.json"
            with open(drift_report_path, "w") as f:
                json.dump(msg_freq_drift_results, f, indent=2)

            mlflow.log_artifact(str(drift_report_path), artifact_path="monitoring_reports")

        self.next(self.end)

    @step
    def end(self):
        print("Pipeline complete")

if __name__ == "__main__":
    MonitoringFlow()