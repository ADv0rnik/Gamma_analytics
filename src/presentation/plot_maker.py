import os
import pandas as pd

from matplotlib import pyplot as plt
from dataclasses import dataclass

from src.config import OUTPUT_DIR

GRID_PARAMS = {
    "linestyle":'-',
    "linewidth":1
}

FONT_PARAMS = {
    "fontsize": 14,
    "fontweight": "bold",
    "fontfamily": "Arial",
}

LEGEND = True


@dataclass
class PlotMaker:
    data: pd.DataFrame

    def make_single(self, **kwargs) -> str:
        output_file = None
        figure, ax = plt.subplots(figsize=(16, 6))
        dist_predefined = kwargs["dist_predefined"]
        normalized = kwargs["normalized"]

        columns = [column for column in self.data.columns if column.startswith('generic') and not column.endswith('n')]
        columns_norm = [column for column in self.data.columns if column.startswith('generic') and column.endswith('n')]
        if dist_predefined and not normalized:

            title = "Count rate with predefined distance"

            filename = "default_plot_non_normalized.png"
            output_file = os.path.join(OUTPUT_DIR, filename)
            x = self.data["x"]
            y = self.data["generic_count_rate"]

            self.__set_ax_params(ax, title)
            ax.plot(x, y, lw=1)

            plt.savefig(output_file)
        if dist_predefined and normalized:
            title = "Count rate with predefined distance (Normalized)"
            filename = "default_plot_normalized.png"
            output_file = os.path.join(OUTPUT_DIR, filename)
            x = self.data["x"]
            y = self.data["generic_count_rate_n"]

            self.__set_ax_params(ax, title)
            ax.plot(x, y, lw=1)

            plt.savefig(output_file)
        if not dist_predefined and not normalized:
            filename = "default_multiplot_non_normalized.png"
            output_file = os.path.join(OUTPUT_DIR, filename)
            self.data.plot(x="x", y=columns)
            plt.savefig(output_file)
        if not dist_predefined and normalized:
            filename = "default_multiplot_normalized.png"
            output_file = os.path.join(OUTPUT_DIR, filename)
            self.data.plot(x="x", y=columns_norm, xlabel="Distance / m", ylabel="Count rate, cps", grid=True)
            plt.savefig(output_file)

        plt.close(figure)
        return output_file

    @staticmethod
    def __set_ax_params(axes, title):
        """
        Set parameters for the plot
        :return:
        """
        axes.spines.top.set_visible(False)
        axes.spines.right.set_visible(False)

        axes.legend()
        axes.grid(True, which='major', axis='y', **GRID_PARAMS)
        axes.set_title(title, fontweight ="bold")
