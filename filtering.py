from database_config import db
from database_manager import InputTable, RawBlastTable, _DatabaseManager


def evaluate(e_value : float, bit_score : float) -> bool:
    """
    Evaluate a blast results viabilty and decide if it is to be included in filtered blast
    :param e_value:
    :param bit_score:
    :return: True is the result passes all tests, False otherwise
    """
    if e_value < 1e-10:
        return False
    if bit_score < 1e-10:
        return False

    return True



def select_raw():
    cur = db.cursor()
    cur_select = RawBlastTable(cur)
    contents = cur_select.custom_query("select * from raw_blast;",True)
    for row in enumerate(contents):
        e_value = float(row[2])
        accession_code = row[3]
        org_name = row[4]
        score = row[5]
        description = row[6]
        bit_score = float(row[7])
        identifier = row[8]
        print(org_name,evaluate(e_value,bit_score),identifier ,accession_code)
    cur.close()
if __name__ == "__main__":
    select_raw()
