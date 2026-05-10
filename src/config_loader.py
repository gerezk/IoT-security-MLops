from pathlib import Path
from pydantic import BaseModel, Field, model_validator
import yaml


class TrainConfig(BaseModel):
    n_estimators: int = Field(gt=0)
    random_state: int = 42
    data_path: Path
    model_path: Path

    @model_validator(mode="after")
    def validate_paths(self):
        # validate training data exists
        base_dir = Path(__file__).resolve().parents[1]

        if not (base_dir / self.data_path).exists():
            raise FileNotFoundError(
                f"Data path does not exist: {self.data_path}"
            )

        # create model output directory automatically
        (base_dir / self.model_path).parent.mkdir(parents=True, exist_ok=True)

        return self


# --- Top-level config model ---
class Config(BaseModel):
    train_config: TrainConfig
   # eval_config: TestConfig

def load_config(config_file: Path) -> Config:
    """
    Load config from yaml file.
    :param config_file: relative path from project root to config file
    :return: Config object
    """
    with open(config_file, "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    config = Config(**data)

    return config