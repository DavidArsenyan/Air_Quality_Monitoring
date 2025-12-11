# 📌 Air Quality Monitoring and Forecasting System

A complete pipeline for collecting, processing, analyzing, and forecasting PM2.5 air-quality data in Yerevan using the OpenAQ API, machine learning techniques, and an interactive Flask dashboard.

---

## 🚀 Features

- 🌍 Automatic retrieval of sensor metadata from OpenAQ  
- 📥 Daily PM2.5 data collection for all Yerevan sensors  
- 🧹 Dataset cleaning and missing-value imputation (KNN)  
- 🤖 LSTM neural network for 7-day PM2.5 forecasting  
- 🧩 Modular OOP-based backend implemented in Flask  
- 📊 Interactive dashboard (overview, forecast, history) using Chart.js  
- 🔄 Fully reproducible end-to-end pipeline  

---

## 📁 Project Structure

```
pollution_V2/
│
├── my_scripts/
│   ├── main.py               # Retrieve sensor metadata
│   ├── data_handling.py      # Download daily PM2.5 data
│   ├── data_combining.py     # Merge sensor datasets
│   ├── data_analysis.py      # Clean + KNN imputation
│   ├── model.py              # LSTM forecasting model
│
├── home.py                   # Flask backend entry point
├── templates/                # Dashboard HTML pages
├── data/                     # Raw + processed datasets
├── requirements.txt
└── README.md
```

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/DavidArsenyan/Air_Quality_Monitoring.git
cd Air_Quality_Monitoring/pollution_V2
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔧 Running the Full Pipeline (Correct Order)

### 1. Retrieve Sensor Metadata  
```bash
python my_scripts/main.py
```

### 2. Download Daily Sensor Data  
```bash
python my_scripts/data_handling.py
```

### 3. Combine Sensor CSV Files  
```bash
python my_scripts/data_combining.py
```

### 4. Clean + Impute Missing Values (KNN)  
```bash
python my_scripts/data_analysis.py
```

### 5. Train LSTM Forecasting Model  
```bash
python my_scripts/model.py
```

---

## 🖥 Launching the Dashboard

Start the Flask backend:

```bash
python home.py
```

Open the dashboard:

```
http://127.0.0.1:5000/
```

---

## 🧠 Notes

- Requires a valid OpenAQ API key in `main.py` and `data_handling.py`.  
- Running `model.py` retrains the LSTM and updates `new_forecast.csv`.  
- The backend follows an OOP architecture for better modularity.

---

## 📄 License

This project is intended for academic and research purposes.
