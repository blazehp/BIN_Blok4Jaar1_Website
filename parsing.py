import pandas as pd
from pandas import DataFrame


def parse_excel(file_path: str, sheet_name: str) -> tuple[
    DataFrame, DataFrame]:
    """""Parse an excel file into a dictionary"""
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    read_1 = df.iloc[:, 0:2]
    read_2 = df.iloc[:, 3:5]

    return read_1, read_2


if __name__ == '__main__':
    example = parse_excel(
        "C:\\Users\\maxim\\Downloads\\Course4_dataset_v04.xlsx", "groep5")
print(example)
