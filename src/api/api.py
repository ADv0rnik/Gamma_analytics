import os
import traceback

import pandas as pd
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from src.settings.config import OUTPUT_DIR, CACHE
from src.utils import zip_files, generate_coordinates, create_job_dir
from src.api.run_generation import run_data_generation
from src.api.run_simulation import run_mcmc
from src.tools.profiler import construct_dataframe
from .models import GenerationQueryParams, SimulationQueryParams
from src.exceptions.error_handlers import WrongFileFormatException
from src.exceptions.error_codes import ErrorCodesEnum


analytics_router = APIRouter(tags=["analytics"])

logger = logging.getLogger("gamma")
logger.event_source = __name__


@analytics_router.get('/generate')
async def run_generation(params: GenerationQueryParams = Depends()):
    csv_filename = os.path.join(OUTPUT_DIR, "generated_data.csv")
    x_coord, y_coord = await generate_coordinates(distance=params.dist)
    CACHE["activity"] = params.act
    try:
        if params.make_plot:
            result = await run_data_generation(
                activity=params.act,
                coordinates=(x_coord, y_coord),
                include_angles=params.include_angles,
                add_speed=params.add_speed,
                road_span=params.dist,
                num_points = params.num_points,
                speed=params.speed,
                time=params.acq_time,
                make_plot=True
            )
            result["data"].to_csv(csv_filename, index=False)
            result["data"] = csv_filename
            result_files = list(result.values())
            zip_file = zip_files(result_files)
            logger.info(f"The {os.path.basename(zip_file)} archive has been created")
            return FileResponse(path=zip_file, filename=os.path.basename(zip_file), media_type="application/zip")
        else:
            result = await run_data_generation(
                activity=params.act,
                coordinates=(x_coord, y_coord),
                include_angles=params.include_angles,
                add_speed=params.add_speed,
                road_span=params.dist,
                num_points=params.num_points,
                speed=params.speed,
                time=params.acq_time,
                make_plot=False
            )
            result["data"].to_csv(csv_filename, index=False)
            zip_file = zip_files([csv_filename])
            logger.info(
                f"The archive {os.path.basename(zip_file)} has been created successfully",
                extra={
                    "event_name": "generate_endpoint",
                    "event_source": logger.event_source,
                }
            )
            return FileResponse(path=zip_file, filename=os.path.basename(zip_file), media_type="application/zip")
    except AttributeError as err:
        logger.error(
            f"An {AttributeError.__name__} occurred  while handling the request: {traceback.format_exc(limit=1)}"
        )
        return HTTPException(status_code=500, detail=str(err))


@analytics_router.get('/simulate_generic')
async def run_simulation_from_generic(
        sim_params: SimulationQueryParams = Depends()
):
    try:
        generated_data = pd.read_csv(os.path.join(OUTPUT_DIR, "generated_data.csv"))
    except FileNotFoundError as err:
        logger.error(
            f"An {FileNotFoundError.__name__} occurred  while handling the request: {traceback.format_exc(limit=1)}",
        )
        return HTTPException(status_code=500, detail=str(err))
    else:
        if sim_params.is_specified:
            res = await run_mcmc(
                generated_data,
                simnum=sim_params.sim_number,
                burn_in=sim_params.burn_in,
                init_params=(
                sim_params.init_x_pos, sim_params.init_y_pos, sim_params.init_activity, sim_params.init_bkg)
            )

            return {"result": res}
        else:
            try:
                res = await run_mcmc(
                    generated_data,
                    simnum=sim_params.sim_number,
                    burn_in=sim_params.burn_in
                )
                result_files = list(res.values())
                zip_file = zip_files(result_files)
            except KeyError as err:
                logger.error(f"An {KeyError.__name__} occurred  while handling the request: {traceback.format_exc(limit=1)}")
                return HTTPException(status_code=500, detail=str(err))
            else:
                return FileResponse(
                    path=zip_file,
                    filename=os.path.basename(zip_file),
                    media_type="application/zip"
                )


@analytics_router.post('/simulate_real')
async def run_simulation_from_file(
        sim_params: SimulationQueryParams = Depends(),
        file: UploadFile = File(...)
):
    logger.info(f"Received file for analysis: {file.filename}")
    job_dir = await create_job_dir(file.filename)
    local_filename = os.path.join(job_dir, file.filename)

    if file.filename != "" and file.filename.endswith(".csv"):
        try:
            with open(local_filename, "wb") as f_out:
                buffer = await file.read()
                f_out.write(buffer)

            if not os.path.isfile(local_filename):
                raise WrongFileFormatException(ErrorCodesEnum.WRONG_FILE_FORMAT.value)

            data_from_file = pd.read_csv(local_filename)
            data_for_simulation = await construct_dataframe(data_from_file)

            if sim_params.is_specified:
                res = await run_mcmc(
                    data_for_simulation,
                    simnum=sim_params.sim_number,
                    burn_in=sim_params.burn_in,
                    init_params=(
                        sim_params.init_x_pos, sim_params.init_y_pos, sim_params.init_activity, sim_params.init_bkg)
                )

                return {"result": res}
            else:
                try:
                    res = await run_mcmc(
                        data_for_simulation,
                        simnum=sim_params.sim_number,
                        burn_in=sim_params.burn_in
                    )
                    result_files = list(res.values())
                    zip_file = zip_files(result_files)
                except KeyError as e:
                    logger.error(f"Error while handling request {e}")
                    return HTTPException(status_code=500, detail=str(e))
                else:
                    return FileResponse(
                        path=zip_file,
                        filename=os.path.basename(zip_file),
                        media_type="application/zip"
                    )

        except FileNotFoundError as err:
            logger.error(
                f"An {FileNotFoundError.__name__} occurred  while handling the request: {traceback.format_exc(limit=1)}"
            )
            return HTTPException(status_code=500, detail=f"An {FileNotFoundError.__name__} occurred  while handling the request")
    else:
        logger.error("Wrong file format or file is not received")
        raise WrongFileFormatException(ErrorCodesEnum.WRONG_FILE_FORMAT.value)
