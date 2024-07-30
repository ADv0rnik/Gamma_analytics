import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.analytics.analyser import Analyser
from src.analytics.run_analytics import make_normalization
from src.presentation.plot_maker import make_graph
from src.config import (
    NORMALIZED,
    OUTPUT_DIR
)
from src.utils import zip_files, simulate_coordinates

analytics_router = APIRouter(tags=["analytics"])


@analytics_router.get('/simulate')
async def run_analytics(
        make_plot: bool = False,
        include_angles: bool = False,
        dist: int = 300,
        act: float = 100.0
):
    x_coord, y_coord = await simulate_coordinates(distance=dist)
    analyser = Analyser(
        activity=act,
        coordinates=(x_coord, y_coord),
        include_angles=include_angles,
    )

    csv_filename = os.path.join(OUTPUT_DIR, "simulated_data.csv")
    df = await analyser.construct_data()

    if NORMALIZED:
        df = await make_normalization(df)

    df.to_csv(csv_filename, index=False)
    if make_plot:
        result = make_graph(df)
        result["csv"] = csv_filename
        result_files = list(result.values())
        zip_file = zip_files(result_files)
        return FileResponse(path=zip_file, filename=os.path.basename(zip_file), media_type="application/zip")
    else:
        zip_file = zip_files([csv_filename])
        return FileResponse(path=zip_file, filename=os.path.basename(zip_file), media_type="application/zip")
