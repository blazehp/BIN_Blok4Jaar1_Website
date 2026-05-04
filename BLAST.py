import sys

from contourpy.util import data

import parsing as data_frame
import pandas as pd
from pandas import DataFrame
import requests
from requests import Response
import asyncio
from asyncio import Task
from Bio.Blast import NCBIXML, NCBIWWW
from time import sleep
from database_manager import DatabaseManager
from database_manager import db

NCBIWWW.email = "mmj.guillorit@sudent.han.nl"

async def fetch_status(url:str) -> dict:
    print(f"Fetching status for: {url}")
    response :Response = await asyncio.to_thread(requests.get,url,None)
    return {'status': response.status_code, 'url':url}

async def main():
    apple_task: Task[dict] = asyncio.create_task(fetch_status("https://apple.com"))
    google_task: Task[dict] = asyncio.create_task(fetch_status("https://google.com"))
    apple_status : dict = await apple_task
    google_status : dict = await google_task
    print(apple_status)
    print(google_status)



def query(sequence : str ):
    """
    :param sequence:

    :return: return the data stream of an xml file to parse the needed information
    """
    print(f"Querying {sequence}")
    results_handle = NCBIWWW.qblast(program="blastx",database="nr",sequence = sequence,matrix_name='BLOSUM62')
    print('results retrieved')
    return results_handle

def query_parser(data_stream : 'str'):
    return

def query_excel(data_frames : tuple ) -> tuple[str, str]:
    """
    :param data_frames:

    :return: results of each sequence blast into a df
    """
    df_1 = data_frames[0]
    df_2 = data_frames[1]
    for index, row in df_1.iterrows():
        print(f"Querying {df_1.iloc[index, 0]}")
        results_handle = NCBIWWW.qblast("blastx", "nt", df_1.iloc[index][1])

    data = {
        "e_value": "",
        "accession_code": "",
        "protein_name": "",
        "organism_name": "",
    }
    cur = db.cursor()
    dm = DatabaseManager(cur)
    dm.insert("raw_blast", data)
    return




if __name__ == "__main__":
    print(query('ACTGCTGATCGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAG'))

###
""""
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML

sequence = "ACTGCTGATCGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAG"

# Perform a BLAST search
result_handle = NCBIWWW.qblast("blastn", "nt", sequence)

# Parse and print BLAST results
blast_record = NCBIXML.read(result_handle)
for alignment in blast_record.alignments:
    for hsp in alignment.hsps:
        print(f"Alignment Title: {alignment.title}")
        print(f"Alignment Score: {hsp.score}")
"""