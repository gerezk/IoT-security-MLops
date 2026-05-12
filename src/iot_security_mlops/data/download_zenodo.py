import requests

from iot_security_mlops.utils_core import find_repo_root


DOI = "10.5281/zenodo.19663451"

FILES = [
    "train.csv",
    "test.csv",
    "reference.csv",
    "post-deployment.csv",
]


def get_latest_record_metadata(doi: str) -> dict:
    """
    Resolve DOI and return Zenodo record metadata.
    """
    doi_url = f"https://doi.org/{doi}"

    # Zenodo redirects DOI -> latest record page
    response = requests.get(doi_url, allow_redirects=True)
    response.raise_for_status()

    # Example final URL:
    # https://zenodo.org/records/19663451
    final_url = response.url

    record_id = final_url.rstrip("/").split("/")[-1]

    api_url = f"https://zenodo.org/api/records/{record_id}"

    api_response = requests.get(api_url)
    api_response.raise_for_status()

    return api_response.json()


def build_file_url_map(metadata: dict) -> dict:
    """
    Build mapping: filename -> direct download URL
    """
    file_map = {}

    for file_info in metadata["files"]:
        filename = file_info["key"]

        # direct download URL
        url = file_info["links"]["self"]

        file_map[filename] = url

    return file_map


def download():
    base_dir = find_repo_root()
    data_dir = base_dir / "data/processed"
    data_dir.mkdir(parents=True, exist_ok=True)

    metadata = get_latest_record_metadata(DOI)
    file_urls = build_file_url_map(metadata)

    for file_name in FILES:
        if file_name not in file_urls:
            print(f"{file_name} not found in Zenodo record")
            continue

        output_path = data_dir / file_name

        if output_path.exists():
            print(f"{file_name} already exists, skipping.")
            continue

        print(f"Downloading {file_name}...")

        response = requests.get(file_urls[file_name], stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Saved to {output_path}")

if __name__ == "__main__":
    download()