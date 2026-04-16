# Pairwise Sequence Alignment

## The Problem

-   Two DNA sequences often share regions of similarity
    because they evolved from a common ancestor or perform a similar function
-   Identifying those shared regions by eye is impractical for sequences longer than a few dozen characters
-   [%g global_alignment "Global alignment" %] finds the best end-to-end correspondence between two sequences,
    inserting gap characters (`-`) wherever a character in one sequence has no counterpart in the other
-   A gap corresponds to an insertion or deletion event during evolution
-   Before building the full algorithm,
    it helps to see a simpler problem with the same structure:
    computing the minimum number of single-character edits needed to turn one string into another

## A Warm-Up: Edit Distance

-   The edit distance between two strings is
    the minimum number of insertions, deletions, or substitutions needed to transform one into the other
-   Define $d(i,j)$ as the edit distance between the first $i$ characters of string $a$
    and the first $j$ characters of string $b$
-   The recurrence is:

<p>$$d(i,j) = \min\!\begin{cases} d(i-1,\,j-1) & \text{if } a_i = b_j \quad\text{(characters match, no cost)} \\ d(i-1,\,j-1) + 1 & \text{if } a_i \neq b_j \quad\text{(substitute)} \\ d(i-1,\,j) + 1 & \text{(delete from } a \text{)} \\ d(i,\,j-1) + 1 & \text{(insert into } a \text{)} \end{cases}$$</p>

-   The boundary conditions are $d(i,0) = i$ (delete all of $a$'s prefix)
    and $d(0,j) = j$ (insert all of $b$'s prefix)
-   This is [%g dynamic_programming "dynamic programming" %]:
    every subproblem is solved once and stored,
    so the total work is $O(mn)$ rather than the exponential cost of trying all possible alignments

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why is $d(i,0) = i$ in the edit distance recurrence, rather than $d(i,0) = 0$?

Because the first $i$ characters of $a$ have already been aligned perfectly
:   Wrong: $d(i,0)$ represents aligning $a[1..i]$ against an empty string, which requires $i$ deletions, not zero.

Because you need $i$ deletions to transform $a[1..i]$ into the empty string
:   Correct: each of the $i$ characters in the prefix must be removed, costing one unit per character.

Because each character in $a$ must be substituted for a gap
:   Wrong: substitution replaces one character with another; removing a character is a deletion, not a substitution.

Because the minimum edit distance is always equal to the longer sequence's length
:   Wrong: if both sequences are identical the edit distance is zero, regardless of length.

</div>

## Scoring an Alignment

-   Global alignment assigns a score to each aligned pair of positions rather than a uniform cost:
    -   Matching characters contribute a positive reward
    -   Mismatched characters contribute a small penalty
    -   Each gap character contributes a penalty

[%inc align.py mark="params"%]

-   `MATCH_SCORE` > 0 rewards exact matches
-   `MISMATCH_PENALTY` and `GAP_PENALTY` are both negative and equal here
    -   Every non-match costs one unit regardless of whether it is a substitution or an insertion/deletion
-   Setting `GAP_PENALTY` equal to `MISMATCH_PENALTY` is the simplest possible scoring scheme
    -   More elaborate aligners use larger gap-open penalties to discourage fragmented alignments

## The Needleman-Wunsch Algorithm

-   [%g needleman_wunsch "Needleman-Wunsch" %] solves global alignment exactly using dynamic programming
-   Build a matrix $H$ of size $(m+1)\times(n+1)$ where $m$ and $n$ are the sequence lengths
-   Initialize the border:
    $H[i,0] = i \times \text{gap}$ and $H[0,j] = j \times \text{gap}$
    to represent aligning a prefix of one sequence against an empty string
-   Fill $H$ left-to-right, top-to-bottom using the recurrence:

<p>$$H(i,j) = \max\!\begin{cases} H(i-1,\,j-1) + s(a_i,\,b_j) & \text{(match or mismatch)} \\ H(i-1,\,j) + g & \text{(gap in } b \text{)} \\ H(i,\,j-1) + g & \text{(gap in } a \text{)} \end{cases}$$</p>

-   $s(a_i, b_j)$ is `MATCH_SCORE` or `MISMATCH_PENALTY` and $g$ is `GAP_PENALTY`
-   There is no zero floor:
    unlike local alignment,
    global alignment must account for every character in both sequences, so negative scores are allowed
-   The final score of the best global alignment is $H[m, n]$.

[%inc align.py mark="score-func"%]

[%inc align.py mark="fill"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Needleman-Wunsch does NOT include a `max(0, ...)` floor in its recurrence. What is the consequence?

Negative cells are discarded, making the algorithm run faster
:   Wrong: there is no discarding; every cell is filled and may hold a negative value.

The algorithm can produce alignments whose total score is negative
:   Correct: a global alignment must span both sequences end to end, so if the sequences share few matches the total score can be negative.

The alignment always starts and ends at the same position in both sequences
:   Wrong: this describes a property of global alignment (both sequences are fully consumed) but is not a direct consequence of removing the zero floor.

Mismatches are penalised more heavily than gaps
:   Wrong: the relative penalties are set by `MISMATCH_PENALTY` and `GAP_PENALTY`, not by the presence or absence of a zero floor.

</div>

## An Example DP Table

-   Aligning `SEQ_A = "ACGT"` with `SEQ_B = "AGT"` using `MATCH_SCORE = 2`,
    `MISMATCH_PENALTY = -1`,
    `GAP_PENALTY = -1`:

|   |    | A  | G  | T  |
|---|---:|---:|---:|---:|
|   |  0 | -1 | -2 | -3 |
| A | -1 |  2 |  1 |  0 |
| C | -2 |  1 |  1 |  0 |
| G | -3 |  0 |  3 |  2 |
| T | -4 | -1 |  2 |  5 |

-   Row labels (left) are characters of `SEQ_A`; column labels (top) are characters of `SEQ_B`
-   $H[1,1] = 2$: A matches A, so $H[0,0] + 2 = 0 + 2 = 2$
-   $H[2,1] = 1$: C vs A is a mismatch
    -   Best is diagonal $H[1,0] + (-1) = -1 + (-1) = -2$,
        or delete $H[1,1] + (-1) = 2 + (-1) = 1$,
        so the delete wins
-   $H[4,3] = 5$: the score of the best global alignment

## Traceback

-   The best global alignment ends at $H[m, n]$ (bottom-right cell)
-   Follow the path that produced each cell's score back through $H$ until reaching $H[0,0]$
-   At each cell, check which neighbour's score plus the relevant penalty matches the current cell:
    -   If the diagonal move from $H[i-1,j-1]$ matches (preferred on ties),
        step diagonally and record the pair $(a_i, b_j)$
    -   If the upward move from $H[i-1,j]$ matches,
        step up and record $a_i$ paired with a gap in $b$
    -   Otherwise step left and record a gap in $a$ paired with $b_j$
-   Reverse the collected characters at the end, since the traceback runs backwards

[%inc align.py mark="traceback"%]

[%inc align.py mark="align"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Put these Needleman-Wunsch steps in the correct order.

1.  Initialise the first row and column of an (m+1) x (n+1) matrix with cumulative gap penalties
2.  Fill the remaining cells left-to-right and top-to-bottom using the recurrence
3.  Read off the alignment score from the bottom-right cell H[m, n]
4.  Follow the traceback path from H[m, n] back to H[0, 0]
5.  Reverse the collected characters to produce the aligned sequences

</div>

<div class="forma-labeling" data-lang="en" markdown="1">

Label each traceback move with the alignment operation it represents.

| Traceback Move | Alignment Operation |
| -------------- | ------------------- |
| Diagonal move (up-left) | Match or mismatch: one character from each sequence is consumed |
| Upward move | Gap inserted in sequence B: a character of A has no counterpart in B |
| Leftward move | Gap inserted in sequence A: a character of B has no counterpart in A |
| Reached H[0, 0] | End of the global alignment: both sequences are fully consumed |

</div>

## Displaying the Alignment

[%inc align.py mark="format"%]

-   Running the algorithm on `SEQ_A = "ACGT"` and `SEQ_B = "AGT"` produces:

```
a: ACGT
   | ||
b: A-GT
```

-   The gap in `seq_b` at position 2 accounts for the `C` in `seq_a` that has no counterpart
-   The score is $3 \times 2 + (-1) = 5$:
    three matches at `MATCH_SCORE` = 2 and one gap at `GAP_PENALTY` = -1

## Visualizing the Scoring Matrix

-   Plotting $H$ as a heatmap shows where high-scoring regions form
-   Bright cells cluster along diagonals where the sequences share runs of matching characters

[%inc align.py mark="plot"%]

[%figure
  slug="align-matrix"
  img="align.svg"
  alt="Heatmap of the Needleman-Wunsch scoring matrix for ACGT vs AGT, with brightest cell at bottom right."
  caption="Scoring matrix for SEQ_A = 'ACGT' vs SEQ_B = 'AGT'. The traceback follows the brightest path from H[m,n] (bottom right) back to H[0,0] (top left)."
%]

## Testing

Unlike the [diffusion](@/diffusion/) and [Lotka-Volterra](@/lotka/) lessons,
all scores here are integers computed by exact arithmetic:
no floating-point rounding occurs and no tolerance is needed in any test.

Matrix shape
:   The matrix must have one extra row and column for the gap-penalty border.
    An off-by-one error in the loop bounds is the most common bug in DP implementations.

Border initialization
:   $H[i,0] = i \times g$ and $H[0,j] = j \times g$ for all $i$ and $j$.
    A common mistake is leaving the first row and column at zero
    (which gives Smith-Waterman local alignment, not Needleman-Wunsch global alignment).

Identical sequences
:   Aligning a sequence with itself must match at every position with no gaps or mismatches.
    The score is exactly $\text{len} \times \text{MATCH\_SCORE}$.
    This test also checks that the aligned strings are returned in the correct order (not reversed).

Mismatch in alignment
:   `"AAAC"` vs `"AGAC"`: the second character differs (A vs G),
    but the flanking matches make a gapless alignment preferable to introducing a gap.
    Score = $3 \times 2 + (-1) = 5$.
    This test verifies that the algorithm correctly accepts a mismatch rather than inserting a gap.

Gap in alignment
:   `"ACGT"` vs `"AGT"`: `seq_b` has no C, so the aligner inserts a gap.
    Score = $3 \times 2 + (-1) = 5$.
    This test is the key check on the gap-handling branch of the traceback.

All mismatches
:   When every character pair is a mismatch and `GAP_PENALTY == MISMATCH_PENALTY`,
    the optimal global alignment still pairs all characters (no gaps),
    since introducing a gap would not improve the score.
    Score = $\text{len} \times \text{MISMATCH\_PENALTY}$.
    Note the difference from Smith-Waterman, which would return an empty alignment with score 0.

[%inc test_align.py%]

<section class="exercises" markdown="1">

## Exercises

### Do the math

Aligning "AGTC" with "AGC" using `MATCH_SCORE = 2`, `MISMATCH_PENALTY = -1`, `GAP_PENALTY = -1`:
the best global alignment has three matches and one gap.
What is the total alignment score?

### Effect of gap penalty

Change `GAP_PENALTY` from -1 to -3 (while keeping `MISMATCH_PENALTY = -1`) and re-run
`align("ACGT", "AGT")`.
Does the alignment still contain a gap, or does it change?
Explain the result in terms of the recurrence relation.

### Local alignment (Smith-Waterman)

The Smith-Waterman algorithm for local alignment differs from Needleman-Wunsch
in exactly two ways: the first row and column are all zeros (not cumulative gap penalties),
and each cell uses `max(0, diag, delete, insert)` instead of `max(diag, delete, insert)`.
Implement `fill_local(seq_a, seq_b)` and `traceback_local(H, seq_a, seq_b)` where the
traceback starts at the cell with the highest value and stops when it reaches a zero.
Verify that aligning `"AAACGT"` with `"CCGT"` locally produces a different result
than aligning them globally.

### Scoring matrix for amino acids

Biological sequence aligners use substitution matrices such as BLOSUM62 that assign
different scores to each pair of amino acid characters, reflecting how often each
substitution occurs in evolution.
Replace `_nt_score` with a function that looks up scores in a small hand-written
$4 \times 4$ substitution matrix for the four DNA bases A, C, G, T.
Assign a higher score to transitions (A vs G, C vs T) than transversions (A vs C, A vs T, etc.),
since transitions are more common mutations.
Verify that aligning `"ATCG"` with `"AGCG"` now gives a different score than with the
flat `MATCH_SCORE` / `MISMATCH_PENALTY` scheme.

### Affine gap penalty

The linear gap penalty $g$ treats opening a gap and extending an existing gap identically.
A more realistic affine gap penalty charges a higher cost $g_o$ to open a gap and a lower
cost $g_e$ to extend it: a gap of length $k$ costs $g_o + (k-1)g_e$.
Look up the three-matrix formulation of Needleman-Wunsch with affine gaps
(using matrices $H$, $E$, $F$) and implement it.
Verify that with $g_o = -3$ and $g_e = -1$ the alignment of `"ACCCGT"` with `"AGT"`
produces a single gap of length 3 rather than three individual gaps.

</section>
