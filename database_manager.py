"""`database_manager.py`: Contains utility class(es) and function(s) to
safely and properly manage the database from one place."""
from typing import Literal, Any
import warnings

from mysql.connector.abstracts import MySQLCursorAbstract

class _DatabaseManager:
    """Class containing handful of utility functions to ease managing the database"""
    
    def __init__(self, cur: MySQLCursorAbstract, table: Literal["input",
    "raw_blast", "filtered_blast", "protein", "organism"],
                 data: dict[str,Any]):
        self.cursor = cur
        self.table = table
        self.data = data
    
    def select(self, columns: str = "all"):
        """
        Select all or specified column(s) from selected table.
        
        Parameters:
            columns (str): Optional param to select all or specific column(s)
        """
        try:
            if columns == "all":
                self.cursor.execute(f"SELECT * FROM {self.table};")
            else:
                self.cursor.execute(f"SELECT {columns} FROM {self.table};")
            return self.cursor.fetchall()
        except:
            print("Error selecting value(s) from table")
    
    def insert(self):
        """Insert values for all columns in table."""
        # try:
        columns = ','.join([key for key in self.data.keys()])
            # Using placeholders + tuple data to allow None values
<<<<<<< Updated upstream
        value_placeholders = ','.join([f"%s" for _ in self.data.keys()])
        values = tuple(self.data.values())
        if None in values:
            raise ValueError
        query = f"INSERT INTO {self.table} ({columns}) VALUES ({value_placeholders})"
        self.cursor.execute(query, params=values)
        # except ValueError:
        #      print("Check inputted values. Cannot insert NONE values")
        # except:
        #      print("Error inserting into Database")
=======
            value_placeholders = ','.join([f"%s" for _ in self.data.keys()])
            values = tuple(self.data.values())
            if None in values:
                warnings.warn("Inserting NONE values may cause errors")
            query = f"INSERT INTO {self.table} ({columns}) VALUES ({value_placeholders})"
            self.cursor.execute(query, params=values)
        except ValueError:
            print("Check inputted values.")
        except:
            print("Error inserting into Database; ")
>>>>>>> Stashed changes
    
    def update(self, position, pvalue):
        """
        Update columns in table.
        
        **NOTE**: If a column's value is `None`, it will be omitted from the
        query.
        
        Parameters:
            position (str): The column name to update at
            pvalue (Any): The value of the column.
            
        """
        # Update columns
        for (column, value) in self.data.items():
            # Remove empty keys. There are not meant to be updated
            # *This was before, a pop. But that caused dict size change
            # during runtime.
            if self.data[column] is None:
                continue
            
            if type(value) == int or type(value) == float:
                query = (f"UPDATE {self.table} SET {column} = {value} WHERE "
                         f"{position} = {pvalue}")
            else:
                query = (f"UPDATE {self.table} SET {column} = '{value}' WHERE"
                         f" {position} = {pvalue}")
                
            self.cursor.execute(query)
        return None
    
    def delete(self, record_id: int):
        """
        Delete a record from the table
        
        Parameters:
            record_id (int): The id of the record to delete
        """
        query = f"DELETE FROM {self.table} WHERE id = {record_id}"
        self.cursor.execute(query)
        return None
    
    def custom_query(self, query: str, returns: bool = False):
        """
        Run a custom query into the database.
        
        Parameters:
            query (str): The raw **MYSQL** query
            returns (bool): weither or not the query returns data
        """
        if returns:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        
        self.cursor.execute(query)
        return None
    
class InputTable(_DatabaseManager):
    def __init__(self, cur: MySQLCursorAbstract):
        self.column: dict[Literal["sequence", "run_id"], Any] = {
            "sequence": None,
            "run_id": None
        }
        super().__init__(cur, "input", self.column)
        
class RawBlastTable(_DatabaseManager):
    def __init__(self, cur: MySQLCursorAbstract):
        self.column: dict[Literal["run_id","e_value","identity_perc", "accession_code",
        "protein_name","description", "organism_name","score","bits","coverage"],
        Any] = {
            "run_id": None,
            "e_value": None,
            "identity_perc": None,
            "accession_code": None,
            "protein_name": None,
            "organism_name": None,
            "score": None,
            "description": None,
            "bits": None,
            "coverage": None,
        }
        super().__init__(cur, "raw_blast", self.column)
        
class FilteredBlast(_DatabaseManager):
    def __init__(self, cur: MySQLCursorAbstract):
        self.column: dict[Literal["run_id","e_value","identity_perc", "accession_code",
        "protein_name","description", "organism_name","score","bits","coverage"],
        Any] = {
            "run_id": None,
            "e_value": None,
            "identity_perc": None,
            "accession_code": None,
            "protein_name": None,
            "organism_name": None,
            "score": None,
            "description": None,
            "bits": None,
            "coverage": None,
        }
        super().__init__(cur, "filtered_blast", self.column)
        
class ProteinTable(_DatabaseManager):
    def __init__(self, cur: MySQLCursorAbstract):
        self.column: dict[Literal["protein_name", "protein_function",
        "hit_id"],
        Any] = {
            "protein_name": None,
            "protein_function": None,
            "hit_id": None
        }
        super().__init__(cur, "protein", self.column)

class OrganismTable(_DatabaseManager):
    def __init__(self, cur: MySQLCursorAbstract):
        self.column: dict[Literal["organism_name", "family", "sex",
        "species", "hit_id"], Any] = {
            "organism_name": None,
            "family": None,
            "sex": None,
            "species": None,
            "hit_id": None
        }
        super().__init__(cur, "organism", self.column)
        
