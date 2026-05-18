import sys

from contourpy.util import data

import parsing as data_frame
import pandas as pd
from pandas import DataFrame
import requests
from requests import Response
import asyncio
from asyncio import Task
from Bio import Blast, UniProt
from Bio.Blast import NCBIXML, NCBIWWW
from time import sleep
from database_config import db
from database_manager import InputTable, RawBlastTable
import re
import time

Blast.email = "mmj.guillorit@sudent.han.nl"


def query(sequence : str):
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
    insert_input.insert()
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
    # for alignment in blast_record.alignments:
    #     for hsp in alignment.hsps:
    #         print(f"Alignment: {alignment} evalue {hsp.expect}")
    #
    # for description in blast_record.descriptions:
    #      print(f"Description: {description}")
    return

