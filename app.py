# https://flask.palletsprojects.com/en/stable/tutorial/layout/
import asyncio
import os
import time

from dotenv import load_dotenv

from _webcreds import write_creds as write_env
from analysis import species_graph, all_species_graph

load_dotenv()
PORT = os.getenv("PORT")
if PORT is None:
    PORT = 3000

if PORT == 3000:
    write_env()

from quart import Quart, render_template, request
from database_config import db
from BLAST import query
from database_manager import FilteredBlast, RawBlastTable
from quart_wtf import QuartForm, CSRFProtect
from wtforms import StringField
from wtforms.validators import Optional

# Load environment variables into the server
# This is the .env when in development mode
load_dotenv()

app = Quart(__name__)
app.secret_key = os.getenv("CSRF_SECRET_KEY")
csrf = CSRFProtect(app)
PORT = os.getenv("PORT")


@app.route('/')
async def index():
    return await render_template('index.html')


@app.route('/blast')
async def blast():
    return await render_template('blast/index.html')


class BlastFilterForm(QuartForm):
    search_word = StringField("Search", validators=[Optional()])

@app.route('/200seq_blast', methods=["GET", "POST"])
async def seq200blast():
    form = await BlastFilterForm.create_form()
    cur = db.cursor(dictionary=True)

    # RawBlast for now until data is available in FilteredBlast
    flblast_db = RawBlastTable(cur)
    result = flblast_db.select()[:50]
    if await form.validate_on_submit():
        sw = form.search_word.data
        if sw is not None:
            result = flblast_db.custom_query(f"""
            SELECT * FROM raw_blast WHERE protein_name LIKE '%{sw}%' OR organism_name LIKE '%{sw}%' OR description LIKE '%{sw}%';
            """, returns=True)
    columns = list(result[0].keys())
    return await render_template('blast/200_blast.html', data=result, columns=columns, form=form)

@app.route('/self-blast')
async def self_blast():
    return await render_template('/blast/self_blast.html')

@app.route('/docs')
async def docs():
    return await render_template('tech_doc.html')


@app.route('/analysis')
async def analysis():
    species_graph()
    all_species_graph()
    return await render_template('analysis.html')


# Admin Routes
@app.route('/admin', methods=["GET", "POST"])
async def admin():
    tables = ["input", "raw_blast", "filtered_blast", "protein", "organism"]
    current_table = request.args.get("table", "input")

    if current_table not in tables:
        current_table = "input"

    cursor = db.cursor()

    # Fetch data
    cursor.execute(f"SELECT * FROM {current_table}")
    rows_raw = cursor.fetchall()

    # Extract column names
    columns = [desc[0] for desc in cursor.description]

    # Convert rows --> dicts (IMPORTANT)
    rows = []
    for row in rows_raw:
        row_dict = {}
        for index, col in enumerate(columns):
            row_dict[col] = row[index]
        rows.append(row_dict)

    # db.close()
    return await render_template("admin.html", tables=tables,
                                 current_table=current_table, columns=columns,
                                 rows=rows)


def blast_querying():
    cursor = db.cursor()

    # Fetch data
    cursor.execute(f"SELECT id ,sequence FROM input WHERE run_id is NULL")
    non_blasted_sequences = cursor.fetchall()
    for (ids, seq) in non_blasted_sequences:
        print(f'Running blast for {ids}')
        query(seq, ids)
        # Extra time than suggested time to reduce chance of blocking
        print("Pausing...")
        time.sleep(20.0)

    cursor.close()
    return


@app.route('/run_blast', methods=["GET"])
async def run_blast():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, blast_querying)
    return "Blasting..."


@app.route("/_creds", methods=["GET"])
async def _creds():
    db_creds = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DEV_DB_HOST"),
        "port": os.getenv("DEV_DB_PORT"),
        "database": os.getenv("DB_DATABASE"),
        "pool_name": os.getenv("DB_POOL_NAME"),
        "pool_size": int(os.getenv("DB_POOL_SIZE")),
        "csrf_secret_key": os.getenv("CSRF_SECRET_KEY"),
    }
    return db_creds


def delete_table(cur, table_name: str = "all"):
    """
    DANGER: Only run when need to do a **full wipe**!
    Delete all or inputted table(s) in the database.
    """
    if table_name == "all":
        cur.execute("DROP TABLE IF EXISTS organism")
        cur.execute("DROP TABLE IF EXISTS protein")
        cur.execute("DROP TABLE IF EXISTS filtered_blast")
        cur.execute("DROP TABLE IF EXISTS raw_blast")
        cur.execute("DROP TABLE IF EXISTS input")

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
                    sequence
                    longtext
                    NOT
                    NULL,
                    run_id
                    varchar
                (
                    255
                ),
                    -- Constraints
                    UNIQUE
                (
                    run_id
                )
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
                    run_id
                    varchar
                (
                    255
                ) NOT NULL,

                    e_value varchar
                (
                    255
                ) NOT NULL,
                    accession_code varchar
                (
                    255
                ) NOT NULL,
                    protein_name varchar
                (
                    255
                ) NOT NULL,
                    organism_name varchar
                (
                    255
                ) NOT NULL,
                    score float
                (
                    24
                ) NOT NULL,
                    description varchar
                (
                    2500
                ) NOT NULL,
                    bits float
                (
                    24
                ) NOT NULL,
                    identity_perc float
                (
                    24
                ) NOT NULL,
                    converage float
                (
                    24
                ),
                    -- Constraints
                    CONSTRAINT query_id FOREIGN KEY
                (
                    run_id
                )
                    REFERENCES input
                (
                    run_id
                )
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
                    run_id
                    varchar
                (
                    255
                ) NOT NULL,

                    e_value varchar
                (
                    255
                ) NOT NULL,
                    accession_code varchar
                (
                    255
                ) NOT NULL,
                    protein_name varchar
                (
                    255
                ) NOT NULL,
                    organism_name varchar
                (
                    255
                ) NOT NULL,
                    score float
                (
                    24
                ) NOT NULL,
                    description varchar
                (
                    2500
                ) NOT NULL,
                    bits float
                (
                    24
                ) NOT NULL,
                    identity_perc float
                (
                    24
                ) NOT NULL,
                    converage float
                (
                    24
                ),
                    -- Constraints
                    CONSTRAINT q_id FOREIGN KEY
                (
                    run_id
                )
                    REFERENCES input
                (
                    run_id
                )
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
                    varchar
                (
                    255
                ) NOT NULL,
                    protein_function varchar
                (
                    2500
                ),
                    hit_id int
                (
                    255
                ) NOT NULL,
                    -- Constraints
                    CONSTRAINT prot_blast_hit FOREIGN KEY
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
                    varchar
                (
                    255
                ) NOT NULL,
                    family varchar
                (
                    255
                ),
                    sex varchar
                (
                    255
                ),
                    species varchar
                (
                    255
                ) NOT NULL,
                    hit_id int
                (
                    255
                ) NOT NULL,
                    -- Constraints
                    CONSTRAINT org_blast_hit FOREIGN KEY
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
