# Authorship Attribution by N-gram Profiles

## The Problem

-   [%g authorship_attribution "Authorship attribution" %] asks,
    "Given an anonymous text and a set of candidate authors,
    whose writing style does the text most resemble?"
-   Applications include forensic linguistics (disputed documents, plagiarism detection)
    and literary studies (anonymous or pseudonymous works)
-   Style is captured not by vocabulary choices but by low-level character patterns:
    how often certain pairs or triples of characters appear together
-   The approach here:
    -   Generate a synthetic corpus of short texts in which
        each author uses a distinct set of characters with higher frequency
    -   Build a [%g ngram_profile "character n-gram profile" %] for each author from training texts
    -   Attribute each test text to the author whose profile is most similar,
        using [%g cosine_similarity "cosine similarity" %] as the distance measure

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why are character n-grams more reliable for authorship attribution than word
frequency profiles?

Because character n-grams are always more frequent than words.
:   Wrong: character n-grams are shorter sequences and can be more frequent in
    raw count terms, but that is not why they are preferred for attribution.

Because character n-grams capture unconscious stylistic habits such as
punctuation, spacing, and morpheme preferences that are harder to alter than
word choice.
:   Correct: authors may deliberately vary vocabulary to avoid detection, but
    character-level patterns are more deeply habitual and change less consciously.

Because word frequency profiles require labeled training data.
:   Wrong: both word frequency profiles and character n-gram profiles are built
    from raw (unlabeled) text; no class labels are needed.

Because character n-grams are language-independent.
:   Wrong: although n-grams can be applied across languages, this is not the
    reason they outperform word profiles for single-language attribution tasks.

</div>

## Character N-gram Profiles

-   A [%g char_ngram "character n-gram" %] is a sequence of $n$ consecutive characters in a text
    -   Spaces and punctuation are treated as characters so that word-boundary patterns are captured
-   For a text of length $L$ characters there are $L - n + 1$ overlapping n-grams
-   The profile for an author is the relative frequency of each n-gram across all their training texts

<p>$$p(ng) = \frac{\text{count}(ng)}{\sum_{ng'} \text{count}(ng')}$$</p>

-   The profile is a probability distribution over the set of observed n-grams

## Cosine Similarity

-   Given two profiles $\mathbf{p}_A$ and $\mathbf{p}_B$ (treated as vectors indexed by n-gram),
    with $\|\mathbf{p}\| = \sqrt{\sum_{ng} p(ng)^2}$,
    the cosine similarity is:

<p>$$\text{sim}(A, B) = \frac{\sum_{ng} p_A(ng)\, p_B(ng)}{\|\mathbf{p}_A\|\;\|\mathbf{p}_B\|}$$</p>

-   Cosine similarity ranges from 0 (no shared n-grams) to 1 (identical profiles)
-   Dividing by the norms makes the measure length-independent:
    a short text and a long text with the same relative frequencies score 1

<div class="forma-numeric-entry" data-correct="0.96" data-tolerance="0.001" data-lang="en" markdown="1">

Profile A has bigrams "ab" with frequency 0.6 and "cd" with frequency 0.8
(it contains no other bigrams, and the two frequencies form a unit vector).
Profile B has "ab" with frequency 0.8 and "cd" with frequency 0.6.
What is the cosine similarity of A and B?

</div>

## Generating Synthetic Texts

-   The 15-character alphabet "abcdefghijklmno" is divided into three equal groups of five
-   Each author favors one group
-   Characters from the preferred group are sampled five times more often
    than characters from the other groups,
    producing clearly separable profiles
-   Words are random strings of 3 to 6 characters
-   texts contain 150 words
-   The last of the four texts per author serves as the [%g hold_out "held-out" %] test text

[%inc generate_authorship.py mark="generate"%]

## Building N-gram Profiles

[%inc authorship.py mark="ngrams"%]

[%inc authorship.py mark="profile"%]

## Computing Cosine Similarity

[%inc authorship.py mark="similarity"%]

## Attributing an Unknown Text

-   For each candidate author,
    build a profile from their training texts
-   Compute the cosine similarity between the unknown text's profile and each candidate profile
-   The candidate with the highest similarity is the predicted author

[%inc authorship.py mark="attribute"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

An unknown text scores 0.94 similarity to Author A and 0.31 to Author B.
What would it mean if Author A's score were only slightly higher than Author B's,
say 0.52 vs 0.48?

The attribution is still reliable because Author A has the higher score.
:   Wrong: a small margin between scores indicates that the profiles are
    nearly equally similar; small perturbations in the text could reverse the ranking.

The attribution should be treated with caution because the scores are close and
the unknown text may genuinely resemble both authors.
:   Correct: a large gap (as in 0.94 vs 0.31) provides strong evidence for the
    top candidate; a small gap suggests low confidence and warrants additional evidence.

The method has a bug because scores this close should not occur.
:   Wrong: close scores are a legitimate outcome when two authors share similar
    stylistic habits; the method is working correctly.

Both authors should be reported as equally likely candidates.
:   Wrong: the method returns a ranking; reporting a tie requires a separate
    statistical test not implemented here.

</div>

## Visualizing the Results

[%inc authorship.py mark="plot"%]

[%figure
  slug="authorship-similarity"
  img="authorship-similarity.svg"
  alt="A horizontal bar chart with three bars. The bar for Author C extends to approximately 0.94 on the similarity axis while the bars for Author A and Author B each reach approximately 0.33 and 0.30."
  caption="Cosine similarity of the Author C test text against each candidate's training profile (NGRAM_SIZE=2). Author C scores 0.94; Authors A and B score 0.33 and 0.30, correctly identifying the author with a large margin."
%]

## Testing

-   Bigram counts
    -   "abc" with $n=2$ yields exactly the bigrams "ab" and "bc", each with count 1
    -   "aaa" with $n=2$ yields two overlapping "aa" bigrams

-   Profile normalization
    -   A profile built from any non-empty text must sum to 1.0

-   Cosine edge case
    -   Identical profiles have cosine similarity exactly 1.0
    -   Profiles with no shared n-grams have cosine similarity 0.0

-   Attribution accuracy
    -   Every test text in the synthetic corpus must be attributed to its true author

[%inc test_authorship.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Authorship attribution key terms

Character n-gram
:   A sequence of $n$ consecutive characters in a text, including spaces; captures
    local typing habits such as common letter combinations and word-boundary patterns

N-gram profile
:   The relative frequency distribution of all observed n-grams in a text or
    collection of texts; represents the author's stylistic fingerprint

Cosine similarity
:   $\text{sim}(A,B) = (\mathbf{p}_A \cdot \mathbf{p}_B) / (\|\mathbf{p}_A\|\|\mathbf{p}_B\|)$;
    ranges from 0 (no shared n-grams) to 1 (identical profiles); length-independent

Authorship attribution
:   The task of identifying the author of an anonymous text by comparing its
    stylistic features to profiles built from texts of known authorship

Attribution margin
:   The difference between the top candidate's similarity score and the
    next-highest score; a small margin indicates low attribution confidence

</div>

<section class="exercises" markdown="1">

## Exercises

### Effect of n-gram size

Repeat the attribution experiment with $n = 1$, $2$, $3$, and $4$.
Plot the similarity scores for all three test texts at each $n$.
At which n-gram size does the margin between the correct author and the
next-best candidate peak?
Explain why very large $n$ might reduce accuracy on short texts.

### Profile distance matrix

Build profiles for all training texts (not averaged per author) and compute
the pairwise cosine similarity matrix.
Visualize it as a heatmap.
Do texts from the same author cluster together?

### Cross-validation

Modify the experiment so that for each author, one of the training texts is
held out as the test text while the remaining training texts are used to build
the profile.
Repeat for each training text in turn (leave-one-out cross-validation) and
report the attribution accuracy rate.

### Impostor experiment

Create a fourth author whose preferred character set overlaps 50% with Author A's.
Does the attribution method correctly distinguish Author A from the impostor?
What similarity score threshold would you set to report "uncertain" rather than
making a forced choice?

</section>
