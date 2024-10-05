import os
import pandas as pd

from matplotlib import pyplot as plt
from dataclasses import dataclass
from src.utils import mean_count_rate
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
    data: pd.DataFrame | pd.Series
    output_file: str = None
    legend: list = None

    def plot_count_rate(self, **kwargs) -> str:
        figure, ax = plt.subplots(figsize=(16, 6))
        x = self.data["x"]
        dist_predefined = kwargs["dist_predefined"]
        normalized = kwargs["normalized"]
        columns = [column for column in self.data.columns if column.startswith('generic') and not column.endswith('n')]
        columns_norm = [column for column in self.data.columns if column.startswith('generic') and column.endswith('n')]
        if self.legend is None:
            self.legend = ["Count rate"]

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
        if self.legend is None:
            self.legend = ["Count rate"]

        title = f"Poisson distribution for count rate (Speed: {kwargs['speed']} m per sec, Acquisition time: {kwargs['time']} sec)"
        filename = "poisson_plot.png"
        self.output_file = os.path.join(OUTPUT_DIR, filename)
        self.__set_ax_params(ax, title)
        ax.plot(x, y, lw=2, color="red")

        plt.legend([self.legend], frameon=False, prop=LEGEND_PARAMS)
        plt.savefig(self.output_file)
        plt.close(figure)
        return self.output_file

    def plot_mcmc_sequence(self, **kwargs) -> str:
        if self.legend is None:
            self.legend = ["Count rate"]

        figure, ax = plt.subplots(figsize=(10, 6))
        title = "Fit of the peak in measurement time-series"
        filename = "mcmc_sequence_plot.png"
        ax.scatter(self.data.index, self.data['pois_data'], label='Measurement data', alpha=0.5)
        self.output_file = os.path.join(OUTPUT_DIR, filename)
        self.__set_ax_params(ax, title, labels={
            "x": "Measurement points along the road",
            "y": "Count rate, cps",
        })
        if kwargs:
            res_burnin = kwargs["burnin_data"]
        else:
            raise KeyError

        for i in range(0, len(res_burnin), 1000):
            green_line = mean_count_rate(
                self.data["x"],
                self.data['y'],
                res_burnin[i, 0],
                res_burnin[i, 1],
                res_burnin[i, 2],
                res_burnin[i, 3]
            )
            ax.plot(green_line, linewidth=2, color=(0, 1, 0, 0.2))

        plt.legend(self.legend, frameon=False, prop=LEGEND_PARAMS)
        plt.savefig(self.output_file)
        plt.close(figure)
        return self.output_file

    @staticmethod
    def __set_ax_params(axes, title: str, labels: dict = None) -> None:
        """
        Set parameters for the plot
        :return: None
        """
        if labels is None:
            labels = LABELS

        axes.spines.top.set_visible(False)
        axes.spines.right.set_visible(False)
        axes.tick_params(axis='both', length=5.0, labelsize=12)
        axes.grid(True, which='major', axis='y', **GRID_PARAMS)
        axes.set_title(title, fontdict=TITLE_PARAMS)
        axes.set_ylabel(labels["y"], fontdict=FONT_PARAMS)
        axes.set_xlabel(labels["x"], fontdict=FONT_PARAMS)
