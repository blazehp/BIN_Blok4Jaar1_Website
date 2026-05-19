import pandas as pd
import asyncio
from Bio import Blast, UniProt
from Bio.Blast import NCBIXML, NCBIWWW
from database_config import db
from database_manager import InputTable, RawBlastTable
import re
from parsing import parse_excel


Blast.email = "mmj.guillorit@sudent.han.nl"


async def query(sequence : str):
    """
    :param sequence:
    :return: Query_id , accession_code, description, organism,
    score , e-value, identities,

    """

    print(f"Querying {sequence}")

    #   Initialize DB cursor and raw blast data table
    cur = db.cursor()
    insert_input = InputTable(cur)


    #   query NCBI database and parse out the resulting HTML file
    results_handle = NCBIWWW.qblast(program="blastx", database="nr",
                                    sequence=sequence)
    blast_records = NCBIXML.parse(results_handle)
    blast_record = next(blast_records)

    #recover query identification code
    query_id = blast_record.query_id

    #input query id and sequence into db
    insert_input.column['sequence'] = sequence
    insert_input.column['run_id'] = query_id
    insert_input.update()
    db.commit()
    cur.close()

    #Loop through resulting hits
    for alignment in blast_record.alignments:
        cur = db.cursor()
        insert_raw = RawBlastTable(cur)

        #Find accession_code (2), description (3), organism from hit (4)
        name = re.search(pattern='(\|([.\w\d]*)\|)(.*?)(\[(.*?)\])',
                         string=alignment.title).group(2, 3, 5)
        accession_code = name[0]
        description = name[1]
        organism = name[2]

        #loop through HSP from alignment (n)
        for hsp in alignment.hsps:
            hit_score = hsp.score
            escore = hsp.expect
            bits = hsp.bits
            identities = hsp.identities
            insert_raw.column['accession_code'] = accession_code
            insert_raw.column['description'] = description
            insert_raw.column['organism_name'] = organism
            insert_raw.column['e_value'] = escore
            insert_raw.column['bits'] = bits
            insert_raw.column['identity_perc'] = identities
            insert_raw.column['score'] = hit_score
            insert_raw.column['protein_name'] = "protein name"
            insert_raw.insert()
            db.commit()
            cur.close()

    return


async def fill_db(path:str):
    """
    loop through all sequences and push them to database

    :return:
    """
    data_stream = parse_excel(file_path=path,sheet_name="groep5")

    df_1 = data_stream[0]
    df_2 = data_stream[1]

    sequences = pd.concat([
        df_1.iloc[:, 1],
        df_2.iloc[:, 1]
    ]).dropna().tolist()

    for it in sequences:
        await push_to_db(it)
    return


async def push_to_db(sequence: str):
    """Add sequence to database"""
    cur = db.cursor()
    insert_input = InputTable(cur)
    insert_input.column['sequence'] = sequence
    insert_input.insert()
    db.commit()
    cur.close()
    return


