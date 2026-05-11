from config_loader import load_config
from pathlib import Path


def main(config_file):
    config = load_config(config_file)

if __name__ == '__main__':
    config_path = Path(__file__).resolve().parents[1] / 'config.yaml'
    main(config_path)