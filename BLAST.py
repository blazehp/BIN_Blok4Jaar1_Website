import asyncio
import re

import pandas as pd
from Bio import Blast, UniProt
from Bio.Blast import NCBIXML, NCBIWWW

from database_config import db
from database_manager import InputTable, RawBlastTable
from parsing import parse_excel


Blast.email = "mmj.guillorit@sudent.han.nl"


def query(sequence: str, seq_id):
    """
    :param sequence , seq_id:
    :return: Query_id , accession_code, description, organism,
    score , e-value, identities,
    """

    print(f"Querying {sequence}")

    # Initialize DB cursor and raw blast data table
    cur = db.cursor()
    insert_input = InputTable(cur)

    # Query NCBI database and parse out the resulting HTML file
    results_handle = NCBIWWW.qblast(
        program="blastx",
        database="nr",
        sequence=sequence,
    )

    blast_records = NCBIXML.parse(results_handle)
    blast_record = next(blast_records)

    # Recover query identification code
    query_id = blast_record.query_id

    # Input query id and sequence into db
    insert_input.column["run_id"] = query_id
    insert_input.update("id", seq_id)
    db.commit()
    cur.close()

    # Loop through resulting hits
    for alignment in blast_record.alignments:
        cur = db.cursor()
        insert_raw = RawBlastTable(cur)

        # Find accession_code (2), description (3), organism (4)
        name = re.search(
            pattern=r"(\|([.\w\d]*)\|)(.*?)(\[(.*?)\])",
            string=alignment.title,
        ).group(2, 3, 5)

        accession_code = name[0]
        description = name[1]
        organism = name[2]

        # Loop through HSP from alignment (n)
        for hsp in alignment.hsps:
            insert_raw.column["run_id"] = query_id
            insert_raw.column["accession_code"] = accession_code
            insert_raw.column["description"] = description
            insert_raw.column["organism_name"] = organism
            insert_raw.column["e_value"] = hsp.expect
            insert_raw.column["bits"] = hsp.bits
            insert_raw.column["identity_perc"] = hsp.identities
            insert_raw.column["score"] = hsp.score

            insert_raw.column["coverage"] = (
                (hsp.query_span / blast_record.query_length * 100)
                if hsp.query_span > 0
                else 0
            )

            insert_raw.column["protein_name"] = (
                description.replace(organism, "").strip()
            )

            insert_raw.insert()
            db.commit()
            cur.close()

    return query_id


async def fill_db(path):
    """
    Loop through all sequences and push them to database.
    """

    (df_1, df_2) = parse_excel(
        file_path=path,
        sheet_name="groep5",
    )

    sequences = pd.concat(
        [
            df_1.iloc[:, 1],
            df_2.iloc[:, 1],
        ]
    ).dropna().tolist()

    for it in sequences:
        await push_to_db(it)


async def push_to_db(sequence: str):
    """Add sequence to database"""
    cur = db.cursor()
    insert_input = InputTable(cur)

    insert_input.column["sequence"] = sequence
    insert_input.insert()

    db.commit()
    cur.close()
