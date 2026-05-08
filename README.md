#  Intelligent Insider Threat Detection

A deep learning-based system that analyzes employee activity logs to identify suspicious behavior and potential insider threats within an organization.

---

## Project Overview

Insider threats are one of the most dangerous cybersecurity risks — they come from authorized employees who already have access to sensitive systems. This project uses multiple deep learning models to detect anomalous behavior from employee activity logs.

**Dataset:** CERT Insider Threat Dataset r4.2 — Carnegie Mellon University SEI  
**Approach:** Behavioral feature engineering + DNN + CNN + Autoencoder ensemble

---

## Team Members

| Member | Responsibilities |
|--------|-----------------|
| Member 1 | Data Loading, Preprocessing, Feature Engineering, DNN Model |
| Member 2 | CNN Model, Autoencoder, Risk Scoring, Presentation |

---

## Project Structure

```
insider-threat-detection/
│
├── data/
│   ├── logon.csv           # Login/logout events
│   ├── device.csv          # USB connect/disconnect events
│   ├── file.csv            # File access events
│   └── users.csv           # Employee metadata
│
├── models/
│   ├── dnn_model.py        # Deep Neural Network (Member 1)
│   ├── cnn_model.py        # Convolutional Neural Network (Member 2)
│   ├── autoencoder.py      # Autoencoder anomaly detector (Member 2)
│   └── risk_scoring.py     # Combined risk score (Member 2)
│
├── notebooks/
│   └── insider_threat_project.ipynb   # Main notebook
│
├── presentation/
│   └── insider_threat_detection.pptx
│
├── requirements.txt
└── README.md
```

---

##  Models Used

### 1. DNN Deep Neural Network (Member 1)
- **Purpose:** Binary classification of insider threat vs normal user
- **Input:** 8 behavioral features per user
- **Architecture:** Dense(128) → Dense(64) → Dense(32) → Dense(1)
- **Activation:** ReLU + Sigmoid output
- **Loss:** Binary Crossentropy | **Optimizer:** Adam

### 2. CNN  Convolutional Neural Network (Member 2)
- **Purpose:** Detect activity patterns that indicate insider threat
- **Input:** Behavioral features reshaped as (n_features, 1) sequence
- **Architecture:** Conv1D(32) → MaxPooling1D → Flatten → Dense(32) → Dense(1)
- **Train/Test Split:** 80% / 20% | **Epochs:** 20

### 3. Autoencoder (Member 2)
- **Purpose:** Anomaly detection via reconstruction error
- **Trained on:** Normal (non-threat) users only
- **Architecture:** Input → Dense(16) → Bottleneck(8) → Dense(16) → Output
- **Anomaly Score:** MSE between input and reconstruction
- **Threshold:** 90th percentile of MSE scores

---

##  Risk Scoring

All three model outputs are combined into a single unified risk score per user:

```
Risk Score = (0.33 × DNN Score) + (0.33 × CNN Score) + (0.33 × Autoencoder Error)
```

- Users with `risk_score > 0.5` are flagged as potential insider threats
- Top 10 highest-risk users are reported for investigation

---

##  Features Engineered

From the raw CSV logs, the following behavioral features are extracted per user:

| Feature | Source | Description |
|---------|--------|-------------|
| total_logons | logon.csv | Total login events |
| afterhours_logons | logon.csv | Logins after 6 PM |
| weekend_logons | logon.csv | Logins on weekends |
| unique_pcs | logon.csv | Number of machines accessed |
| total_file_actions | file.csv | Total file operations |
| removable_media_copies | file.csv | Files copied to USB |
| files_from_removable | file.csv | Files copied from USB |
| device_connects | device.csv | USB connect events |
| device_disconnects | device.csv | USB disconnect events |

---

##  Evaluation Metrics

- **Precision, Recall, F1-Score** — via `classification_report`
- **AUC-ROC Score** — area under the ROC curve
- **Reconstruction Error Plot** — visualizing anomaly scores per user
- **Training Loss Curves** — for both CNN and Autoencoder

---


## Dataset

**CERT Insider Threat Dataset r4.2**  
Source: Carnegie Mellon University  Software Engineering Institute  
Link: [https://resources.sei.cmu.edu/library/asset-view.cfm?assetid=508099](https://resources.sei.cmu.edu/library/asset-view.cfm?assetid=508099)

> This is a synthetic dataset designed for insider threat research. It simulates realistic employee behavior logs over 17 months for ~4,000 employees.

---

## Future Work
- Integrate `email.csv` for richer behavioral features
- Use real ground truth labels from the CERT answers file
- Add LSTM model for sequential time-series modeling
- Tune model hyperparameters with cross-validation
- Deploy as a real-time alerting dashboard
- Test on full dataset without row sampling limits

---

##  License

This project is for academic purposes only. Dataset usage follows CMU SEI terms and conditions.
