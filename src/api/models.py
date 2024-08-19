from fastapi import Query


class SimulationQueryParams:
    def __init__(
        self,
        make_plot: bool = Query(default=False, description="Switch to True to make a plot"),
        include_angles: bool = Query(default=False, description="Switch to True to include angles"),
        dist: int = Query(default=300, description="Calculate the distance between turning points of the vehicle"),
        act: float = Query(default=100.0, description="Predefined activity performed in MBq"),
    ):
        self.make_plot = make_plot
        self.include_angles = include_angles
        self.dist = dist
        self.act = act
