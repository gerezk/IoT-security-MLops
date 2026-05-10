from config_loader import load_config
from pathlib import Path
import argparse

def main(args):
    base_dir = Path(__file__).resolve().parents[1]
    config = load_config(base_dir / "config.yaml")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--train-path", type=str)
    parser.add_argument("--model-output", type=str)

    args = parser.parse_args()

    main(args)