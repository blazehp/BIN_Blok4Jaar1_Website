import pandas as pd


def parse_excel(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    read_1 = df.iloc[:, 0:1].to_dict()
    read_2 = df.iloc[:, 3:4].to_dict()

    print(read_2)


if __name__ == '__main__':
    parse_excel(r"C:\Users\ruben\Downloads\Course4_dataset_v04.xlsx", "groep5")
