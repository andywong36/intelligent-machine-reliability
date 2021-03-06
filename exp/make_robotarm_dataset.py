from os import path

import click
import numpy as np
import pandas as pd

@click.command()
@click.argument('src_dir', type=click.Path(exists=True))
@click.argument('dest_dir', type=click.Path(exists=True))
def convert_robot_data(src_dir, dest_dir):
    colnames = ("tick", "direction", "position", "torque", "tension")

    normal_data = dict()
    abnormal_data = dict()

    normal_data["normal"] = path.join(src_dir, "Normal_adjusted_150.csv")

    abnormal_data["loose_l2"] = path.join(src_dir, "loose_data_99-100.csv")
    abnormal_data["loose_l1"] = path.join(src_dir, "loose_data_120-122.csv")
    abnormal_data["tight"] = path.join(src_dir, "tight_data_168-170.csv")
    abnormal_data["sandy"] = path.join(src_dir, "sandy_data_150-152.csv")
    abnormal_data["highT"] = path.join(src_dir, "temperature_166_at_40deg.csv")
    # abnormal_data["obstruction"] = src_dir + r"\obstruction_data.csv"

    for dictionary in [normal_data, abnormal_data]:
        for label in dictionary:
            combined_data = load_robot_data(dictionary[label])
            deststr = path.join(dest_dir, "robotarm_{}.pkl".format(label))
            click.echo(f"Writing to {deststr}")
            pd.to_pickle(combined_data, deststr)


def load_robot_data(filename):
    data = pd.read_csv(filename, sep=",")
    data.columns = ["time", "run", "direction", "position", "torque", "tension"]

    # Delete the first couple of rows, where the angle is being calibrated
    data = data[(data.run != 0) & (data.direction != 0)]
    # Delete the rows where there are an inconsistent number of observations
    uniq, counts = np.unique(data.run, return_counts=True)
    mask = uniq[counts == 2000]
    data = data[np.isin(data.run, mask)]

    data["time"] = [i % 2000 for i in range(len(data))]
    data["direction"] = data["direction"] - 1

    rl_data = data[["time", "direction", "position", "torque", "tension"]].copy()
    rl_data.set_index(pd.Series(range(len(rl_data))), inplace=True)

    return rl_data

if __name__ == "__main__":
    convert_robot_data()