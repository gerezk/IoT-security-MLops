# MLops Pipeline for Predicting Cyberattacks against an IoT Network

## 🚀 Overview

This project implements an end-to-end MLOps pipeline for anomaly and attack detection in MQTT-based IoT network traffic. 
The pipeline processes raw packet captures exported from Wireshark, validates dataset quality using Great Expectations, 
trains a <ins>random forest</ins> model for network intrusion detection, and supports fully reproducible execution using Docker.

Repository Structure:

```md
├── config.yaml
├── Dockerfile
├── flows
│   └── training_flow.py
├── notebooks
│   ├── model_training.ipynb
│   ├── msg_freq_validation.ipynb
│   └── pre-training_analysis.ipynb
├── pyproject.toml
├── requirements
│   ├── base.txt
│   ├── post_training_tests.txt
│   ├── pre_training_tests.txt
│   ├── start.txt
│   └── training.txt
└── src
    └── iot_security_mlops
        ├── config_loader.py
        ├── data
        │   ├── download_zenodo.py
        │   └── load_data.py
        ├── models
        │   ├── metrics.py
        │   └── train_model.py
        ├── pre-process_data.py
        ├── tests
        │   └── pre_training_tests.py
        ├── train.py
        ├── utils_core.py
        └── utils_data.py
```

## 📊🔍 Message Frequency Validation

Inconsistencies were identified between documented and observed message frequencies, primarily for sensors labeled as 
random, which should mean that sending is achieved at random periods (*m*), with *m* ≤ *n*, where *n* is the documented
message frequency. All random sensors were assigned an *n* of 3600. This should mean that messages are randomly 
distributed between 0 and 3600 seconds.

Instead, it was found that all random sensors behaved as periodic sensors with
a message frequency of 1 second. Additionally, the light intensity sensor should have pushed a message every 1800
seconds. Instead a frequency of 180 seconds was observed.

This finding does not invalidate the overarching purpose of the dataset, since the 
focus is on the protocol-level features and attack signatures rather than the exact temporal structure. But this is 
still important to note when creating tests for the MLops pipeline.

For details on the analysis, see `../notebooks/msg_freq_validation.ipynb`.

## ✅ Testing

### Pre-training Tests

See `../notebooks/pre-training_analysis.ipynb` for justification of the pre-training tests.
The implementation of the tests can be found in `../src/tests/pre-training-test.py`.

### Pre-deployment Tests

The dataset creators tested several ML models on the MQTT dataset, including random forest. Their random forest scored
a test accuracy of 99.4% and an F1 score of 0.994. However, this dataset is heavily imbalanced; malicious packets only 
make up about 1% of the dataset. The authors showed that using a balanced version with 50% normal packets and 50% 
malicious packets leads to a drop in performance. With the balanced dataset, their random forest achieved a test accuracy 
of 91.6% and an F1 score of 0.914.

The dataset consutrcted for this project consists of about 5% malicious packets. Therefore, <ins>a threshold of 0.95 for both
accuracy and F1 score</ins> will be used for testing model robustness. The notebook `model_training` shows that a default
random forest model achieves a test accuracy of 98.1% and an F1 score of 0.979.

During the training step, an artificial failure scenario was introduced by enforcing a minimum dataset size threshold of 
1000 samples. If the dataset falls below this threshold, the pipeline is aborted to prevent training on insufficient data, 
which could lead to overfitting and unreliable model performance. This design choice reflects a fail-fast strategy where 
invalid or insufficient input data should halt execution early rather than propagate errors into downstream model 
artifacts.

### Post-deployment Tests

tbd

## 🛠️ Tech Stack
- Python (3.11)
- Data Processing
  - pandas
  - NumPy
- Machine learning
  - Scikit-learn
- Orchestration
  - Metaflow
- Versioning
  - mlflow
- Testing
  - Great Expectations

## ▶️ How to Run

### Docker 

Clone repository:

```
gh repo clone gerezk/IoT-security-MLops
cd IoT-security-MLops
```

Open Docker:

```
open -a Docker
```

Build container:

```
docker build --platform=linux/amd64 -t mqtt-mlops .
```

Download data:

```
docker run --platform=linux/amd64 -it \
  -v $(pwd)/data/processed:/app/data/processed \
  mqtt-mlops python src/iot_security_mlops/data/download_zenodo.py
```

Cache micromamba + all pypi envs:
```
docker volume create metaflow-cache
```

Run container:

```
docker run --platform=linux/amd64 -it \
 -v metaflow-cache:/app/.metaflow \
 -v $(pwd)/data:/app/data \
 -v $(pwd)/output:/app/output \
 mqtt-mlops
```

## ℹ️ Sources

The dataset in the project is based on the MQTTset. The goal of the dataset creators 
was to provide a dataset for a realistic IoT configuration based on the MQTT 
communication protocol, which is a network protocol specifically used in IoT contexts.

The full dataset is on [Kaggle](https://www.kaggle.com/datasets/cnrieiit/mqttset). It is licensed under the
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) license.
More information can be found in the paper 
([DOI: 10.3390/s20226578](https://doi.org/10.3390/s20226578)).

The pre-processed datasets can be found at 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19663451.svg)](https://doi.org/10.5281/zenodo.19663451).
These datasets are also licensed under the [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) license.