import io
import base64
import matplotlib

from database_config import db
from database_manager import InputTable, RawBlastTable, OrganismTable, ProteinTable
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_row_stats(row, run_rows):
    """Aggregate the row's run for stat cards + chart payloads."""

    def fnum(r, key):
        return to_float(r.get(key))

    scores = [fnum(r, "score") for r in run_rows if
              fnum(r, "score") is not None]
    bits = [fnum(r, "bits") for r in run_rows if fnum(r, "bits") is not None]
    idents = [fnum(r, "identity_perc") for r in run_rows if
              fnum(r, "identity_perc") is not None]
    avg = lambda xs: round(sum(xs) / len(xs), 2) if xs else 0

    ranked = sorted(run_rows, key=lambda r: fnum(r, "score") or float("-inf"),
                    reverse=True)
    rank = next((i for i, r in enumerate(ranked, 1) if r["id"] == row["id"]),
                None)

    # DB column is sometimes spelled "converage" — handle both
    coverage = row.get("coverage", row.get("converage"))

    stats = {
        "rank": rank, "total": len(run_rows),
        "avg_score": avg(scores), "avg_bits": avg(bits),
        "avg_identity": avg(idents),
        "max_score": max(scores) if scores else 0,
        "coverage": coverage,
    }

    top = ranked[:10]
    chart_data = {
        "identity": fnum(row, "identity_perc") or 0,
        "coverage": to_float(coverage),
        "compare": {
            "labels": ["Score", "Bits", "Identity %"],
            "this_hit": [fnum(row, "score") or 0, fnum(row, "bits") or 0,
                         fnum(row, "identity_perc") or 0],
            "run_avg": [stats["avg_score"], stats["avg_bits"],
                        stats["avg_identity"]],
        },
        "top_hits": {
            "labels": [r.get("accession_code", "?") for r in top],
            "scores": [fnum(r, "score") or 0 for r in top],
            "current": row.get("accession_code"),
        },
    }
    return stats, chart_data


# Palette mirrored from blast.css
ACCENT = "#3a5a40"
ACCENT_BRIGHT = "#588157"
ACCENT_SOFT = "#a3b18a"
LINE = "#d8d3c4"
TEXT = "#1a1a17"
MUTED = "#6b6b63"


def make_chart(fig):
    """Save the current figure to a base64 PNG and close it."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_row_charts(chart_data):
    charts = {}
    
    # 1. Identity pie chart
    ident = chart_data["identity"] or 0
    fig, ax = plt.subplots()
    ax.pie([ident, 100 - ident], colors=["#3a5a40", "#d8d3c4"],
           labels=[f"{ident}%", ""])
    charts["identity"] = make_chart(fig)
    
    # 2. This hit vs run average (grouped bars)
    cmp = chart_data["compare"]
    fig, ax = plt.subplots()
    x = range(len(cmp["labels"]))
    ax.bar([i - 0.2 for i in x], cmp["this_hit"], width=0.4,
           label="This hit", color="#3a5a40")
    ax.bar([i + 0.2 for i in x], cmp["run_avg"], width=0.4,
           label="Run avg", color="#a3b18a")
    ax.set_xticks(list(x))
    ax.set_xticklabels(cmp["labels"])
    ax.legend()
    charts["compare"] = make_chart(fig)
    
    # 3. Top hits by score (horizontal bars)
    th = chart_data["top_hits"]
    colors = ["#588157" if label == th["current"] else "#a3b18a"
              for label in th["labels"]]
    fig, ax = plt.subplots()
    ax.barh(th["labels"], th["scores"], color=colors)
    ax.invert_yaxis()  # puts the first one at the top
    charts["top_hits"] = make_chart(fig)
    
    return charts


def render_data_desc(hit_id, query_id) -> dict :
    """
    Collect information about a hit to display in the description.
    :param query_id from filtered_blast:
    :param hit_id from filtered_blast:
    :return: dictionary = {
        "protein_name": None,
        "protein_function": None,
        "organism_name": None,
        "family": None,
        "sex": None,
        "species": None,
        "sequence": None,
    }
    """

    book = {
        "protein_name": None,
        "protein_function": None,
        "organism_name": None,
        "family": None,
        "sex": None,
        "species": None,
        "sequence": None,
    }
    #collect Organism and Protein Name
    cur = db.cursor()
    collect_raw = RawBlastTable(cur)
    collected = collect_raw.custom_query("Select protein_name, organism_name from filtered_blast where id = %s;",params=(hit_id,),returns=True)
    if len(collected) == 0:
        print(f"Hit {hit_id} not found in database")
        book["protein_name"] = 'ERROR RETRIEVING INFORMATION'
        book["organism_name"] = 'ERROR RETRIEVING INFORMATION'
        return book
    else:
        book["protein_name"] = collected[0][0]
        book["organism_name"] = collected[0][1]

    cur.close()

    #collect Taxonomy
    cur = db.cursor()
    collect_tax = OrganismTable(cur)
    collected_tax = collect_tax.custom_query("Select family, genus, species from organism where organism_name = %s;",params=(book["organism_name"],),returns=True)

    if len(collected_tax) == 0:
        book["family"] = 'ERROR RETRIEVING INFORMATION'
        book["genus"] = 'ERROR RETRIEVING INFORMATION'
        book["species"] = 'ERROR RETRIEVING INFORMATION'
    else:
        book["family"] = collected_tax[0][0]
        book["genus"] = collected_tax[0][1]
        book["species"] = collected_tax[0][2]
    cur.close()

    #collect function
    cur = db.cursor()
    collect_func = ProteinTable(cur)
    collected_func = collect_func.custom_query("select protein_function from protein where protein_name = %s;",params=(book["protein_name"],),returns=True)
    if len(collected_func) == 0:
        book["protein_function"] = 'ERROR RETRIEVING INFORMATION'
    else:
        book["protein_function"] = collected_func[0][0]
    cur.close()

    #collect sequence
    cur = db.cursor()
    collect_input = InputTable(cur)
    collected_input = collect_input.custom_query("select sequence from input where run_id = %s;",params=(query_id,),returns=True)
    if len(collected_input) == 0:
        book["sequence"] = 'ERROR RETRIEVING INFORMATION'
    else:
        book["sequence"] = collected_input[0][0]
    cur.close()

    return book
