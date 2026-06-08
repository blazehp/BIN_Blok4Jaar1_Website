import mysql.connector

import visualisation as vs
from database_config import db
from database_manager import RawBlastTable


def all_species_graph():
    cur = None
    try:
        cur = db.cursor(dictionary=True)
        flblast_db = RawBlastTable(cur)
        result = flblast_db.custom_query("""SELECT organism_name, count(organism_name)
                                            FROM railway.raw_blast t
                                            group by organism_name
                                            order by count(organism_name) desc LIMIT 24
                                         """, returns=True)
        if not result:
            print("no data returned by database")
            return
        print(result)
        entries = {
            row["organism_name"]: row["count(organism_name)"]
            for row in result
        }
        vs.create_piechart(entries, 'organism_name')
    except mysql.connector.Error as e:
        print(f"ran into a mySQirrel error: {e}")
    except Exception as e:
        print(f"ran into an error{e}")
    finally:
        if cur is not None:
            cur.close()


# dummy function for the analysis page please
def species_graph():
    data = [
        ('eukarya', 100, [
            ('fungi', 70, [
                ('Rozellida', 40, []),
                ('Aphelida', 20, []),
                ('Chytridiomyceta', 5, []),
            ]),
            ('animalia', 15, [
                ('Chordate', 6, [
                    ('Mammal', 4, []),
                    ('aves', 1, []),

                ]),
                ('Echinoderm', 4, []),
                ('Hemichordate', 2, []),
                ('Mollusca', 1, []),
                ('Brachiopod', 1, []),
                ('Phoronid', 1, []),
            ]),
        ]),
    ]
    vs.create_sunburst_chart(data, title="Speciestest")


if __name__ == '__main__':
    species_graph()
    all_species_graph()
