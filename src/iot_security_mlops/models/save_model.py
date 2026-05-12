from pathlib import Path
import skops.io as sio

from src.iot_security_mlops.utils import find_repo_root


def save_model(model, rel_path: Path) -> None:
    """
    Saves a trained model to the given path
    :param model:
    :param rel_path: relative path from project root to save the model to.
    :return: None
    """
    full_path = find_repo_root() / rel_path

    sio.dump(model, full_path)