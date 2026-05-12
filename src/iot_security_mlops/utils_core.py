from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """
    Find the root of the repository. Files pyproject.toml or .git assumed to be at the repo root.
    :param start: the path to start from, defaults to the current working directory
    :return: path to the root of the repository
    """
    start = start or Path(__file__).resolve()

    for parent in [start] + list(start.parents):
        if (parent / ".git").exists():
            return parent
        if (parent / "pyproject.toml").exists():
            return parent

    raise RuntimeError("Could not find repository root")


def load_requirements(path: Path) -> dict:
    """
    Load requirements from a conventionally formatted .txt file and convert it to a dict.
    :param path: absolute path to requirements file
    :return: dict of requirements
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"File {path} not found")

    packages = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            name, version = line.split("==")
            packages[name] = version

    return packages