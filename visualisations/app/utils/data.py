import pandas as pd
import polars as pl

def get_data():
    train_meta_path = "./kaggle/input/icecube-neutrinos-in-deep-ice/train_meta.parquet"
    train_path = "./kaggle/input/icecube-neutrinos-in-deep-ice/batch_1.parquet"
    sensor_geometry_path = (
        "./kaggle/input/icecube-neutrinos-in-deep-ice/sensor_geometry.csv"
    )

    train = pl.read_parquet(train_path).to_pandas() # 3 seconds quicker than reading directly with Pandas
    sensor_geometry = pd.read_csv(sensor_geometry_path)
    train_meta = pd.read_parquet(train_meta_path)

    return train, train_meta, sensor_geometry


def get_top_5_interactions(train, sensor_geometry, event_id):
    event_train = train.loc[train["event_id"] == event_id].copy()
    event_train["time"] = event_train["time"] - event_train["time"].min()
    event_train = event_train.sort_values(by="charge", ascending=False).head(5)
    event_train = event_train.merge(
        sensor_geometry,
        how="inner",
        on="sensor_id",
    )
    event_train["charge"] = round(event_train["charge"], 1)
    event_train["auxiliary"] = event_train["auxiliary"].astype(str)
    for column in ["x", "y", "z"]:
        event_train[column] = round(event_train[column])

    event_train.columns = [
        "Event ID",
        "Sensor ID",
        "Time (ns)",
        "Charge (eV)",
        "Auxiliary",
        "x",
        "y",
        "z",
    ]

    return event_train


def get_data_text():
    with open("./utils/data_text.txt", "r") as f:
        data_text = f.read()
    return data_text


def get_how_to_text():
    with open("./utils/how_to_text.txt", "r") as f:
        how_to_text = f.read()
    return how_to_text
