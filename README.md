# MLops Pipeline for Predicting Cyberattacks against an IoT Network

## 📌 TL;DR

tbw

## 🚀 Overview

tbw

## ✅ Testing 

### Pre-training Tests

Some assumptions must be made that may not be applicable during an actual 
deployed scenario due to limitations on how the data was collected.
Validation rules are derived from these assumptions.

The following columns must not be null:
1. **frame.***: comes from the capture itself in Wireshark and should never be null in a valid export.
2. **ip.***: assumption that all packets have an IPv4 layer.
3. **tcp.***: assumption that the IP protocol in a packet's IPv4 header is TCP. 
Exception, tcp.analysis.initial_rtt is NOT included in this rule.

The following columns must adhere to some distribution:
1. **tcp.dstport** must be an int ranging from 0 to 65535 (inclusive): TCP destination port numbers are 16-bit 
unsigned integers ranging from 0 to 65535.
2. **ip.src** and **ip.dst** must be a member of the set {10.16.100.73, 10.16.120.44, 10.16.120.72, 192.168.0.151, 
192.168.0.150, 192.168.0.152, 192.168.0.154, 192.168.0.155, 192.168.0.180, 192.168.0.173, 192.168.0.176, 192.168.0.178, 
192.168.0.174, 192.168.1.90, 192.168.1.91, 192.168.1.100}, which contains the IP addresses of all devices used for 
data collection.

### Pre-deployment Tests

tbd

### Post-deployment Tests

tbd

## 🛠️ Tech Stack
- Python (3.12)
- Testing
  - Great Expectations
- Data Processing
  - pandas
  - NumPy
- Machine learning
  - tbd

## ▶️ How to Run

### Docker 

tbd

### Virtual Environment

tbd

## ℹ️ Sources

The dataset in the project is based on the MQTTset. The goal of the dataset creators 
was to provide a dataset for a realistic IoT configuration based on the MQTT 
communication protocol, which is a network protocol specifically used in IoT contexts.

The full dataset is on [Kaggle](https://www.kaggle.com/datasets/cnrieiit/mqttset). 
More information can be found in the paper 
([DOI: 10.3390/s20226578](https://doi.org/10.3390/s20226578)).