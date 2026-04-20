from pathlib import Path
import urllib.request

BASE_URL = "https://zenodo.org/records/19663452/files"

FILES = [
    "training.csv",
    "reference.csv",
    "post-deployment.csv",
]

def download():
    base_dir = Path(__file__).resolve().parents[1]
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