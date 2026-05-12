# MLops Pipeline for Predicting Cyberattacks against an IoT Network

## 🚀 Overview

This project implements an end-to-end MLOps pipeline for anomaly and attack detection in MQTT-based IoT network traffic. 
The pipeline processes raw packet captures exported from Wireshark, validates dataset quality using Great Expectations, 
trains machine learning models for network intrusion detection, and supports fully reproducible execution using Docker.

Repository Structure:

```md
├── config.yaml
├── Dockerfile
├── notebooks
│   ├── model_training.ipynb
│   ├── msg_freq_validation.ipynb
│   └── pre-training_analysis.ipynb
├── requirements.txt
├── run_pipeline.sh
└── src
    ├── config_loader.py
    ├── data
    │   ├── download_zenodo.py
    │   └── load_data.py
    ├── models
    │   └── train_model.py
    ├── pre-process_data.py
    ├── tests
    │   └── pre-training-test.py
    ├── train.py
    └── utils.py
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

tbd

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