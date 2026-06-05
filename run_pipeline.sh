#!/bin/bash

python -m flows.training_flow --environment=pypi run --config train_baseline_v1.yaml
python -m flows.training_flow --environment=pypi run --config train_more_trees_v1.yaml

python -m flows.monitoring_flow --environment=pypi run --config monitor_inject_drift_v1.yaml

python -m flows.ab_test_flow --environment=pypi run --config ab_test_v1.yaml