# Air Quality Monitoring and Forecasting System

This project provides a complete pipeline for collecting, processing, and forecasting PM2.5 air-quality data in Yerevan using the OpenAQ API, Python data-processing tools, machine learning, and a Flask-based dashboard.

## Features

- Automatic retrieval of sensor metadata from the OpenAQ platform  
- Daily PM2.5 data collection for all available sensors  
- Dataset merging, cleaning, and missing-value imputation using KNN  
- LSTM-based forecasting model for short-term predictions  
- Modular backend architecture using object-oriented design principles  
- Interactive dashboard for data visualization and analysis  
- Fully reproducible workflow from raw data to forecast results  

## Project Structure

```
pollution_V2/
│
├── my_scripts/
│   ├── main.py               # Retrieve sensor metadata from OpenAQ
│   ├── data_handling.py      # Download daily PM2.5 data for each sensor
│   ├── data_combining.py     # Merge individual sensor files into a unified dataset
│   ├── data_analysis.py      # Clean data and perform KNN imputation
│   ├── model.py              # LSTM forecasting model and prediction generation
│
├── home.py                   # Flask backend entry point
├── templates/                # Dashboard HTML pages
├── data/                     # Raw and processed datasets
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/DavidArsenyan/Air_Quality_Monitoring.git
cd Air_Quality_Monitoring/pollution_V2
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Full Pipeline

To reproduce the entire dataset and forecast results, run the scripts in the following order:

### 1. Retrieve sensor metadata
```bash
python my_scripts/main.py
```

### 2. Download daily PM2.5 measurements
```bash
python my_scripts/data_handling.py
```

### 3. Combine sensor files into a unified dataset
```bash
python my_scripts/data_combining.py
```

### 4. Clean and impute missing values
```bash
python my_scripts/data_analysis.py
```

### 5. Train the LSTM forecasting model
```bash
python my_scripts/model.py
```

## Launching the Dashboard

Start the Flask server:

```bash
python home.py
```

Then open the dashboard in a web browser:

```
http://127.0.0.1:5000/
```

The interface includes:

- A main overview page with trends, heatmaps, and aggregated statistics  
- A forecasting page displaying LSTM prediction results  
- A history page containing long-term sensor performance and daily averages  

## Notes

- You must supply a valid OpenAQ API key in `main.py` and `data_handling.py`.  
- The system employs an object-oriented backend for improved modularity and maintainability.  

## License

This project is intended for academic purposes.
