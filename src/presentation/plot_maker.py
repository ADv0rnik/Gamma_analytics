import os

import pandas as pd
from matplotlib import pyplot as plt

from src.config import (
    IS_FIXED_DISTANCE,
    NORMALIZED,
    OUTPUT_DIR
)


def make_graph(data: pd.DataFrame, dist_predefined=IS_FIXED_DISTANCE, normalize=NORMALIZED) -> dict:
    figure, ax = plt.subplots(figsize=(16, 6))
    x = data["x"]
    columns = [column for column in data.columns if column.startswith('sim') and not column.endswith('n')]
    columns_norm = [column for column in data.columns if column.startswith('sim') and column.endswith('n')]

    try:
        if dist_predefined:
            filename = "plot_single.png"
            output_file = os.path.join(OUTPUT_DIR, filename)
            y = data["sim_data"]
            ax.plot(x, y, lw=1)
            plt.savefig(output_file)
        elif normalize:
            filename = "plot_multi_normalized.png"
            output_file = os.path.join(OUTPUT_DIR, filename)
            data.plot(x="x", y=columns_norm, xlabel="Distance / m", ylabel="Fluence rate", grid=True)
            plt.savefig(OUTPUT_DIR, filename)
        else:
            filename = "plot_multi.png"
            output_file = os.path.join(OUTPUT_DIR, filename)
            data.plot(x="x", y=columns)
            plt.savefig(OUTPUT_DIR, filename)
    except TypeError as e:
        print(f"An error occurred while creating plot: {e}")
    else:
        plt.close(figure)
        return {
            "plot": output_file
        }

# TODO: Revoke make_graph function using OOP approach
