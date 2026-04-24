# https://flask.palletsprojects.com/en/stable/tutorial/layout/

from flask import Flask, render_template, redirect
import os
from dotenv import load_dotenv
from database_config import db

# Load environment variables into the server
# This is the .env when in development mode
load_dotenv()

app = Flask(__name__)
PORT = os.getenv("PORT")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/blast')
def blast():
    print(f"Is connected? {db.is_connected()}")
    return render_template('blast.html')


@app.route('/docs')
def docs():
    return render_template('tech_doc.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


def delete_table(cur, table_name: str = "all"):
    """
    DANGER: Only run when need to do a **full wipe**!
    Delete all or inputted table(s) in the database.
    """
    if table_name == "all":
        cur.execute("DROP TABLE IF EXISTS input")
        cur.execute("DROP TABLE IF EXISTS raw_blast")
        cur.execute("DROP TABLE IF EXISTS protein")
        cur.execute("DROP TABLE IF EXISTS organism")
        cur.execute("DROP TABLE IF EXISTS filtered_blast")
    else:
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")


if __name__ == '__main__':
    cur = db.cursor()
    # Create Database Tables on server launch
    
    # -- Input table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS input
                (
                    id
                    int
                    PRIMARY
                    KEY
                    AUTO_INCREMENT,
                    header
                    varchar
                (
                    255
                ) UNIQUE NOT NULL,
                    read_1 text NOT NULL,
                    read_2 text NOT NULL
                    );
                """)
    
    # -- Raw Blast table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS raw_blast
                (
                    id
                    int
                    PRIMARY
                    KEY
                    AUTO_INCREMENT,
                    e_value
                    text
                    NOT
                    NULL,
                    accession_code
                    text
                    NOT
                    NULL,
                    protein_name
                    text
                    NOT
                    NULL,
                    organism_name
                    text
                    NOT
                    NULL
                );
                """)
    
    # -- Filtered Blast table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS filtered_blast
                (
                    id
                    int
                    PRIMARY
                    KEY
                    AUTO_INCREMENT,
                    e_value
                    text
                    NOT
                    NULL,
                    identity_perc
                    int
                    NOT
                    NULL,
                    accession_code
                    varchar
                (
                    255
                ) UNIQUE NOT NULL
                    );
                """)
    
    # -- Protein table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS protein
                (
                    id
                    int
                    PRIMARY
                    KEY
                    AUTO_INCREMENT,
                    protein_name
                    text
                    NOT
                    NULL,
                    protein_function
                    text
                    NOT
                    NULL,
                    hit_id
                    int
                    NOT
                    NULL,
                    -- Constraints
                    CONSTRAINT
                    prot_blast_hit
                    FOREIGN
                    KEY
                (
                    hit_id
                )
                    REFERENCES filtered_blast
                (
                    id
                )
                    );
                """)
    
    # -- Organism table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS organism
                (
                    id
                    int
                    PRIMARY
                    KEY
                    AUTO_INCREMENT,
                    organism_name
                    text
                    NOT
                    NULL,
                    family
                    text
                    NOT
                    NULL,
                    sex
                    text
                    NOT
                    NULL,
                    species
                    text
                    NOT
                    NULL,
                    hit_id
                    int
                    NOT
                    NULL,
                    -- Constraints
                    CONSTRAINT
                    org_blast_hit
                    FOREIGN
                    KEY
                (
                    hit_id
                )
                    REFERENCES filtered_blast
                (
                    id
                )
                    );
                """)
    
    # Close connection after table creation
    cur.close()
    
    # Start Server
    app.run(debug=PORT == "3000", port=PORT)
