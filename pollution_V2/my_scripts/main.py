# -------------------------- #
from openaq import OpenAQ
import pandas as pd

client = OpenAQ("f2ae9f923f46869d0254a8f714b115d8ff9b26ae25178ab506172346f487455b")

locations = client.locations.list(
    bbox=(44.40, 40.10, 44.65, 40.32),  # The bbox defines a rectangular geographic area to limit the search.
    limit=100 # sets the maximum number of locations to retrieve.
)

rows = []

for loc in locations.results:
    for sensor in loc.sensors:
        rows.append({
            "location_id": loc.id,
            "location_name": loc.name,
            "sensor_id": sensor.id,
            "parameter": sensor.parameter.name,
            "datetime_first": loc.datetime_first.utc,
            "datetime_last": loc.datetime_last.utc
        })

df = pd.DataFrame(rows)
df.to_csv("../data/my_sensors_with_dates.csv", index=False)
print("Saved", len(df), "rows.")
