import pandas as pd


def parse_excel(file_path: str, sheet_name: str) -> dict[str, str]:
    """""Parse a excel file into a dictionary"""
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    read_1 = df.iloc[:, 0:2]
    read_2 = df.iloc[:, 3:5]
    dict_1 = read_1.set_index(0)[1].to_dict()
    dict_2 = read_2.set_index(3)[4].to_dict()

    return {**dict_1, **dict_2}


if __name__ == '__main__':
    example = parse_excel(
        r"C:\Users\ruben\Downloads\Course4_dataset_v04.xlsx", "groep5")
    print(type(example))
