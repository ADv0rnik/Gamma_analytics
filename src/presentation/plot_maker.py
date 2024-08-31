import os
import pandas as pd

from matplotlib import pyplot as plt
from dataclasses import dataclass

from src.config import OUTPUT_DIR, STEP, SRC_Y

GRID_PARAMS = {
    "linestyle":'-',
    "linewidth":1
}
FONT_PARAMS = {
    'fontsize': 16,
    'fontweight': 'normal',
    'family': 'sans-serif',
    'fontstyle': 'normal'
}
TITLE_PARAMS = {
    'fontsize': 18,
    'fontweight': 'bold',
    'color': 'darkblue',
    'family': 'sans-serif',
    'fontstyle': 'normal'
}
LEGEND_PARAMS = {
    "family": "sans-serif",
    "weight": "normal",
    "size": 14
}
LABELS = {
    "x": "Distance, m",
    "y": "Count rate",
}
LEGEND = True


@dataclass
class PlotMaker:
    data: pd.DataFrame
    output_file: str = None
    legend: str = "Count rate"

    def plot_count_rate(self, **kwargs) -> str:
        figure, ax = plt.subplots(figsize=(16, 6))
        x = self.data["x"]
        dist_predefined = kwargs["dist_predefined"]
        normalized = kwargs["normalized"]
        columns = [column for column in self.data.columns if column.startswith('generic') and not column.endswith('n')]
        columns_norm = [column for column in self.data.columns if column.startswith('generic') and column.endswith('n')]

        if dist_predefined and not normalized:
            title = f"Count rate with predefined distance of {SRC_Y} meters"
            filename = "default_plot_non_normalized.png"
            self.output_file = os.path.join(OUTPUT_DIR, filename)
            y = self.data["generic_count_rate"]

            self.__set_ax_params(ax, title)
            ax.plot(x, y, lw=2, color="red")

            plt.legend([self.legend], frameon=False, prop=LEGEND_PARAMS)
            plt.savefig(self.output_file)
        if dist_predefined and normalized:
            title = f"Count rate with predefined distance of {SRC_Y} meters (Normalized)"
            filename = "default_plot_normalized.png"
            self.output_file = os.path.join(OUTPUT_DIR, filename)
            y = self.data["generic_count_rate_n"]

            self.__set_ax_params(ax, title)
            ax.plot(x, y, lw=2, color="red")

            plt.legend([self.legend], frameon=False, prop=LEGEND_PARAMS)
            plt.savefig(self.output_file)
        if not dist_predefined and not normalized:
            title = f"Count Rate vs. Distance (Source to detector distance step: {STEP} m.)"
            filename = "default_multiplot_non_normalized.png"
            self.output_file = os.path.join(OUTPUT_DIR, filename)

            self.__set_ax_params(ax, title)
            for column in columns:
                ax.plot(self.data["x"], self.data[column], lw=2)

            plt.legend(columns, frameon=False, prop=LEGEND_PARAMS)
            plt.savefig(self.output_file)
        if not dist_predefined and normalized:
            title = f"Normalized count rate vs. Distance (Source to detector distance step: {STEP} m.)"
            filename = "default_multiplot_normalized.png"
            self.output_file = os.path.join(OUTPUT_DIR, filename)

            self.__set_ax_params(ax, title)
            for column in columns_norm:
                ax.plot(x, self.data[column], lw=2)

            plt.legend(columns_norm, frameon=False, prop=LEGEND_PARAMS)
            plt.savefig(self.output_file)

        plt.close(figure)
        return self.output_file

    def plot_poisson(self, **kwargs) -> str:
        figure, ax = plt.subplots(figsize=(16, 6))
        x = self.data["x"]
        y = self.data["pois_data"]

        title = f"Poisson distribution for count rate (Speed: {kwargs['speed']} m per sec, Acquisition time: {kwargs['time']} sec)"
        filename = "poisson_plot.png"
        self.output_file = os.path.join(OUTPUT_DIR, filename)
        self.__set_ax_params(ax, title)
        ax.plot(x, y, lw=2, color="red")

        plt.legend([self.legend], frameon=False, prop=LEGEND_PARAMS)
        plt.savefig(self.output_file)
        plt.close(figure)
        return self.output_file

    @staticmethod
    def __set_ax_params(axes, title):
        """
        Set parameters for the plot
        :return: None
        """
        axes.spines.top.set_visible(False)
        axes.spines.right.set_visible(False)
        axes.tick_params(axis='both', length=5.0, labelsize=12)
        axes.grid(True, which='major', axis='y', **GRID_PARAMS)
        axes.set_title(title, fontdict=TITLE_PARAMS)
        axes.set_ylabel(LABELS["y"], fontdict=FONT_PARAMS)
        axes.set_xlabel(LABELS["x"], fontdict=FONT_PARAMS)
