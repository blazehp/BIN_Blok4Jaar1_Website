import visualisation as vs
from database_config import db
from database_manager import RawBlastTable


def all_species_graph():
    cur = db.cursor()
    flblast_db = RawBlastTable(cur)
    result = flblast_db.custom_query("""SELECT organism_name, count(organism_name)
                                   FROM railway.raw_blast t
                                   group by organism_name
                                   order by count(organism_name) desc LIMIT 501
                                """)


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
