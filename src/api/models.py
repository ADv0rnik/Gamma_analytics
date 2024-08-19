from fastapi import Query


class GenerationQueryParams:
    def __init__(
        self,
        make_plot: bool = Query(default=False, description="Switch to True to make a plot"),
        include_angles: bool = Query(default=False, description="Switch to True to include angles"),
        add_speed: bool = Query(default=False, description="Add speed to calculations"),
        dist: int = Query(default=300, description="Calculate the distance between turning points of the vehicle"),
        act: float = Query(default=100.0, description="Predefined activity performed in MBq"),
        speed: float = Query(default=13.9, description="Speed of the vehicle in m per sec"),
        acq_time: int = Query(default=1, description="Acquisition time of the detector in seconds"),
    ):
        self.make_plot = make_plot
        self.include_angles = include_angles
        self.dist = dist
        self.act = act
        self.add_speed = add_speed
        self.speed = speed
        self.acq_time = acq_time