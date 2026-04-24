"""`database_manager.py`: Contains utility class(es) and function(s) to
safely and properly manage the database from one place."""
from typing import Literal, Any

from numpy import array as np_array
from mysql.connector.abstracts import MySQLCursorAbstract
from database_config import db

class DatabaseManager:
    """Class containing handful of utility functions to ease managing the database"""
    def __init__(self, cur: MySQLCursorAbstract):
        self.cursor = cur
        
    def select(self, table: Literal["input", "raw_blast", "filtered_blast",
    "protein", "organism"], columns: str = "all"):
        """
        Select all or specified column(s) from selected table.
        
        Parameters:
            table (str): Table to fetch from
            columns (str): Optional param to select all or specific column(s)
        """
        try:
            if columns == "all":
                self.cursor.execute(f"SELECT * FROM {table}")
            else:
                self.cursor.execute(f"SELECT {columns} FROM {table}")
            
            res = []
            while self.cursor.nextset():
                res.append(self.cursor.fetchall())
            res = np_array(res)
            return res.flatten()
        except:
            print("Error selecting value(s) from table")
        
    def insert(self, table: Literal["input", "raw_blast", "filtered_blast",
    "protein", "organism"],
               data: dict[str,
    Any]):
        """
        Insert values for all columns in the specified table.
        
        Parameters:
          table (str): The table name to insert into.
          data (dict[str, Any]): Data to insert into selected table.
          **Keys** is column name and **Values** is value(s) for that column.
        """
        try:
            columns = []
            match table:
                case "input":
                    columns = ["header", "read_1", "read_2"]
                case "raw_blast":
                    columns = ["e_value", "accession_code", "protein_name",
                               "organism_name"]
                case "filtered_blast":
                    columns = ["e_value", "identity_perc", "accession_code"]
                case "protein":
                    columns = ["protein_name", "protein_function", "hit_id"]
                case "organism":
                    columns = ["organism_name", "family", "sex", "species",
                               "hit_id"]
            
            if len(columns) == 0:
                raise ValueError("Table Name not Found")
            
            # Safety fallback for when inputted incorrect column(s)
            for key in data.keys():
                if key not in columns:
                    raise ValueError("Invalid Column name")
            
            cur = db.cursor()
            values = data.values()
            cur.execute(f"INSERT INTO {table} ({','.join(columns)}) VALUES ("
                        f"{','.join(values)})")
        except:
            print("Error inserting into Database")
            
    def custom_query(self, query: str, returns: bool = False):
        """
        Run a custom query into the database.
        
        Parameters:
            query (str): The raw **MYSQL** query
            returns (bool): Rather or not the query returns data
        """
        if returns:
            self.cursor.execute(query)
            res = []
            while self.cursor.nextset():
                res.append(self.cursor.fetchall())
            res = np_array(res)
            return res.flatten()
        
        self.cursor.execute(query)
        return None