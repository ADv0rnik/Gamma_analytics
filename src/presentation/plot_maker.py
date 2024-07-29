import pandas as pd
from matplotlib import pyplot as plt

from src.config import (
    IS_FIXED_DISTANCE,
    NORMALIZED,
    OUTPUT_DIR
)


def make_graph(data: pd.DataFrame, dist_predefined=IS_FIXED_DISTANCE, normalize=NORMALIZED) -> None:
    figure, ax = plt.subplots(figsize=(16, 6))
    x = data["x"]
    columns = [column for column in data.columns if column.startswith('sim') and not column.endswith('n')]
    columns_norm = [column for column in data.columns if column.startswith('sim') and column.endswith('n')]
    try:
        if dist_predefined:
            y = data["sim_data"]
            ax.plot(x, y, lw=1)
            plt.savefig(OUTPUT_DIR + "/" + "fig_single.png")
            # plt.show()
        elif normalize:
            data.plot(x="x", y=columns_norm, xlabel="Distance / m", ylabel="Fluence rate", grid=True)
            plt.savefig(OUTPUT_DIR + "/" + "fig_multi_norm_1.png")
            # plt.show()
        else:
            data.plot(x="x", y=columns)
            plt.savefig(OUTPUT_DIR + "/" + "fig_multi.png")
    except TypeError as e:
        print(f"An error occurred while creating plot: {e}")