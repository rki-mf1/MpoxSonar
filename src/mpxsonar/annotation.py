import json
import subprocess

import pandas as pd

from . import logging


class Annotator:
    def __init__(self, annotator_exe_path=None, SNPSIFT_exe_path=None) -> None:
        # "snpEff/SnpSift.jar"
        self.annotator = annotator_exe_path
        self.SNPSIFT = SNPSIFT_exe_path

    def snpeff_annotate(self, input_vcf, output_vcf, database_name):
        if not self.annotator:
            raise ValueError("Annotator executable path is not provided.")
        # Command to annotate using SnpEff
        command = [f"java -jar {self.annotator} {database_name} {input_vcf} "]
        try:
            # Run the SnpEff annotation
            with open(output_vcf, "w") as output_file:
                result = subprocess.run(
                    command, shell=True, stdout=output_file, stderr=subprocess.PIPE
                )
            # result = subprocess.run(['java', '-version'], stderr=subprocess.STDOUT)
            if result.returncode != 0:
                logging.error("Output failed with exit code: %s", result.returncode)
                print("Error output:", result.stderr.decode("utf-8"))

        except subprocess.CalledProcessError as e:
            logging.error("Annotation failed: %s", e)

    def snpeff_transform_output(self, annotated_vcf, output_tsv):
        if not self.SNPSIFT:
            raise ValueError("SNPSIFT executable path is not provided.")

        # Command to transform SnpEff-annotated VCF to TSV
        transform_command = [
            f"java -jar {self.SNPSIFT} extractFields -s ',' -e '.' {annotated_vcf} 'CHROM' 'POS' 'REF' 'ALT' 'ANN[*].EFFECT' 'ANN[*].IMPACT' "
        ]

        try:
            # Run the transformation command
            with open(output_tsv, "w") as output_file:
                result = subprocess.run(
                    transform_command,
                    shell=True,
                    stdout=output_file,
                    stderr=subprocess.PIPE,
                )
            if result.returncode != 0:
                logging.error("Output failed with exit code: %s", result.returncode)
                print("Error output:", result.stderr.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            logging.error("Output transformation failed: %s", e)


def read_tsv_snpSift(file_path: str) -> pd.DataFrame:
    """
    Process the TSV file from SnpSift, deduplicate the ANN[*].EFFECT column,
    remove values in ANN[*].IMPACT column, and split the records
    to have one effect per row.
    Returns the modified DataFrame.

    Parameters:
        file_path (str): Path to the input TSV file.

    Returns:
        pd.DataFrame: Modified DataFrame with deduplicated ANN[*].EFFECT column and one effect per row.

    Note:

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


def read_sonar_hash(file_path: str):

    with open(file_path, "r") as file:
        data = json.load(file)

    return data


def export_vcf_SonarCMD(refmol, sample_name, output_vcf):
    sonar_cmd = [
        "sonar",
        "match",
        "-r",
        refmol,
        "--sample",
        sample_name,
        "--format",
        "vcf",
        "-o",
        output_vcf,
    ]
    try:
        subprocess.run(sonar_cmd, check=True)
        # print("Sonar command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Sonar match command failed:", e)


def import_annvcf_SonarCMD(sonar_hash, ann_input):

    sonar_cmd = [
        "sonar",
        "import-ann",
        "--sonar-hash",
        sonar_hash,
        "--ann-input",
        ann_input,
    ]
    try:
        subprocess.run(sonar_cmd, check=True)

        # print("Sonar command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Sonar import-ann command failed:", e)
