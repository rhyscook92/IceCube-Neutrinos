import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import math


def get_sensor_fig(sensor_geometry):
    sensor_fig = px.scatter_3d(
        sensor_geometry,
        x="x",
        y="y",
        z="z",
        opacity=0.3,
        color_discrete_sequence=["black"],
    )
    sensor_fig.update_traces(marker_size=1)
    sensor_fig["data"][0]["showlegend"] = True
    sensor_fig["data"][0]["name"] = "Sensor location"
    sensor_fig.update_layout(legend={"itemsizing": "constant"})

    return sensor_fig


def get_charge_fig(frame_time, event_train, sensor_geometry, max_charge):
    """
    Creates a plotly 3dScatter plot of the max charge per sensor as of frame_time
    """
    frame_df = event_train.loc[event_train["time"] <= frame_time]
    frame_df = frame_df.groupby(["sensor_id"], as_index=False).agg({"charge": "sum"})

    frame_geometry = sensor_geometry.merge(
        frame_df,
        how="inner",
        on="sensor_id",
    )

    frame_fig = px.scatter_3d(
        frame_geometry,
        x="x",
        y="y",
        z="z",
        opacity=0.7,
        size="charge",
        color="charge",
        size_max=40 * frame_geometry["charge"].max() / max_charge,
    )

    return frame_fig


def get_centroid(event_train, sensor_geometry, centroid_method="highest_charge"):
    """
    Returns the charge weighted centroid of the neutrino collision.
    This seems like an interesting point to pass our line through
    """
    centroid = event_train.merge(sensor_geometry, on="sensor_id", how="left")

    if centroid_method == "highest_charge":
        # Make sure the line passes through the highest charge point
        centroid = (
            centroid.groupby(["x", "y", "z"], as_index=False)
            .agg({"charge": "sum"})
            .sort_values(by="charge", ascending=False)
            .head(1)
        )
    else:
        # Make the line pass through the charge weighted "mean" point
        for column in ["x", "y", "z"]:
            centroid[column] *= centroid["charge"]
        centroid = centroid.groupby(["event_id"], as_index=False).agg(
            {"x": "mean", "y": "mean", "z": "mean"}
        )

    return centroid["x"].item(), centroid["y"].item(), centroid["z"].item()


def get_line_fig(event_meta, event_train, sensor_geometry):
    azimuth = event_meta.azimuth.item()
    zenith = event_meta.zenith.item()

    # unnormalised direction vector
    x_hat = np.cos(azimuth) * np.sin(zenith)
    y_hat = np.sin(azimuth) * np.sin(zenith)
    z_hat = np.cos(zenith)

    # we want to force this line to pass through the most intersting point in the event_df
    x_0, y_0, z_0 = get_centroid(event_train, sensor_geometry)

    lines = {
        "x": [-1000 * x_hat + x_0, 1000 * x_hat + x_0],
        "y": [-1000 * y_hat + y_0, 1000 * y_hat + y_0],
        "z": [-1000 * z_hat + z_0, 1000 * z_hat + z_0],
    }
    line_df = pd.DataFrame(data=lines)
    line_fig = px.line_3d(line_df, x="x", y="y", z="z", color_discrete_sequence=["red"])
    line_fig["data"][0]["showlegend"] = True
    line_fig["data"][0]["name"] = "Neutrino direction"

    return line_fig


def build_event_fig(event_id, sensor_geometry, train, train_meta, aux_filter):
    event_train = train.loc[train["event_id"] == event_id].copy()
    event_meta = train_meta[train_meta["event_id"] == event_id]

    sensor_fig = get_sensor_fig(sensor_geometry)
    line_fig = get_line_fig(event_meta, event_train, sensor_geometry)

    if aux_filter == "False Only":
        event_train = event_train.loc[event_train["auxiliary"] == False]
    elif aux_filter == "True Only":
        event_train = event_train.loc[event_train["auxiliary"] == True]

    max_charge = event_train.groupby("sensor_id").agg({"charge": "sum"}).charge.max()

    event_fig = get_event_fig(
        sensor_fig, sensor_geometry, line_fig, max_charge, event_train
    )

    return event_fig


def get_event_fig(
    sensor_fig, sensor_geometry, line_fig, max_charge, event_train, num_frames=20
):

    # make figure
    fig_dict = {"data": [], "layout": {}, "frames": []}

    # fill in most of layout
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [
                        None,
                        {
                            "frame": {"duration": 300, "redraw": True},
                            "fromcurrent": True,
                            "transition": {
                                "duration": 150,
                                "easing": "quadratic-in-out",
                            },
                        },
                    ],
                    "label": "Play",
                    "method": "animate",
                },
                {
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0},
                        },
                    ],
                    "label": "Pause",
                    "method": "animate",
                },
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87, "l": 10},
            "showactive": False,
            "type": "buttons",
            "x": 0.35,
            "xanchor": "right",
            "y": 0.1,
            "yanchor": "top",
        }
    ]

    sliders_dict = {
        "active": num_frames - 1,
        "yanchor": "top",
        "xanchor": "center",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Time:",
            "visible": True,
            "xanchor": "right",
        },
        "transition": {"duration": 200, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 10, "l": 10, "r": 10},
        "len": 0.9,
        "x": 0.8,
        "y": 0,
        "steps": [],
    }

    # Prepare times to label slider
    event_train["time"] = event_train["time"] - event_train["time"].min()
    end_time = event_train["time"].max()
    time_step = math.ceil(end_time / num_frames)

    # Display final frame as a starting point
    charge_fig = get_charge_fig(end_time, event_train, sensor_geometry, max_charge)
    fig_dict["data"] = [sensor_fig.data[0], line_fig.data[0], charge_fig.data[0]]

    # Interate over the frames and update the slider
    for frame_num in range(0, num_frames):

        # Build the frame data
        frame_time = frame_num * time_step
        charge_fig = get_charge_fig(
            frame_time, event_train, sensor_geometry, max_charge
        )

        # Build the frame data
        frame = {"data": [], "name": frame_num}
        frame["data"] = [sensor_fig.data[0], line_fig.data[0], charge_fig.data[0]]
        fig_dict["frames"].append(frame)

        # Update the slider
        slider_text = f"{int(round(frame_time, 0))}ns"
        slider_step = {
            "args": [
                [str(frame_num)],
                {
                    "frame": {"duration": 300, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 300},
                },
            ],
            "label": slider_text,
            "method": "animate",
        }
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)

    # Touch up the layout
    camera = dict(
        up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=0), eye=dict(x=0, y=1.3, z=0)
    )
    fig.update_layout(
        coloraxis_colorbar_title_text="Charge",
        paper_bgcolor="#f8f9fa",
        coloraxis_colorbar=dict(lenmode="fraction", len=0.75, thickness=20),
        scene_camera=camera,
        scene=dict(
            xaxis=dict(showticklabels=False, range=[-600, 600]),
            yaxis=dict(showticklabels=False, range=[-600, 600]),
            zaxis=dict(showticklabels=False, range=[-600, 600]),
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_visible=False,
        ),
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=20,  # top margin
        ),
    )
    fig.update_coloraxes(cmax=max_charge, cmin=0, colorscale="Plasma")

    return fig
