import numpy as np
import polars as pl
import altair as alt

# mccole: params
MATCH_SCORE = 2      # reward for aligning identical characters
MISMATCH_PENALTY = -1  # penalty for aligning different characters
GAP_PENALTY = -1     # penalty per gap character inserted in either sequence

# Example sequences for the lesson.
SEQ_A = "ACGT"
SEQ_B = "AGT"
# mccole: /params


# mccole: score-func
def _nt_score(a, b):
    """Return match score or mismatch penalty for two nucleotide characters."""
    return MATCH_SCORE if a == b else MISMATCH_PENALTY
# mccole: /score-func


# mccole: fill
def fill_matrix(seq_a, seq_b):
    """Return the Needleman-Wunsch scoring matrix for two sequences.

    The matrix has shape (len(seq_a)+1, len(seq_b)+1).  Entry H[i, j] holds
    the score of the best global alignment of seq_a[:i] with seq_b[:j].
    The first row and column are initialised to cumulative gap penalties to
    represent aligning a non-empty prefix with an empty string.
    """
    m, n = len(seq_a), len(seq_b)
    H = np.zeros((m + 1, n + 1), dtype=int)
    for i in range(m + 1):
        H[i, 0] = i * GAP_PENALTY
    for j in range(n + 1):
        H[0, j] = j * GAP_PENALTY
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            diag = H[i - 1, j - 1] + _nt_score(seq_a[i - 1], seq_b[j - 1])
            delete = H[i - 1, j] + GAP_PENALTY  # gap in seq_b
            insert = H[i, j - 1] + GAP_PENALTY  # gap in seq_a
            H[i, j] = max(diag, delete, insert)
    return H
# mccole: /fill


# mccole: traceback
def traceback(H, seq_a, seq_b):
    """Trace back from the bottom-right cell to recover the global alignment.

    Returns (aligned_a, aligned_b, score) where '-' marks a gap.
    Global alignment always ends at H[m, n] and traces back to H[0, 0].
    When the diagonal, delete, and insert moves give equal scores, the
    diagonal (match/mismatch) move is preferred to produce a unique result.
    """
    i, j = len(seq_a), len(seq_b)
    score = int(H[i, j])
    aligned_a, aligned_b = [], []
    while i > 0 or j > 0:
        if (
            i > 0
            and j > 0
            and H[i, j] == H[i - 1, j - 1] + _nt_score(seq_a[i - 1], seq_b[j - 1])
        ):
            aligned_a.append(seq_a[i - 1])
            aligned_b.append(seq_b[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and H[i, j] == H[i - 1, j] + GAP_PENALTY:
            aligned_a.append(seq_a[i - 1])
            aligned_b.append("-")
            i -= 1
        else:
            aligned_a.append("-")
            aligned_b.append(seq_b[j - 1])
            j -= 1
    return "".join(reversed(aligned_a)), "".join(reversed(aligned_b)), score
# mccole: /traceback


# mccole: align
def align(seq_a, seq_b):
    """Return the best global alignment of seq_a and seq_b as (aligned_a, aligned_b, score)."""
    H = fill_matrix(seq_a, seq_b)
    return traceback(H, seq_a, seq_b)
# mccole: /align


# mccole: format
def format_alignment(aligned_a, aligned_b):
    """Return a three-line string representation of an alignment.

    The middle row marks matches with '|' and mismatches or gaps with ' '.
    """
    middle = "".join("|" if a == b else " " for a, b in zip(aligned_a, aligned_b))
    return f"a: {aligned_a}\n   {middle}\nb: {aligned_b}"
# mccole: /format


# mccole: plot
def plot_matrix(H, seq_a, seq_b):
    """Return an Altair heatmap of the scoring matrix."""
    rows = [
        {
            "i": i,
            "j": j,
            "score": int(H[i, j]),
            "row_label": seq_a[i - 1] if i > 0 else "",
            "col_label": seq_b[j - 1] if j > 0 else "",
        }
        for i in range(H.shape[0])
        for j in range(H.shape[1])
    ]
    df = pl.DataFrame(rows)
    return (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X(
                "j:O",
                title=f"seq_b: {seq_b}",
                axis=alt.Axis(labelExpr="datum.value == 0 ? '' : datum.value"),
            ),
            y=alt.Y(
                "i:O",
                title=f"seq_a: {seq_a}",
                sort="descending",
                axis=alt.Axis(labelExpr="datum.value == 0 ? '' : datum.value"),
            ),
            color=alt.Color("score:Q", scale=alt.Scale(scheme="blues"), title="Score"),
            tooltip=["i", "j", "score"],
        )
        .properties(width=300, height=300, title="Needleman-Wunsch scoring matrix")
    )
# mccole: /plot


if __name__ == "__main__":
    H = fill_matrix(SEQ_A, SEQ_B)
    aligned_a, aligned_b, score = traceback(H, SEQ_A, SEQ_B)
    print(f"Score: {score}")
    print(format_alignment(aligned_a, aligned_b))
    chart = plot_matrix(H, SEQ_A, SEQ_B)
    chart.save("align.svg")
    print("Saved align.svg")
    print("\nDP matrix:")
    print("     " + "  ".join(f" {c}" for c in " " + SEQ_B))
    for i in range(H.shape[0]):
        label = SEQ_A[i - 1] if i > 0 else " "
        print(f"  {label}  " + "  ".join(f"{H[i,j]:2d}" for j in range(H.shape[1])))
