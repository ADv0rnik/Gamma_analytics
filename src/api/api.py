import os
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from src.analytics.data_constructor import DataConstructor
from src.analytics.run_analytics import make_normalization
from src.presentation.plot_maker import make_graph
from src.config import (
    NORMALIZED,
    OUTPUT_DIR
)
from src.utils import zip_files, generate_coordinates
from .models import GenerationQueryParams

analytics_router = APIRouter(tags=["analytics"])


@analytics_router.get('/generate')
async def run_analytics(params: GenerationQueryParams = Depends()):
    x_coord, y_coord = await generate_coordinates(distance=params.dist)
    analyser = DataConstructor(
        activity=params.act,
        coordinates=(x_coord, y_coord),
        include_angles=params.include_angles,
        add_speed=params.add_speed,
        speed=params.speed,
        time=params.acq_time
    )

    csv_filename = os.path.join(OUTPUT_DIR, "generated_data.csv")
    df = await analyser.construct_data()

    if NORMALIZED:
        df = await make_normalization(df)

    df.to_csv(csv_filename, index=False)
    if params.make_plot:
        result = make_graph(df)
        result["csv"] = csv_filename
        result_files = list(result.values())
        zip_file = zip_files(result_files)
        return FileResponse(path=zip_file, filename=os.path.basename(zip_file), media_type="application/zip")
    else:
        zip_file = zip_files([csv_filename])
        return FileResponse(path=zip_file, filename=os.path.basename(zip_file), media_type="application/zip")
