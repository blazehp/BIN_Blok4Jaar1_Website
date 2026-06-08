import io
import base64
import matplotlib

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
