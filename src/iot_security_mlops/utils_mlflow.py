from pathlib import Path
import mlflow

from iot_security_mlops.config_loader import load_config, Config


def initialize_flow_environment(root: Path) -> tuple[Path, Config, Path, Path]:
    """
    Loads config and initializes MLflow tracking.
    :param root: Path to the project root.
    :return: tuple
        (config_path, config, artifact_dir, db_path)
    """

    config_path = root / "config.yaml"
    config = load_config(config_path)

    tracking_dir = root / config.paths.mlflow_dir
    artifact_dir = tracking_dir / "artifacts"

    artifact_dir.mkdir(parents=True, exist_ok=True)

    db_path = tracking_dir / "mlflow.db"

    mlflow.set_tracking_uri(f"sqlite:///{db_path}")

    return config_path, config, artifact_dir, db_path