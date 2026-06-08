from database_config import db
from database_manager import InputTable, RawBlastTable, _DatabaseManager, \
    ProteinTable, FilteredBlast, OrganismTable
from Bio import Entrez , SeqIO
import requests
from time import sleep

from retrieve_protein import organism

Entrez.email = "mmj.guillorit@student.han.nl"

def evaluate(e_value : float, bit_score : float,score : int, identity : int) -> bool:
    """
    Evaluate a blast results viability and decide if it is to be included in filtered blast
    :param identity:
    :param e_value:
    :param bit_score:
    :param score:
    :return: True is the result passes all tests, False otherwise
    """
    if e_value < 1e-30:
        return False
    if bit_score < 50:
        return False
    if score < 50:
        return False
    if identity < 50:
        return False
    return True


def select_read(qid:str):
    """

    :return: select a specified sequence based on the query id entered
    """
    cur = db.cursor(dictionary=True)
    cur_select = RawBlastTable(cur)
    contents = cur_select.custom_query("select * from raw_blast where run_id = qid;", True)
    # for row in enumerate(contents):
    cur.close()
    return contents


def filter_raw() -> tuple:
    """

    :return: A list op dictionaries with all the contents of RAW blast
    """
    cur = db.cursor(dictionary=True)
    cur_select = RawBlastTable(cur)
    contents = cur_select.custom_query("select * from raw_blast;",True)
    cur.close()
    cur = db.cursor(dictionary=True)
    cur_add = FilteredBlast(cur)
    for row in contents:
        if row["run_id"] == '-':
            continue
        if evaluate(float(row['e_value']),float(row['bits']),int(row['score']),int(row['identity_perc'])):
            cur_add.column['run_id'] = row['run_id']
            cur_add.column['e_value'] = row["e_value"]
            cur_add.column['accession_code'] = row["accession_code"]
            cur_add.column['protein_name'] = row["protein_name"]
            cur_add.column['organism_name'] = row["organism_name"]
            cur_add.column['score'] = row["score"]
            cur_add.column['bits'] = row["bits"]
            cur_add.column['description'] = row["description"]
            cur_add.column['identity_perc'] = row["identity_perc"]
            cur_add.column['coverage'] = 0
            cur_add.insert()
    db.commit()
    cur.close()

    return contents


def seek_protein():

    cur = db.cursor(dictionary=True)
    cur_select = RawBlastTable(cur)
    contents = cur_select.custom_query("select distinct id , protein_name, accession_code from filtered_blast where accession_code != '-' ;",True)
    cur.close()
    already_in = set()

    for row in contents:

        cur = db.cursor(dictionary=True)
        add = ProteinTable(cur)

        if row["protein_name"] in already_in:
            result = add.custom_query(
                "SELECT hit_id FROM protein WHERE protein_name = %s;",
                params=(row['protein_name'],),
                returns=True
            )
            hit_ids = result[0]["hit_id"].split(",")
            if str(row["id"]) not in hit_ids:
                hit_ids.append(str(row["id"]))
            updated = ",".join(hit_ids)
            add.custom_query(
                "UPDATE protein SET hit_id = %s WHERE protein_name = %s;",
                params=(updated, row['protein_name']),
                returns=False
            )
            db.commit()

        else:
            already_in.add(row["protein_name"])
            add.column["protein_name"] = row["protein_name"]
            add.column["hit_id"] = str(row["id"])
            add.column["protein_function"] = get_protein_function(
                row["protein_name"])
            add.insert()
            db.commit()
            sleep(0.33)

        cur.close()
    return


def get_protein_function(protein_name: str) -> str | None:
    """
    Look up a protein's function using the UniProt REST API.

    Args:
        protein_name: Common name or gene name (e.g. "BRCA1", "insulin", "p53")

    Returns:
        A string describing the protein's function, or None if not found.
    """
    base = "https://rest.uniprot.org/uniprotkb"

    # search for the protein and grab the top result
    try:
        search_resp = requests.get(
            f"{base}/search",
            params={
                "query": protein_name,
                "fields": "accession",
                "format": "json",
                "size": 1,
            },
        )
        search_resp.raise_for_status()

        results = search_resp.json().get("results", [])
        if not results:
            return "NO DATA ON THIS PROTEIN"

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return 'SEARCH ERROR'
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        return 'SEARCH ERROR'
    except requests.exceptions.Timeout as e:
        print(f"Request timed out: {e}")
        return 'Time out request'
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return 'SEARCH ERROR'

    accession = results[0]["primaryAccession"]

    # fetch the full entry to extract the function annotation
    entry_resp = requests.get(
        f"{base}/{accession}",
        params={"fields": "cc_function", "format": "json"},
    )
    entry_resp.raise_for_status()

    comments = entry_resp.json().get("comments", [])
    for comment in comments:
        if comment.get("commentType") == "FUNCTION":
            texts = [text["value"] for text in comment.get("texts", [])]
            return " ".join(texts)

    return "FAILED API CALL"


def seek_tax():
    # Pre-populate already_in from existing DB records to survive restarts
    cur = db.cursor(dictionary=True)
    existing = OrganismTable(cur).custom_query(
        "SELECT organism_name FROM organism;",
        returns=True
    )
    already_in = {row["organism_name"] for row in existing}

    # Fetch distinct organisms to process
    blast_cur = RawBlastTable(cur)
    contents = blast_cur.custom_query(
        "SELECT DISTINCT id, organism_name, accession_code "
        "FROM filtered_blast WHERE accession_code != '-';",
        returns=True
    )
    cur.close()

    for row in contents:
        organism = row["organism_name"]
        row_id = str(row["id"])

        cur = db.cursor(dictionary=True)
        add = OrganismTable(cur)

        try:
            if organism in already_in:
                result = add.custom_query(
                    "SELECT hit_id FROM organism WHERE organism_name = %s;",
                    params=(organism,),
                    returns=True
                )
                if not result:
                    print(f"Warning: '{organism}' in already_in but not found in DB, skipping.")
                    continue

                hit_ids = result[0]["hit_id"].split(",")

                # Guard against duplicate IDs across runs
                if row_id not in hit_ids:
                    hit_ids.append(row_id)
                    updated = ",".join(hit_ids)
                    add.custom_query(
                        "UPDATE organism SET hit_id = %s WHERE organism_name = %s;",
                        params=(updated, organism),
                        returns=False
                    )
                    db.commit()

            else:
                print(f"New organism: {organism}")
                already_in.add(organism)

                try:
                    tax = get_taxonomy(row["accession_code"])
                except (RuntimeError, ValueError) as e:
                    print(f"Skipping '{organism}': taxonomy fetch failed — {e}")
                    continue

                add.column["organism_name"] = organism
                add.column["family"] = tax["family"]
                add.column["genus"] = tax["genus"]
                add.column["species"] = tax["species"]
                add.column["hit_id"] = row_id
                print(organism,tax["family"],tax["genus"],tax["species"],row_id)
                add.insert()
                db.commit()
                cur.close()

                # Respect NCBI rate limit (max 3 requests/sec)
                sleep(0.34)

        except Exception as e:
            print(f"Unexpected error processing row {row}: {e}")
            db.rollback()

        finally:
            cur.close()



def get_taxonomy(taxid: str ) -> dict:
    """
    Retrieve taxonomy information from NCBI Taxonomy.

    Parameters
    ----------
    taxid : str
        NCBI Taxonomy ID (e.g. "9606" for Homo sapiens)

    Returns
    -------
    dict
        {
            "taxid": ...,
            "organism_name": ...,
            "species": ...,
            "genus": ...,
            "family": ...,
            "class": ...,
        }

    Raises
    ------
    ValueError
        If no record is found for the given taxid
    RuntimeError
        If the NCBI request fails
    """

    try:
        with Entrez.efetch(db="taxonomy", id=taxid, retmode="xml") as handle:
            records = Entrez.read(handle)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch taxonomy for taxid '{taxid}': {e}") from e

    if not records:
        raise ValueError(f"No taxonomy record found for taxid '{taxid}'")

    record = records[0]

    taxonomy = {
        "taxid": record.get("TaxId") or "No TaxId Found",
        "organism_name": record.get(
            "ScientificName") or "No Organism Name Found",
        "species": "No Species Found",
        "genus": "No Genus Found",
        "family": "No Family Found",
        "class": "No Class Found",
    }

    # If the queried taxon itself is species rank, capture it directly
    if record.get("Rank") == "species":
        scientific_name = record.get("ScientificName")
        if scientific_name:
            taxonomy["species"] = scientific_name

    # Walk lineage to fill in ranks
    for node in record.get("LineageEx", []):
        rank = node.get("Rank")
        name = node.get("ScientificName")

        if not rank or not name:
            continue

        if rank == "species" and taxonomy["species"] == "No Species Found":
            taxonomy["species"] = name
        elif rank == "genus":
            taxonomy["genus"] = name
        elif rank == "family":
            taxonomy["family"] = name
        elif rank == "class":
            taxonomy["class"] = name

    return taxonomy


seek_tax()