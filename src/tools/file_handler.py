import pandas as pd


async def construct_dataframe(raw_data: pd.DataFrame) -> pd.DataFrame:
    raw_data_cropped = pd.concat([raw_data.iloc[:, 3], raw_data.iloc[:, 4], raw_data.iloc[:, -1]], axis=1)
    return raw_data_cropped