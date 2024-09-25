from fastapi import Query


class GenerationQueryParams:
    def __init__(
        self,
        make_plot: bool = Query(default=False, description="Switch to True to make a plot"),
        include_angles: bool = Query(default=False, description="Switch to True to include angles"),
        add_speed: bool = Query(default=False, description="Add speed to calculations"),
        dist: int = Query(default=-300, description="Start point along x axis"),
        act: float = Query(default=100.0, description="Predefined activity performed in MBq"),
        speed: float = Query(default=13.9, description="Speed of the vehicle in m per sec"),
        acq_time: int = Query(default=1, description="Acquisition time of the detector in seconds"),
        num_points: int = Query(default=100, description="Number of points to generate"),
    ):
        self.make_plot = make_plot
        self.include_angles = include_angles
        self.dist = dist
        self.act = act
        self.add_speed = add_speed
        self.speed = speed
        self.acq_time = acq_time
        self.num_points = num_points

class SimulationQueryParams:
    def __init__(
            self,
            sim_number: int = Query(default=10000, description="Number of simulations"),
            is_specified: bool = Query(default=False, description="Switch to True to specify initial parameters"),
            init_x_pos: int = Query(default=0, description="Initial x position of the source"),
            init_y_pos: int = Query(default=50, description="Initial y position of the source"),
            init_activity: int = Query(default=100, description="Initial activity (MBq)"),
            init_bkg: int = Query(default=10, description="Initial background level (cps)"),
    ):
        self.sim_number = sim_number
        self.is_specified = is_specified
        self.init_x_pos = init_x_pos
        self.init_y_pos = init_y_pos
        self.init_activity = init_activity
        self.init_bkg = init_bkg
