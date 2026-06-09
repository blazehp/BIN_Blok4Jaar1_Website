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
from database_manager import FilteredBlast
from quart_wtf import QuartForm, CSRFProtect
from wtforms import StringField, SelectField, FloatField
from wtforms.validators import Optional, NumberRange
from helper import to_float, build_row_stats, render_row_charts, render_data_desc
import matplotlib
matplotlib.use("Agg")

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
    search_word = StringField("Search")
    organism = SelectField("Organism", choices=[("", "All organisms")],
                           validators=[Optional()])
    min_identity = FloatField("Min identity %",
                              validators=[Optional(), NumberRange(0, 100)])
    min_score = FloatField("Min score", validators=[Optional()])
    min_bits = FloatField("Min bits", validators=[Optional()])
    max_evalue = StringField("Max E-value")  # text → allows "1e-10"
    sort_by = SelectField("Sort by", default="score",
                          choices=[("score", "Score"), ("bits", "Bits"),
                                   ("identity_perc", "Identity %"),
                                   ("e_value", "E-value")])
    sort_order = SelectField("Order", default="desc",
                             choices=[("desc", "High → Low"),
                                      ("asc", "Low → High")])


@app.route('/200seq_blast', defaults={'row_id': None})
@app.route('/200seq_blast/<int:row_id>', methods=["GET", "POST"])


async def seq200blast(row_id):
    form = await BlastFilterForm.create_form()
    cur = db.cursor(dictionary=True)
    flblast_db = FilteredBlast(cur)

    # Fetch once, filter in Python: no SQL injection, and correct e-value math
    all_rows = flblast_db.select() or []
    
    organisms = sorted(
        {r["organism_name"] for r in all_rows if r.get("organism_name")})
    form.organism.choices = [("", "All organisms")] + [(o, o) for o in
                                                       organisms]
    
    # --- read filters from query string ---
    search_word = request.args.get("search_word") or None
    organism = request.args.get("organism") or None
    min_identity = to_float(request.args.get("min_identity"))
    min_score = to_float(request.args.get("min_score"))
    min_bits = to_float(request.args.get("min_bits"))
    max_evalue = to_float(request.args.get("max_evalue"))
    sort_by = request.args.get("sort_by", "score")
    sort_order = request.args.get("sort_order", "desc")

    # keep the form widgets showing the active values
    form.search_word.data = search_word or ""
    form.organism.data = organism or ""
    form.min_identity.data = min_identity
    form.min_score.data = min_score
    form.min_bits.data = min_bits
    form.max_evalue.data = request.args.get("max_evalue") or ""
    form.sort_by.data = sort_by
    form.sort_order.data = sort_order
    
    filters = {
        "search_word": search_word, "organism": organism,
        "min_identity": min_identity, "min_score": min_score,
        "min_bits": min_bits,
        "max_evalue": request.args.get("max_evalue") or None,
        "sort_by": sort_by, "sort_order": sort_order,
    }
    
    # --- apply filters ---
    def keep(r):
        if search_word:
            hay = " ".join(str(r.get(c, "")) for c in
                           ("protein_name", "organism_name",
                            "description")).lower()
            if search_word.lower() not in hay:
                return False
        if organism and r.get("organism_name") != organism:
            return False
        if min_identity is not None:
            v = to_float(r.get("identity_perc"))
            if v is not None and v < min_identity:
                return False
        if min_score is not None:
            v = to_float(r.get("score"))
            if v is not None and v < min_score:
                return False
        if min_bits is not None:
            v = to_float(r.get("bits"))
            if v is not None and v < min_bits:
                return False
        if max_evalue is not None:
            v = to_float(r.get("e_value"))
            if v is not None and v > max_evalue:
                return False
        return True
    
    result = [r for r in all_rows if keep(r)]
    
    # --- sort ---
    if sort_by in ("score", "bits", "identity_perc", "e_value"):
        result.sort(key=lambda r: to_float(r.get(sort_by)) if to_float(
            r.get(sort_by)) is not None
        else float("-inf"),
                    reverse=(sort_order != "asc"))
    
    columns = list(all_rows[0].keys()) if all_rows else None
    
    # --- single row detail ---
    if row_id:
        match = next((r for r in all_rows if r["id"] == row_id), None)
        if not match:
            return await render_template('blast/200_blast_row.html',
                                         query_id="Not found", data=None,
                                         stats=None, charts=None)
        run_rows = [r for r in all_rows if
                    r.get("run_id") == match.get("run_id")]
        stats, chart_data = build_row_stats(match, run_rows)
        charts = render_row_charts(chart_data)
        description = render_data_desc(match.get("id"), match.get("run_id"),)
        print(description)
        return await render_template('blast/200_blast_row.html',
                                     query_id=match["run_id"], data=match,
                                     stats=stats, charts=charts,desc = description )

        # cap at 50 only when nothing is being filtered
    any_filter = any(v for v in (search_word, organism, min_identity,
                                 min_score, min_bits, max_evalue))
    display = result if any_filter else result[:50]
    
    return await render_template('blast/200_blast.html',
                                 data=display, columns=columns,
                                 form=form, filters=filters)


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
                ) NOT NULL
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
                ) NOT NULL
                    );
                """)
    
    # Close connection after table creation
    cur.close()
    
    # Start Server
    app.run(debug=PORT == "3000", port=PORT)
