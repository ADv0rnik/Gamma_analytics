import os

from fastapi import APIRouter, Form
from fastapi.responses import FileResponse

from src.analytics.analyser import Analyser
from src.analytics.run_analytics import make_normalization
from src.presentation.plot_maker import make_graph
from src.config import (
    x_coord,
    y_coord,
    NORMALIZED,
    OUTPUT_DIR
)
from src.utils import zip_files

analytics_router = APIRouter(tags=["analytics"])


@analytics_router.get('/analyze')
async def run_analytics(make_plot: bool = False):
    analyser = Analyser(
        coordinates=(x_coord, y_coord),
        include_angles=True
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
