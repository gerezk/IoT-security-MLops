from pathlib import Path
import mlflow
from pydantic import BaseModel
from typing import TypeVar

from iot_security_mlops.config_loader import load_config


T = TypeVar("T", bound=BaseModel)


def initialize_flow_environment(root: Path, config_name: str, model: type[T]) -> tuple[Path, T, Path, Path]:
    """
    Loads config and initializes MLflow tracking.
    :param root: Path to the project root.
    :param config_name: Full config file name in configs dir.
    :param model: config model to use.
    :return: tuple
        (abs_config_path, config, artifact_dir, db_path)
    """

    config_path = root / "configs" / config_name
    if not config_path.exists():
        raise FileNotFoundError(f"Config file {config_path} not found")
    config = load_config(config_path, model)

    tracking_dir = root / config.paths.mlflow_dir
    artifact_dir = tracking_dir / "artifacts"

    artifact_dir.mkdir(parents=True, exist_ok=True)

    db_path = tracking_dir / "mlflow.db"

    mlflow.set_tracking_uri(f"sqlite:///{db_path}")

    return config_path, config, artifact_dir, db_path

def pull_model(db_path: str, experiment_name: str, config_version: str) -> str:
    """
    Gets random forest model from most recent MLflow run_id for given experiment name and config version.
    :param experiment_name: Experiment name.
    :param config_version: Config version (without .yaml).
    :return: sklearn random forest model
    """

    mlflow.set_tracking_uri(f"sqlite:///{db_path}")
    mlflow.set_experiment(experiment_name)

    runs = mlflow.search_runs(
        experiment_names=[experiment_name],
        filter_string=f"tags.config_version = '{config_version}'",
        order_by=["start_time DESC"]
    )

    if len(runs) == 0:
        raise RuntimeError(f"No MLflow runs found for experiment '{experiment_name}, "
                           f"version {config_version}.'")

    run_id = runs.iloc[0].run_id

    model_uri = f"runs:/{run_id}/random_forest"

    return mlflow.sklearn.load_model(model_uri)