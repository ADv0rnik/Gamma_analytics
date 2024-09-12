import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from src.config import OUTPUT_DIR
from src.utils import zip_files, generate_coordinates
from src.api.run_generation import run_data_generation
from .models import GenerationQueryParams, SimulationQueryParams

analytics_router = APIRouter(tags=["analytics"])


@analytics_router.get('/generate')
async def run_analytics(params: GenerationQueryParams = Depends()):
    csv_filename = os.path.join(OUTPUT_DIR, "generated_data.csv")
    x_coord, y_coord = await generate_coordinates(distance=params.dist)
    try:
        if params.make_plot:
            result = await run_data_generation(
                activity=params.act,
                coordinates=(x_coord, y_coord),
                include_angles=params.include_angles,
                add_speed=params.add_speed,
                road_span=params.dist,
                speed=params.speed,
                time=params.acq_time,
                make_plot=True
            )
            result["data"].to_csv(csv_filename, index=False)
            result["data"] = csv_filename
            result_files = list(result.values())
            zip_file = zip_files(result_files)
            return FileResponse(path=zip_file, filename=os.path.basename(zip_file), media_type="application/zip")
        else:
            result = await run_data_generation(
                activity=params.act,
                coordinates=(x_coord, y_coord),
                include_angles=params.include_angles,
                add_speed=params.add_speed,
                road_span=params.dist,
                speed=params.speed,
                time=params.acq_time,
                make_plot=False
            )
            result["data"].to_csv(csv_filename, index=False)
            print(result)
            zip_file = zip_files([csv_filename])
            return FileResponse(path=zip_file, filename=os.path.basename(zip_file), media_type="application/zip")
    except AttributeError as e:
        return HTTPException(status_code=500, detail=str(e))

@analytics_router.get('/simulate')
async def run_simulation(sim_params: SimulationQueryParams = Depends()):
    pass
