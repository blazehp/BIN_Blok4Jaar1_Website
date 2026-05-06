import sys

from contourpy.util import data

import parsing as data_frame
import pandas as pd
from pandas import DataFrame
import requests
from requests import Response
import asyncio
from asyncio import Task
from Bio import Blast
from Bio.Blast import NCBIXML, NCBIWWW
from time import sleep
from database_manager import DatabaseManager
from database_manager import db
import re
import time

Blast.email = "mmj.guillorit@sudent.han.nl"


def extract_organism(hit_def: str) -> str:
    return hit_def




def query(sequence : str ):
    """
    :param sequence:

    :return: returns a string
    """
    print(f"Querying {sequence}")
    results_handle = NCBIWWW.qblast(program="blastx",database="nr",sequence = sequence)
    #results retrieved
    blast_records = NCBIXML.parse(results_handle)
    blast_record = next(blast_records)
    print(blast_record)
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            print(f"Hit Title: {alignment.title}")
            print(f"Hit Score: {hsp.escore}")
            print(f"Hit Type : {hsp.hit_type}")
            print(f"Hit escore: {hsp.escore}")
    return








def query_excel(data_frames : tuple ) -> dict:
    """
    :param data_frames:

    :return: results of each sequence blast into a df
    """
    df_1 = data_frames[0]
    df_2 = data_frames[1]
    template = {
        "e_value": "",
        "accession_code": "",
        "protein_name": "",
        "organism_name": "",
    }
    for index, row in (df_1.iterrows(), df_2.iterrows()):
        print(f"Querying {df_1.iloc[index, 0]}")
        results_handle = NCBIWWW.qblast("blastx", "nt", df_1.iloc[index][1])

    cur = db.cursor()
    dm = DatabaseManager(cur)
    dm.insert("raw_blast", template)
    return




if __name__ == "__main__":
    queried = query('ACATTTGCTTCTGACACAACTGTGTTCACTAGCAACCTCAAACAGACACCATGGTGCATCTGACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTGAACGTGGATGAAGTTGGTGGTGAGGCCCTGGGCAGGCTGCTGGTGGTCTACCCTTGGACCCAGAGGTTCTTTGAGTCCTTTGGGGATCTGTCCACTCCTGATGCTGTTATGGGCAACCCTAAGGTGAAGGCTCATGGCAAGAAAGTGCTCGGTGCCTTTAGTGATGGCCTGGCTCACCTGGACAACCTCAAGGGCACCTTTGCCACACTGAGTGAGCTGCACTGTGACAAGCTGCACGTGGATCCTGAGAACTTCAGGCTCCTGGGCAACGTGCTGGTCTGTGTGCTGGCCCATCACTTTGGCAAAGAATTCACCCCACCAGTGCAGGCTGCCTATCAGAAAGTGGTGGCTGGTGTGGCTAATGCCCTGGCCCACAAGTATCACTAAGCTCGCTTTCTTGCTGTCCAATTTCTATTAAAGGTTCCTTTGTTCCCTAAGTCCAACTACTAAACTGGGGGATATTATGAAGGGCCTTGAGCATCTGGATTCTGCCTAATAAAAAACATTTATTTTCATTGCAA')

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


"""
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
    """