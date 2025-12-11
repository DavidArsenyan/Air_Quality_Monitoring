import datetime
import pandas as pd
from openaq import OpenAQ

client = OpenAQ(api_key="f2ae9f923f46869d0254a8f714b115d8ff9b26ae25178ab506172346f487455b")
def func(sensor_id): # initilize function for getting data of sensors which correspond to the following conditions
    response = client.measurements.list(
    sensors_id=sensor_id,
    data="days",
    datetime_from=datetime.datetime(2024,11,16),
    datetime_to=datetime.datetime(2025,11,16),

    )
    return response

new_data = pd.read_csv("../data/my_sensors_with_dates.csv")
sens_data = new_data["sensor_id"]
 
for i in sens_data: # here we just create a new dataframe for the sensors and make a .csv file for them with this properties
    all_data = []
    response = func(i)
    for m in response.results:
        all_data.append({
            "datetime_from_local": m.period.datetime_from.local,
            "datetime_to_local": m.period.datetime_to.local,
            "value": m.value,
            "parameter": m.parameter.name
        })

        df = pd.DataFrame(all_data)
        df.to_csv(f"../data/daily_data/sensor_{i}.csv", index=False)
df = pd.DataFrame(all_data)
