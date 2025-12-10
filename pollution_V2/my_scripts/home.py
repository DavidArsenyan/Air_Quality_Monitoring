from flask import Flask, render_template
import pandas as pd
import json
import os
import glob
from datetime import datetime


class DataLoader:
    """Handles loading and preprocessing of sensor data."""

    def __init__(self, pm25_path='../data/aligned_sensors_pm25_filled_knn.csv',
                 locations_path='../data/my_sensors_with_dates.csv'):
        self.pm25_path = pm25_path
        self.locations_path = locations_path
        self._df_pm25 = None
        self._sensor_columns = None
        self._sensor_locations = None

    def load_data(self):
        """Loads and preprocesses the main PM2.5 and sensor location data."""
        self._df_pm25 = pd.read_csv(self.pm25_path, parse_dates=['datetime_from_local'])
        self._df_pm25.set_index('datetime_from_local', inplace=True)

        df_loc = pd.read_csv(self.locations_path)
        self._sensor_locations = {str(row['sensor_id']): row['location_name']
                                  for _, row in df_loc.iterrows()}

        self._sensor_columns = [col for col in self._df_pm25.columns
                                if col.startswith('sensor_')]

        return self._df_pm25, self._sensor_columns, self._sensor_locations

    @property
    def df_pm25(self):
        if self._df_pm25 is None:
            self.load_data()
        return self._df_pm25

    @property
    def sensor_columns(self):
        if self._sensor_columns is None:
            self.load_data()
        return self._sensor_columns

    @property
    def sensor_locations(self):
        if self._sensor_locations is None:
            self.load_data()
        return self._sensor_locations


class DashboardDataProcessor:
    """Processes data for the main dashboard view."""

    def __init__(self, df_pm25, sensor_columns):
        self.df_pm25 = df_pm25
        self.sensor_columns = sensor_columns

    def get_7day_trend_data(self):
        """Returns 7-day trend data for all sensors."""
        df_last_7d = self.df_pm25.loc[self.df_pm25.index.max() - pd.Timedelta('7D'):].copy()
        sensor_ids = [col.replace('sensor_', '') for col in df_last_7d.columns]
        all_sensors_json = {col.replace('sensor_', ''): df_last_7d[col].tolist()
                            for col in df_last_7d.columns}
        labels_7d = df_last_7d.index.strftime('%Y-%m-%d').tolist()

        return sensor_ids, all_sensors_json, labels_7d

    def get_current_readings(self):
        """Returns current readings for all sensors."""
        current_readings_json = {}
        last_row = self.df_pm25.iloc[-1]

        for col in self.sensor_columns:
            sensor_id = col.replace('sensor_', '')
            pm25_value = last_row[col]

            current_readings_json[sensor_id] = {
                'pm25': round(pm25_value, 1) if pd.notna(pm25_value) else None,
                'timestamp': last_row.name.strftime('%Y-%m-%d %H:%M')
            }

        return current_readings_json

    def get_heatmap_data(self):
        """Returns 30-day heatmap data for all sensors."""
        df_heatmap_data = self.df_pm25.loc[self.df_pm25.index.max() - pd.Timedelta('30D'):].copy()

        time_diff = df_heatmap_data.index.date - df_heatmap_data.index.date.min()
        df_heatmap_data['day_index'] = (time_diff.astype('timedelta64[D]')).astype(int)
        df_heatmap_data['day_of_week'] = df_heatmap_data.index.dayofweek

        heatmap_matrix_data = {}
        for col in self.sensor_columns:
            sensor_id = col.replace('sensor_', '')
            sensor_data = []
            for index, row in df_heatmap_data.iterrows():
                pm25_value = row[col]
                if pd.notna(pm25_value):
                    pm25_value = round(pm25_value, 1)
                else:
                    pm25_value = None

                sensor_data.append({
                    'x': int(row['day_index']),
                    'y': int(row['day_of_week']),
                    'v': pm25_value,
                    'd': index.strftime('%Y-%m-%d')
                })
            heatmap_matrix_data[sensor_id] = sensor_data

        return heatmap_matrix_data

    def get_historical_records(self):
        """Returns best/worst day records for all sensors."""
        historical_records = {}
        df_daily_avg = self.df_pm25.resample('D').mean()

        for col in self.sensor_columns:
            sensor_id = col.replace('sensor_', '')
            valid_data = df_daily_avg[col].dropna()

            if not valid_data.empty:
                best_day_value = valid_data.min()
                best_day_date = valid_data.idxmin().strftime('%Y-%m-%d')
                worst_day_value = valid_data.max()
                worst_day_date = valid_data.idxmax().strftime('%Y-%m-%d')

                historical_records[sensor_id] = {
                    'best_v': round(best_day_value, 1),
                    'best_d': best_day_date,
                    'worst_v': round(worst_day_value, 1),
                    'worst_d': worst_day_date
                }
            else:
                historical_records[sensor_id] = {
                    'best_v': None, 'best_d': None,
                    'worst_v': None, 'worst_d': None
                }

        return historical_records


class HistoryDataProcessor:
    """Processes individual sensor CSV files for historical analysis."""

    def __init__(self, data_folder='../data/daily_data'):
        self.data_folder = data_folder

    def process_sensor_files(self):
        """Processes all sensor CSV files and returns statistics and time series data."""
        sensor_files = glob.glob(os.path.join(self.data_folder, 'sensor_*.csv'))

        sensor_stats = {}
        sensor_data_json = {}

        print(f"\n--- Starting Sensor File Processing ---")
        print(f"Found {len(sensor_files)} sensor files to process.")

        for file_path in sensor_files:
            filename = os.path.basename(file_path)
            sensor_id = filename.replace('sensor_', '').replace('.csv', '')

            try:
                stats, time_series = self._process_single_sensor(file_path, sensor_id)

                if stats:
                    sensor_stats[sensor_id] = stats
                    sensor_data_json[sensor_id] = time_series
                    print(f"SUCCESS: Sensor {sensor_id} processed. Data points: {stats['count']}")

            except Exception as e:
                print(f"ERROR processing {file_path}: {e}")
                continue

        print(f"\n--- Processing Complete ---")
        print(f"Sensor IDs successfully loaded: {sorted(sensor_stats.keys())}")

        return sorted(sensor_stats.keys()), sensor_stats, sensor_data_json

    def _process_single_sensor(self, file_path, sensor_id):
        """Processes a single sensor CSV file."""
        # Read CSV with datetime parsing
        df = pd.read_csv(file_path,
                         parse_dates=['datetime'] if 'datetime' in pd.read_csv(file_path, nrows=0).columns else [0])

        print(f"\nProcessing: {os.path.basename(file_path)}")
        print(f"Columns: {list(df.columns)}")

        # Identify PM2.5 column
        pm25_col = self._identify_pm25_column(df)

        if not pm25_col:
            print(f"WARN: Could not identify PM2.5 column for sensor {sensor_id}")
            return None, None

        print(f"Identified PM2.5 Column: '{pm25_col}'")

        # Convert to numeric and clean data
        df[pm25_col] = pd.to_numeric(df[pm25_col], errors='coerce')
        pm25_data = df[pm25_col].dropna()

        if pm25_data.empty:
            print(f"WARN: Sensor {sensor_id} skipped - empty after cleaning")
            return None, None

        # Calculate statistics
        stats = self._calculate_statistics(pm25_data)

        # Prepare time series data
        time_series = self._prepare_time_series(df, pm25_col)

        return stats, time_series

    def _identify_pm25_column(self, df):
        """Identifies the PM2.5 column in the dataframe."""
        if 'value' in df.columns:
            return 'value'
        elif 'pm25' in df.columns:
            return 'pm25'
        elif 'PM2.5' in df.columns:
            return 'PM2.5'
        elif len(df.columns) > 1:
            return df.columns[1]
        return None

    def _calculate_statistics(self, pm25_data):
        """Calculates statistical measures for PM2.5 data."""
        return {
            'mean': round(pm25_data.mean(), 2),
            'median': round(pm25_data.median(), 2),
            'std': round(pm25_data.std(), 2),
            'variance': round(pm25_data.var(), 2),
            'min': round(pm25_data.min(), 2),
            'max': round(pm25_data.max(), 2),
            'q25': round(pm25_data.quantile(0.25), 2),
            'q75': round(pm25_data.quantile(0.75), 2),
            'count': int(len(pm25_data))
        }

    def _prepare_time_series(self, df, pm25_col):
        """Prepares time series data for visualization."""
        if len(df.columns) == 0:
            return None

        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df_sorted = df.sort_values(date_col).dropna(subset=[date_col, pm25_col])

        return {
            'dates': df_sorted[date_col].dt.strftime('%Y-%m-%d').tolist(),
            'values': df_sorted[pm25_col].round(2).tolist()
        }


class ForecastDataProcessor:
    """Processes forecast data for the forecast dashboard."""

    def __init__(self, df_pm25, sensor_columns, forecast_path='../data/new_forecast.csv'):
        self.df_pm25 = df_pm25
        self.sensor_columns = sensor_columns
        self.forecast_path = forecast_path

    def get_forecast_data(self, n_actual_days=7):
        """Returns actual and forecast data for all sensors."""
        try:
            df_forecast = pd.read_csv(self.forecast_path, index_col=0, parse_dates=True)
        except FileNotFoundError:
            df_forecast = pd.DataFrame(columns=self.df_pm25.columns)

        df_actual_compare = self.df_pm25.loc[
                            self.df_pm25.index.max() - pd.Timedelta(f'{n_actual_days}D'):
                            ].copy()

        forecast_data_json = {}

        for col in self.sensor_columns:
            sensor_id = col.replace('sensor_', '')

            actual_values = df_actual_compare[col].round(1).tolist()
            actual_labels = df_actual_compare.index.strftime('%m-%d').tolist()

            if col in df_forecast.columns:
                future_values = df_forecast[col].round(1).tolist()
                future_labels = df_forecast.index.strftime('%m-%d').tolist()
            else:
                future_values = []
                future_labels = []

            forecast_data_json[sensor_id] = {
                'actual_values': actual_values,
                'actual_labels': actual_labels,
                'future_values': future_values,
                'future_labels': future_labels
            }

        sensor_ids = [col.replace('sensor_', '') for col in self.sensor_columns]

        return sensor_ids, forecast_data_json


class AirQualityApp:
    """Main application class that orchestrates the Flask app and data processors."""

    def __init__(self):
        self.app = Flask(__name__, template_folder="templates")
        self.data_loader = DataLoader()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up Flask routes."""
        self.app.route('/')(self.dashboard)
        self.app.route('/history')(self.history_dashboard)
        self.app.route('/forecast')(self.forecast_dashboard)

    def dashboard(self):
        """Renders the main dashboard page."""
        df_pm25, sensor_columns, sensor_locations_json = self.data_loader.load_data()

        processor = DashboardDataProcessor(df_pm25, sensor_columns)

        sensor_ids, all_sensors_json, labels_7d = processor.get_7day_trend_data()
        current_readings_json = processor.get_current_readings()
        heatmap_matrix_data = processor.get_heatmap_data()
        historical_records = processor.get_historical_records()

        return render_template('home.html',
                               sensor_ids=sensor_ids,
                               all_sensors_json=json.dumps(all_sensors_json),
                               labels_7d=json.dumps(labels_7d),
                               current_readings_json=json.dumps(current_readings_json),
                               historical_records_json=json.dumps(historical_records),
                               heatmap_matrix_data=json.dumps(heatmap_matrix_data),
                               sensor_locations_json=json.dumps(sensor_locations_json))

    def history_dashboard(self):
        """Renders the sensor history dashboard."""
        _, _, sensor_locations_json = self.data_loader.load_data()

        processor = HistoryDataProcessor()
        sensor_ids, sensor_stats, sensor_data_json = processor.process_sensor_files()

        return render_template('history.html',
                               sensor_ids=sensor_ids,
                               sensor_stats_json=json.dumps(sensor_stats),
                               sensor_data_json=json.dumps(sensor_data_json),
                               sensor_locations_json=json.dumps(sensor_locations_json))

    def forecast_dashboard(self):
        """Renders the forecast dashboard page."""
        df_pm25, sensor_columns, sensor_locations_json = self.data_loader.load_data()

        processor = ForecastDataProcessor(df_pm25, sensor_columns)
        sensor_ids, forecast_data_json = processor.get_forecast_data()

        return render_template('forecast.html',
                               sensor_ids=sensor_ids,
                               forecast_data_json=json.dumps(forecast_data_json),
                               sensor_locations_json=json.dumps(sensor_locations_json))

    def run(self, debug=True):
        """Runs the Flask application."""
        self.app.run(debug=debug)


if __name__ == '__main__':
    air_quality_app = AirQualityApp()
    air_quality_app.run(debug=True)