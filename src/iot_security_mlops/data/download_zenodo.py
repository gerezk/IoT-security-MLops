import urllib.request

from src.iot_security_mlops.utils import find_repo_root


BASE_URL = "https://doi.org/10.5281/zenodo.20126302"

FILES = [
    "training.csv",
    "reference.csv",
    "post-deployment.csv",
]

def download():
    base_dir = find_repo_root()
    data_dir = base_dir / "data/processed"
    data_dir.mkdir(parents=True, exist_ok=True)

    for file_name in FILES:
        url = f"{BASE_URL}/{file_name}"
        output_path = data_dir / file_name

        if not output_path.exists():
            print(f"Downloading {file_name}...")
            urllib.request.urlretrieve(url, output_path)
        else:
            print(f"{file_name} already exists, skipping.")

if __name__ == "__main__":
    download()