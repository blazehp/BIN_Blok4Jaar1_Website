import database_manager
import visualisation as vs
from database_config import db
from database_manager import DatabaseManager


def all_species_graph():
    cur = db.cursor()
    dm = DatabaseManager(cur)

