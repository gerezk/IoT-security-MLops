from pathlib import Path
from pydantic import BaseModel, Field, model_validator
import yaml
from typing import Optional, Literal, TypeVar

from iot_security_mlops.utils.utils_core import find_repo_root
REPO_ROOT = find_repo_root()


class PathConfig(BaseModel):
    train_data: Path
    test_data: Path
    deployment_data: Path

    test_results_dir: Path
    mlflow_dir: Path

    @model_validator(mode="after")
    def validate_paths(self):
        # validate files exist
        if not (REPO_ROOT / self.train_data).exists():
            raise FileNotFoundError(
                f"Train data does not exist: {self.train_data}"
            )
        if not (REPO_ROOT / self.test_data).exists():
            raise FileNotFoundError(
                f"Test data does not exist: {self.test_data}"
            )
        if not (REPO_ROOT / self.deployment_data).exists():
            raise FileNotFoundError(
                f"Post-deployment data does not exist: {self.deployment_data}"
            )
        return self

    def create_output_dirs(self):
        (REPO_ROOT / self.test_results_dir).mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / self.mlflow_dir).mkdir(parents=True, exist_ok=True)


class TrainConfig(BaseModel):
    n_estimators: int = Field(gt=0)
    criterion: Literal["gini", "entropy", "log_loss"]
    max_depth: Optional[int] = None
    min_samples_split: int = Field(ge=2)
    min_samples_leaf: int = Field(ge=1)
    random_state: int = 42

    min_samples: int = Field(gt=0)
    use_subset: bool = False


class DriftTestsConfig(BaseModel):
    inject_drift: bool = False
    sensor_ip: str
    alpha: float = Field(gt=0, lt=1)


class ConfigVersions(BaseModel):
    a: str
    b: str

# --- Shared config ---
class BaseFlowConfig(BaseModel):
    paths: PathConfig

# --- Top-level flow config models ---
class TrainingFlowConfig(BaseFlowConfig):
    train: TrainConfig

class MonitoringFlowConfig(BaseFlowConfig):
    drift: DriftTestsConfig

class ABTestFlowConfig(BaseFlowConfig):
    config_versions: ConfigVersions


T = TypeVar("T", bound=BaseModel)


def load_config(config_file: Path, model: type[T]) -> T:
    """
    Load config from yaml file.
    :param config_file:
    :param model: one of TrainingFlowConfig, MonitoringFlowConfig,or ABTestFlowConfig
    :return: appropriate config object
    """
    with open(config_file) as f:
        data = yaml.safe_load(f)

    return model(**data)