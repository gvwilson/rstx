import numpy as np

SEED = 7493418

# Number of variant loci in each manuscript.  100 loci gives enough resolution
# to distinguish copying families while keeping the sequences short.
N_LOCI = 100

# Probability that a scribe introduces a new variant at any given locus when
# copying.  0.05 means roughly 5 changes per copy on average.  Low enough
# that back-mutations (changing an already-changed locus back) are rare,
# so Hamming distance remains close to the sum of branch-level mutation counts.
MUTATION_PROB = 0.05

# Names of the four surviving manuscripts.
MANUSCRIPTS = ["A", "B", "C", "D"]


def _copy(sequence, prob, rng):
    """Return a copy of sequence with each locus flipped independently with probability prob."""
    flips = rng.random(len(sequence)) < prob
    return np.where(flips, 1 - sequence, sequence)


# mccole: generate
def make_manuscripts(
    n_loci=N_LOCI,
    mutation_prob=MUTATION_PROB,
    seed=SEED,
):
    """Return a dict mapping each manuscript name to its variant sequence.

    The copying tree is:

        archetype
        |-- alpha  (intermediate ancestor of A and B)
        |   |-- A
        |   `-- B
        `-- beta   (intermediate ancestor of C and D)
            |-- C
            `-- D

    Each branch introduces random mutations independently.  The archetype
    starts as all-zero; mutations flip a locus from 0 to 1 (or back).
    Only the four surviving manuscripts are returned; the archetype and
    intermediate ancestors are not observed.
    """
    rng = np.random.default_rng(seed)
    archetype = np.zeros(n_loci, dtype=np.int8)
    alpha = _copy(archetype, mutation_prob, rng)
    beta = _copy(archetype, mutation_prob, rng)
    mss = {
        "A": _copy(alpha, mutation_prob, rng),
        "B": _copy(alpha, mutation_prob, rng),
        "C": _copy(beta, mutation_prob, rng),
        "D": _copy(beta, mutation_prob, rng),
    }
    return mss
# mccole: /generate


if __name__ == "__main__":
    mss = make_manuscripts()
    print(f"Loci: {N_LOCI}, mutation probability per locus: {MUTATION_PROB}")
    for name, seq in mss.items():
        n_diff = int(seq.sum())
        print(f"  {name}: {n_diff} loci differ from archetype (all-zero)")
    names = list(mss)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            dist = int(np.sum(mss[a] != mss[b])) / N_LOCI
            print(f"  D({a},{b}) = {dist:.3f}")
