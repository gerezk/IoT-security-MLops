from pathlib import Path
from pydantic import BaseModel, Field, model_validator
import yaml
from typing import Optional, Literal

from iot_security_mlops.utils_core import find_repo_root


class PathConfig(BaseModel):
    train_data: Path
    deployment_data: Path

    test_results_dir: Path
    model_dir: Path

    @model_validator(mode="after")
    def validate_paths(self):
        # validate files exist
        base_dir = find_repo_root()

        if not (base_dir / self.train_data).exists():
            raise FileNotFoundError(
                f"Train data does not exist: {self.train_data}"
            )
        if not (base_dir / self.deployment_data).exists():
            raise FileNotFoundError(
                f"Deployment does not exist: {self.deployment_data}"
            )

        # create output dirs automatically
        (base_dir / self.test_results_dir).mkdir(parents=True, exist_ok=True)
        (base_dir / self.model_dir).mkdir(parents=True, exist_ok=True)

        return self


class TrainConfig(BaseModel):
    n_estimators: int = Field(gt=0)
    criterion: Literal["gini", "entropy", "log_loss"]
    max_depth: Optional[int] = None
    min_samples_split: int
    min_samples_leaf: int
    random_state: int = 42


# --- Top-level config model ---
class Config(BaseModel):
    paths: PathConfig
    train: TrainConfig


def load_config(config_file: Path) -> Config:
    """
    Load config from yaml file.
    :param config_file: absoluet path to the config file
    :return: Config object
    """
    with open(config_file, "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    config = Config(**data)

    return config