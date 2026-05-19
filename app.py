# https://flask.palletsprojects.com/en/stable/tutorial/layout/

from flask import Flask, render_template, redirect, request
import os
from dotenv import load_dotenv
from database_config import db
from BLAST import query
from asyncio import sleep

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

# Admin Routes
@app.route('/admin', methods=["GET", "POST"])
def admin():
    tables = ["input", "raw_blast", "filtered_blast", "protein", "organism"]
    current_table = request.args.get("table", "input")
    
    # Safety check (prevents injection via ?table=...)
    if current_table not in tables:
        current_table = "input"
    
    cursor = db.cursor()
    
    # Fetch data
    cursor.execute(f"SELECT * FROM {current_table}")
    rows_raw = cursor.fetchall()
    
    # Extract column names
    columns = [desc[0] for desc in cursor.description]
    
    # Convert rows → dicts (IMPORTANT)
    rows = []
    for r in rows_raw:
        row_dict = {}
        for i, col in enumerate(columns):
            row_dict[col] = r[i]
        rows.append(row_dict)
    
    # db.close()
    return render_template("admin.html", tables=tables,
                           current_table=current_table, columns=columns,
                           rows=rows)

@app.route('/run_blast', methods=["GET"])
async def run_blast():
    cursor = db.cursor()

    # Fetch data
    cursor.execute(f"SELECT id ,sequence FROM input WHERE run_id is NULL")
    non_blasted_sequences = cursor.fetchall()
    for (ids, seq) in non_blasted_sequences:
        print(f'running blast for {ids}')
        await query(seq)
        await sleep(10.0)

    return


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
    delete_table(cur)
    
    # -- Input table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS input (
                    id int PRIMARY KEY AUTO_INCREMENT,
                    sequence longtext NOT NULL,
                    run_id varchar(255),
                    );
                """)

    # -- Raw Blast table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS raw_blast (
                    id int PRIMARY KEY AUTO_INCREMENT,
                    run_id varchar(255) NOT NULL,

                    e_value varchar(255) NOT NULL,
                    accession_code varchar(255) NOT NULL,
                    protein_name varchar(255) NOT NULL,
                    organism_name text NOT NULL,
                    score float NOT NULL,
                    desccription text NOT NULL,
                    bits float NOT NULL,
                    identity_perc int NOT NULL,
                    -- Constraints
                    CONSTRAINT query_id FOREIGN KEY(run_id)
                    REFERENCES input(run_id)
                );
                """)

    # -- Filtered Blast table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS filtered_blast (
                    id int PRIMARY KEY AUTO_INCREMENT,
                    run_id varchar(255) NOT NULL,
                    e_value varchar(255) NOT NULL,
                    accession_code varchar(255) NOT NULL,
                    protein_name varchar(255) NOT NULL,
                    organism_name text NOT NULL,
                    score float NOT NULL,
                    desccription text NOT NULL,
                    bits float NOT NULL,
                    identity_perc int NOT NULL,
                    -- Constraints
                    CONSTRAINT q_id FOREIGN KEY(run_id)
                    REFERENCES input(run_id)
                );
                """)

    # -- Protein table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS protein (
                    id int PRIMARY KEY AUTO_INCREMENT,
                    protein_name text NOT NULL,
                    protein_function text NOT NULL,
                    hit_id int NOT NULL,
                    -- Constraints
                    CONSTRAINT prot_blast_hit FOREIGN KEY(hit_id)
                    REFERENCES filtered_blast(id)
                    );
                """)

    # -- Organism table
    cur.execute("""
                CREATE TABLE IF NOT EXISTS organism (
                    id int PRIMARY KEY AUTO_INCREMENT,
                    organism_name varchar(255) NOT NULL,
                    family text NOT NULL,
                    sex text NOT NULL,
                    species text NOT NULL,
                    hit_id int NOT NULL,
                    -- Constraints
                    CONSTRAINT org_blast_hit FOREIGN KEY (hit_id)
                    REFERENCES filtered_blast(id)
                    );
                """)

    # Close connection after table creation
    cur.close()
    
    # Start Server
    app.run(debug=PORT == "3000", port=PORT)
