def phred_score(char):
    """Convert ASCII character to Phred score (Sanger encoding)."""
    return ord(char) - 33


def analyze_fastq(file_path):
    total_reads = 0
    high_quality_reads = 0
    total_bases = 0
    high_quality_bases = 0

    with open(file_path, "r") as f:
        while True:
            header = f.readline().strip()

            if not header:
                break  # End of file

            sequence = f.readline().strip()
            plus = f.readline().strip()
            quality = f.readline().strip()

            total_reads += 1

            scores = [phred_score(q) for q in quality]
            avg_quality = sum(scores) / len(scores)

            total_bases += len(scores)
            high_quality_bases += sum(1 for s in scores if s >= 30)

            if avg_quality >= 30:
                high_quality_reads += 1

            # Optional: print per-read stats
            print(f"{header}")
            print(f"  Avg Q: {avg_quality:.2f}")
            print(
                "  High-quality bases (≥Q30): "
                f"{sum(s >= 30 for s in scores)}/{len(scores)}"
            )

    # Summary
    print("\n===== SUMMARY =====")
    print(f"Total reads: {total_reads}")
    print(f"High-quality reads (avg Q ≥ 30): {high_quality_reads}")
    print(f"Total bases: {total_bases}")
    print(
        f"Percent bases ≥ Q30: "
        f"{(high_quality_bases / total_bases) * 100:.2f}%"
    )