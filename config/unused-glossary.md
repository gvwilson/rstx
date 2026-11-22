# Unused glossary entries

<span id="censoring">Censoring</span>
:   In survival analysis, an observation is censored when the event of interest has not yet
    occurred by the end of the study or when a participant leaves before the study ends; the
    true event time is unknown but is known to exceed the censoring time.  Right-censoring
    (the most common form) occurs when participants are lost to follow-up or the study concludes.

<span id="collapsed_gibbs_sampling">Collapsed Gibbs sampling</span>
:   An MCMC algorithm for Bayesian models in which some latent variables (here,
    the document-topic and topic-word distributions) are analytically integrated
    out before sampling; the remaining variables (topic assignments) are sampled
    iteratively.  "Collapsed" refers to the reduction in the number of explicit
    variables, which improves mixing speed and simplifies implementation.

<span id="core_point">Core point</span>
:   In DBSCAN, a point whose $\varepsilon$-neighborhood contains at least
    `min_samples` points (including itself); core points are the seeds from
    which clusters are expanded by recursively adding all $\varepsilon$-reachable
    neighbors.

<span id="criterion_sdt">Criterion (signal detection)</span>
:   The threshold on the internal evidence axis above which an observer responds
    "signal present"; $c = -\frac{1}{2}(\Phi^{-1}(\text{HR}) + \Phi^{-1}(\text{FAR}))$;
    $c = 0$ for an unbiased observer, $c > 0$ for a conservative observer, and
    $c < 0$ for a liberal observer.

<span id="d_prime">d-prime (d')</span>
:   The sensitivity index in signal detection theory: $d' = \Phi^{-1}(\text{HR}) - \Phi^{-1}(\text{FAR})$,
    where $\Phi^{-1}$ is the inverse standard normal CDF; $d'$ equals the separation
    between the signal and noise distributions in standard deviation units; $d' = 0$
    at chance and $d' > 0$ when the observer can discriminate signal from noise.

<span id="dbscan">DBSCAN</span>
:   Density-Based Spatial Clustering of Applications with Noise; a clustering
    algorithm that groups points by local density rather than distance to a centroid.
    A point is a core point if at least `min_samples` points lie within radius
    $\varepsilon$; clusters expand from core points through chains of $\varepsilon$-neighbors;
    points unreachable from any core point are labelled noise ($-1$).

<span id="diffusion_equation">Diffusion equation</span>
:   The partial differential equation $\partial c/\partial t = D\,\partial^2 c/\partial x^2$
    that describes how a dissolved substance or heat spreads through a medium at a rate
    proportional to the curvature of its concentration profile.

<span id="dirichlet_distribution">Dirichlet distribution</span>
:   A distribution over probability vectors (vectors whose entries are
    non-negative and sum to 1); parameterised by a concentration vector
    $\boldsymbol{\alpha}$ whose magnitude controls how concentrated the samples
    are.  Small $\alpha_k$ values produce sparse distributions (most mass on
    one component); large values produce uniform distributions.  The Dirichlet
    is the conjugate prior for the categorical distribution and is used in LDA
    to model both document-topic and topic-word distributions.

<span id="euler_mascheroni">Euler-Mascheroni constant</span>
:   The constant $\gamma_E = \lim_{n\to\infty}(\sum_{k=1}^n 1/k - \ln n) \approx 0.5772$;
    appears in the mean of the Gumbel extreme-value distribution as $\mathrm{E}[X] = \mu + \gamma_E \beta$.

<span id="extreme_value_distribution">Extreme value distribution</span>
:   A family of distributions that arise as limiting distributions of sample maxima or minima;
    the Gumbel (Type I) member is commonly used to model annual maximum river flows and other
    environmental extremes.

<span id="first_integral">First integral</span>
:   A function of the state variables whose value is constant along every trajectory of a
    dynamical system; also called a conserved quantity or invariant.

<span id="gumbel_distribution">Gumbel distribution</span>
:   FIXME

<span id="gumbel_paper">Gumbel probability paper</span>
:   A plotting technique that rescales the horizontal axis by the reduced variate
    $y = -\ln(-\ln p)$, so that data following a Gumbel distribution plot as a straight line;
    departures from linearity indicate poor fit.

<span id="inter_rater_agreement">Inter-rater agreement</span>
:   The degree to which two or more independent raters assign the same category
    to the same observations; raw percent agreement is easy to compute but is
    inflated by chance agreement; Cohen's kappa corrects for this inflation and
    is the standard measure in psychology, clinical research, and annotation.

<span id="kaplan_meier">Kaplan-Meier estimator</span>
:   A non-parametric estimator of the survival function that accounts for censored observations
    by updating only at observed event times: $\hat{S}(t) = \prod_{t_i \leq t}(1 - d_i/n_i)$
    where $d_i$ is the number of events and $n_i$ the number at risk at time $t_i$.

<span id="kd_tree">KD-tree</span>
:   A binary space-partitioning tree that organises $k$-dimensional points by
    recursively splitting along alternating coordinate axes.  Supports efficient
    range queries: all points within a given distance of a query point can be
    retrieved in $O(\log n)$ time on average, making it well-suited for the
    epsilon-neighborhood lookups required by DBSCAN.

<span id="latent_dirichlet_allocation">Latent Dirichlet Allocation (LDA)</span>
:   A generative probabilistic model (Blei, Ng, Jordan 2003) for text corpora
    in which each document is represented as a mixture of topics and each topic
    is a distribution over words; both mixtures are drawn from Dirichlet priors
    with concentration parameters $\alpha$ (document-topic) and $\beta$ (topic-word).
    Topics and mixtures are latent (unobserved) and must be inferred from the
    observed words.

<span id="local_alignment">Local alignment</span>
:   An alignment that finds the highest-scoring matching subsequence anywhere within two
    sequences, rather than aligning them from end to end; used to locate conserved domains
    within longer sequences.

<span id="neighbor_joining">Neighbor-joining</span>
:   A distance-based algorithm (Saitou and Nei, 1987) that reconstructs a phylogenetic tree
    by iteratively joining the pair of taxa with the smallest corrected distance, running in
    $O(N^3)$ time.

<span id="noise_point">Noise point</span>
:   In DBSCAN, a point that is not a core point and is not within distance
    $\varepsilon$ of any core point; labelled $-1$ and not assigned to any cluster.
    Noise points correspond to outliers or isolated observations that do not belong
    to any dense region.

<span id="phase_portrait">Phase portrait</span>
:   A plot of one state variable against another (e.g., predator vs. prey population) showing
    the family of trajectories a dynamical system can follow, without reference to time.

<span id="q_matrix">Q-matrix</span>
:   A corrected distance matrix used in the neighbor-joining algorithm where each entry
    $Q(i,j) = (n-2)D(i,j) - \sum_k D(i,k) - \sum_k D(j,k)$ removes the bias introduced by
    branches of unequal length.

<span id="reduced_variate">Reduced variate</span>
:   The dimensionless quantity $y = -\ln(-\ln p)$ used in extreme-value analysis; it linearises
    the Gumbel CDF so that data following a Gumbel distribution plot as a straight line against
    the corresponding quantiles on Gumbel probability paper.

<span id="signal_detection_theory">Signal detection theory</span>
:   A framework for separating an observer's perceptual sensitivity from their
    response tendency by modeling the internal decision variable as two overlapping
    normal distributions (signal and noise) and fitting both the hit rate and
    false-alarm rate jointly; the key measures are $d'$ (sensitivity) and
    criterion $c$ (response bias).

<span id="smith_waterman">Smith-Waterman algorithm</span>
:   A dynamic-programming algorithm (Smith and Waterman, 1981) that computes the optimal local
    alignment of two sequences by filling a scoring matrix with a recurrence that includes a
    zero floor, allowing alignments to start anywhere.

<span id="transfer_matrix">Transfer matrix</span>
:   A square matrix $T$ where entry $T[i,j]$ gives the fraction of material at node $j$ that
    moves to node $i$ in one time step; when every column sums to 1 (column-stochastic), the
    total amount of material is exactly conserved at every step.

<span id="tridiagonal_system">Tridiagonal system</span>
:   A linear system $A\mathbf{x} = \mathbf{b}$ in which $A$ has nonzero entries only on the
    main diagonal and the two diagonals immediately above and below it; arises from 1D
    finite-difference discretization and can be solved in $O(n)$ time.

<span id="von_neumann_stability">von Neumann stability condition</span>
:   FIXME
