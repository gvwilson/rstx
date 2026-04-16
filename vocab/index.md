# Vocabulary Richness in Historical Texts

## The Problem

-   Lexical richness — how varied an author's word choices are — is used in
    authorship studies, language acquisition research, and digital humanities.
-   The simplest measure is the [%g type_token_ratio "type-token ratio" %] (TTR):
    the number of distinct word types divided by the total number of word tokens.
-   TTR has a well-known flaw: it falls as text length increases even when richness
    is constant, because longer texts inevitably repeat high-frequency words.
-   The [%g mattr "Moving-Average Type-Token Ratio" %] (MATTR) fixes this by computing
    TTR over fixed-width windows and averaging the results.
-   The approach here:
    -   Generate a synthetic corpus in which each author samples words from a
        [%g zipf_law "Zipfian distribution" %] with a different vocabulary size.
    -   Compute TTR and MATTR for each text using Polars.
    -   Visualize and compare richness scores across authors with Vega-Altair.

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why does a 1000-word text typically have a lower TTR than a 100-word text
from the same author?

Because longer texts contain fewer unique words.
:   Wrong: longer texts contain more unique words in absolute terms; it is the
    ratio of unique words to total words that falls.

Because words are reused more often as text length increases, reducing the
proportion of unique word forms.
:   Correct: common words such as "the" and "of" appear multiple times; as total
    tokens grow, repetitions account for a larger share of the count.

Because the author's vocabulary is exhausted after 100 words.
:   Wrong: the full vocabulary is available throughout; it is reuse frequency that
    changes the ratio.

Because tokenisation introduces more errors in longer texts.
:   Wrong: TTR is a purely statistical property of the token sequence and is
    independent of tokenisation quality.

</div>

## Type-Token Ratio and MATTR

-   Given a text of $T$ tokens containing $V$ distinct word types, the TTR is:

<p>$$\text{TTR} = \frac{V}{T}$$</p>

-   The MATTR with window width $w$ is:

<p>$$\text{MATTR} = \frac{1}{T - w + 1} \sum_{i=0}^{T-w} \text{TTR}(t_i, t_{i+1}, \ldots, t_{i+w-1})$$</p>

-   Each window has the same length $w$, so each window TTR is on the same scale;
    averaging them gives a length-fair summary.
-   When $T \leq w$ there is only one window and MATTR equals the global TTR.

## Generating Synthetic Texts

-   Word frequencies in natural language follow [%g zipf_law "Zipf's law" %]:
    the $k$-th most common word appears with frequency proportional to $1/k$.
-   Sampling from this distribution with different vocabulary sizes reproduces
    the richness differences between authors with limited and extensive lexicons.

[%inc generate_vocab.py mark="generate"%]

## Computing TTR and MATTR

[%inc vocab.py mark="ttr"%]

## Aggregating Richness Scores

[%inc vocab.py mark="richness"%]

## Visualizing Results

[%inc vocab.py mark="plot"%]

[%figure
  slug="vocab-richness"
  img="vocab-richness.svg"
  alt="Bar chart with six bars. Author A bars are shortest, Author B bars are middle height, Author C bars are tallest."
  caption="MATTR for each text in the synthetic corpus. Author A (vocabulary 200), Author B (400), and Author C (800) produce texts with MATTR of roughly 0.63, 0.68, and 0.72 respectively, confirming that the metric distinguishes authors by lexical richness regardless of text length."
%]

## Testing

-   TTR edge cases
    -   A text of all unique words has TTR exactly 1.0.
    -   A text where the same word is repeated $n$ times has TTR $1/n$.
    -   An empty word list returns 0.0 without raising an exception.
-   MATTR fallback
    -   When the text is shorter than the window, MATTR returns the global TTR.
    -   When the text length equals the window width, there is exactly one window and
        MATTR equals the global TTR.
-   Richness ordering
    -   Author A (vocabulary 200), Author B (400), and Author C (800) are generated from
        increasingly large Zipfian vocabularies.
        Their mean MATTR values must increase in the same order.

[%inc test_vocab.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Vocabulary richness key terms

Type-token ratio (TTR)
:   $V/T$ where $V$ is the number of distinct word types and $T$ is the total
    token count; decreases with text length even at constant vocabulary richness

Moving-average TTR (MATTR)
:   Mean of window TTRs computed over overlapping fixed-width windows;
    length-independent because every window has the same size

Zipf's law
:   The empirical regularity that the $k$-th most frequent word in a corpus
    appears roughly $1/k$ times as often as the most frequent word; produces
    the characteristic long tail of rare words in natural language

Vocabulary richness
:   A property of a text or author reflecting how varied word choices are;
    higher richness means proportionally more unique words per token

Window width (MATTR)
:   The fixed number of tokens in each local TTR window; must be short enough
    to keep window TTR below 1.0 but long enough to average out token-level noise

</div>

<section class="exercises" markdown="1">

## Exercises

### Do the math

A 100-word text contains 60 distinct word types.
What is its type-token ratio?

### Effect of window width

Compute MATTR for window widths of 10, 25, 50, 100, and 200 for one of the
Author C texts.
Plot MATTR against window width and explain why MATTR approaches the global TTR
as the window grows toward the text length.

### TTR length dependence

Generate texts of 100, 200, 400, and 800 tokens from the same Zipfian distribution
(vocabulary size 400).
Plot both TTR and MATTR against text length on the same axes.
At what length does the difference between TTR and MATTR become noticeable?

### Real corpus comparison

Download two public-domain texts of very different lengths from Project Gutenberg.
Tokenise each into lowercase words (strip punctuation), then compute TTR and
MATTR with a 50-word window.
Does MATTR correct the length bias visible in TTR?

### Hapax legomena rate

A hapax legomenon is a word that appears exactly once in a text.
Implement `hapax_rate(words)` that returns the fraction of total tokens that are
hapax legomena.
Compare hapax rate with MATTR across the three synthetic authors and discuss
whether hapax rate is also length-independent.

</section>
