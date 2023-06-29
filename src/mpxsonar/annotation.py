import json

import pandas as pd

from . import logging


def read_sonar_hash(file_path: str):

    with open(file_path, "r") as file:
        data = json.load(file)

    return data


def read_tsv_snpSift(file_path: str) -> pd.DataFrame:
    """
    Process the TSV file from SnpSift, deduplicate the ANN[*].EFFECT column,
    remove values in ANN[*].IMPACT column, and split the records
    to have one effect per row. Returns the modified DataFrame.

    Parameters:
        file_path (str): Path to the input TSV file.

    Returns:
        pd.DataFrame: Modified DataFrame with deduplicated ANN[*].EFFECT column and one effect per row.
    """
    try:
        # Read the TSV file into a DataFrame
        df = pd.read_csv(file_path, delimiter="\t")
        df = df.drop(["ANN[*].IMPACT"], axis=1, errors="ignore")
        df.rename(columns={"ANN[*].EFFECT": "EFFECT"}, errors="raise", inplace=True)
        # Deduplicate the values in the ANN[*].EFFECT column
        df["EFFECT"] = df["EFFECT"].str.split(",").apply(set).str.join(",")

        # df['ANN[*].IMPACT'] = ''
        # Split the records into one effect per row
        # df = df.explode('ANN[*].EFFECT')
        # Reset the index
        df = df.reset_index(drop=True)
        # print(df)
        return df
    except KeyError as e:
        logging.error(e)
        logging.error(df.columns)
        raise
    except Exception as e:
        logging.error(e)
        raise
