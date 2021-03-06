# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

query = """
SELECT
  CASE WHEN (DAYOFWEEK(pickup_datetime) = 1) THEN 1 ELSE 0 END AS sunday,
  CASE WHEN (DAYOFWEEK(pickup_datetime) = 2) THEN 1 ELSE 0 END AS monday,
  CASE WHEN (DAYOFWEEK(pickup_datetime) = 3) THEN 1 ELSE 0 END AS tuesday,
  CASE WHEN (DAYOFWEEK(pickup_datetime) = 4) THEN 1 ELSE 0 END AS wednesday,
  CASE WHEN (DAYOFWEEK(pickup_datetime) = 5) THEN 1 ELSE 0 END AS thursday,
  CASE WHEN (DAYOFWEEK(pickup_datetime) = 6) THEN 1 ELSE 0 END AS friday,
  CASE WHEN (DAYOFWEEK(pickup_datetime) = 7) THEN 1 ELSE 0 END AS saturday,
  HOUR(pickup_datetime) AS hourofday,
  pickup_longitude,
  pickup_latitude,
  dropoff_longitude,
  dropoff_latitude,
  passenger_count AS passenger_count,
  (tolls_amount + fare_amount) AS fare_amount
FROM
  [nyc-tlc:yellow.trips]
WHERE
  trip_distance > 0
  AND fare_amount >= 2.5
  AND pickup_longitude > -78
  AND pickup_longitude < -70
  AND dropoff_longitude > -78
  AND dropoff_longitude < -70
  AND pickup_latitude > 37
  AND pickup_latitude < 45
  AND dropoff_latitude > 37
  AND dropoff_latitude < 45
  AND passenger_count > 0
  AND ABS(HASH(pickup_datetime)) % 100000 == {}
"""

features = [
    "sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
    "hourofday",
    "pickup_latitude", "pickup_longitude",
    "dropoff_latitude", "dropoff_longitude",
    "passenger_count",
    "estimated_distance"
]
objective = ["fare_amount"]


def distance_between(lat1, lon1, lat2, lon2):
    # haversine formula to compute distance "as the crow flies".  Taxis can't fly of course.
    dist = np.degrees(np.arccos(np.sin(np.radians(lat1)) * np.sin(np.radians(lat2)) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.cos(np.radians(lon2 - lon1)))) * 60 * 1.515 * 1.609344
    return dist


def estimate_distance(df):
    return distance_between(df['pickup_latitude'], df['pickup_longitude'], df['dropoff_latitude'], df['dropoff_longitude'])


def compute_rmse(actual, predicted):
    return np.sqrt(np.mean((actual-predicted)**2))


def print_rmse(df, rate, name):
    print "{1} RMSE = {0}".format(compute_rmse(df['fare_amount'], rate*estimate_distance(df)), name)


def create_data(n):
    df = pd.io.gbq.read_gbq(query.format(n), project_id="cpb102demo1")
    df["estimated_distance"] = estimate_distance(df)
    return df.dropna()


if __name__ == "__main__":
    df_train = create_data(1)
    df_test = create_data(2)
    rate = df_train['fare_amount'].mean() / estimate_distance(df_train).mean()
    print "Rate = ${0}/km".format(rate)
    print_rmse(df_train, rate, 'Train')
    print_rmse(df_test, rate, 'Test')
    df_train[features+objective].to_csv("trainer/data/taxi-feateng-train.csv", index=False)
    df_test[features+objective].to_csv("trainer/data/taxi-feateng-test.csv", index=False)
