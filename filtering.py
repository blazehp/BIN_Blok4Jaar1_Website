from database_config import db
from database_manager import InputTable, RawBlastTable, _DatabaseManager, \
    ProteinTable


def evaluate(e_value : float, bit_score : float) -> bool:
    """
    Evaluate a blast results viability and decide if it is to be included in filtered blast
    :param e_value:
    :param bit_score:
    :return: True is the result passes all tests, False otherwise
    """
    if e_value < 1e-30:
        return False
    if bit_score < 50:
        return False

    return True

def select_read(qid:str):
    """

    :return: select a specified sequence based on the query id entered
    """
    return

def select_raw() -> tuple:
    """

    :return: A list op tuples with all the contents of RAW blast
    """
    cur = db.cursor()
    cur_select = RawBlastTable(cur)
    contents = cur_select.custom_query("select * from raw_blast;",True)
    #for row in enumerate(contents):
    cur.close()
    return contents

def add_protein():
    cur = db.cursor(dictionary=True)
    cur_select = RawBlastTable(cur)
    contents = cur_select.custom_query("select distinct id , protein_name from raw_blast;",True)
    cur.close()
    already_in = set()
    for row in contents:
        cur = db.cursor(dictionary=True)
        add = ProteinTable(cur)
        if row["protein_name"] not in already_in:
            already_in.add(row["protein_name"])
            add.column['protein_name'] = row["protein_name"]
            add.column["hit_id"] = row['id']
            add.column["protein_function"] = ""
            add.insert()
            db.commit()
            cur.close()
    return