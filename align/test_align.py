from align import (
    GAP_PENALTY,
    MATCH_SCORE,
    MISMATCH_PENALTY,
    SEQ_A,
    SEQ_B,
    align,
    fill_matrix,
)


def test_matrix_shape():
    # The scoring matrix must have one extra row and column for the gap-penalty
    # border that represents aligning a non-empty prefix with an empty string.
    H = fill_matrix(SEQ_A, SEQ_B)
    assert H.shape == (len(SEQ_A) + 1, len(SEQ_B) + 1)


def test_border_initialisation():
    # Needleman-Wunsch initialises H[i, 0] = i * GAP_PENALTY and
    # H[0, j] = j * GAP_PENALTY to represent the cost of consuming
    # i or j characters as pure gaps.
    H = fill_matrix(SEQ_A, SEQ_B)
    for i in range(len(SEQ_A) + 1):
        assert H[i, 0] == i * GAP_PENALTY
    for j in range(len(SEQ_B) + 1):
        assert H[0, j] == j * GAP_PENALTY


def test_identical_sequences():
    # A sequence aligned with itself must match at every position with no gaps.
    # The global score is exactly len(seq) * MATCH_SCORE.
    # Integer arithmetic means no tolerance is needed.
    seq = "ACGT"
    aligned_a, aligned_b, score = align(seq, seq)
    assert aligned_a == seq
    assert aligned_b == seq
    assert score == len(seq) * MATCH_SCORE


def test_mismatch_in_alignment():
    # "AAAC" vs "AGAC": the second character is a mismatch (A vs G) but the
    # surrounding matches make a gapless alignment preferable.
    # Score = 3 * MATCH_SCORE + MISMATCH_PENALTY.
    aligned_a, aligned_b, score = align("AAAC", "AGAC")
    assert aligned_a == "AAAC"
    assert aligned_b == "AGAC"
    assert score == 3 * MATCH_SCORE + MISMATCH_PENALTY


def test_gap_in_alignment():
    # "ACGT" vs "AGT": C in seq_a has no counterpart in seq_b so the best
    # global alignment inserts a gap.
    # Score = 3 * MATCH_SCORE + GAP_PENALTY.
    aligned_a, aligned_b, score = align("ACGT", "AGT")
    assert aligned_a == "ACGT"
    assert aligned_b == "A-GT"
    assert score == 3 * MATCH_SCORE + GAP_PENALTY


def test_all_mismatches():
    # When every pair of characters is a mismatch, the best global alignment
    # still aligns them without gaps (each mismatch costs MISMATCH_PENALTY,
    # which equals GAP_PENALTY here, but diagonal is preferred on ties).
    # Score = len * MISMATCH_PENALTY for equal-length sequences.
    aligned_a, aligned_b, score = align("AAAA", "CCCC")
    assert score == 4 * MISMATCH_PENALTY


def test_example_sequences():
    # Verify the lesson example: SEQ_A = "ACGT", SEQ_B = "AGT".
    # The known optimal global alignment inserts a gap in seq_b for C.
    aligned_a, aligned_b, score = align(SEQ_A, SEQ_B)
    assert aligned_a == "ACGT"
    assert aligned_b == "A-GT"
    assert score == 5
