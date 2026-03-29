# Glossary

## A

<span id="agent_based_model">Agent-based model</span>
:   A simulation in which autonomous agents follow local rules and interact with one another;
    emergent population-level patterns arise from many individual interactions rather than being
    specified directly.  Used in ecology, economics, and epidemiology to study complex systems
    that cannot easily be described by closed-form equations.

<span id="archetype">archetype</span>
:   FIXME

<span id="area_under_curve">Area under the curve (AUC)</span>
:   The area enclosed between the ROC curve and the x-axis, computed using
    the trapezoidal rule as
    $\text{AUC} \approx \sum_i \tfrac{1}{2}(\text{HR}_i + \text{HR}_{i+1})|\text{FAR}_i - \text{FAR}_{i+1}|$;
    AUC = 0.5 for chance performance (the diagonal) and AUC = 1.0 for perfect
    discrimination; it equals the probability that a randomly chosen signal trial
    receives a higher evidence score than a randomly chosen noise trial.

<span id="authorship_attribution">Authorship attribution</span>
:   The task of identifying which of several candidate authors wrote an anonymous
    text by comparing its stylistic features (such as character n-gram frequencies)
    to profiles built from texts of known authorship; used in forensic linguistics
    and literary studies to resolve questions of disputed or pseudonymous authorship.

## B

<span id="bag_of_words">Bag of words</span>
:   A document representation that records only which words appear and how often,
    discarding word order and position; sufficient for topic modeling because topics
    are defined by co-occurrence patterns rather than syntactic structure.

<span id="basic_reproduction_number">Basic reproduction number</span>
:   Denoted $R_0$, the average number of secondary infections caused by a single infectious
    individual in a fully susceptible population; if $R_0 > 1$ an epidemic can grow, if
    $R_0 \leq 1$ it dies out.  For the SIR model, $R_0 = \beta / \gamma$.

<span id="binary_mask">Binary mask</span>
:   A 2-D array of true/false (or 1/0) values indicating which pixels satisfy a criterion such
    as exceeding an intensity threshold; used as input to connected-component labelling.

## C

<span id="censoring">Censoring</span>
:   In survival analysis, an observation is censored when the event of interest has not yet
    occurred by the end of the study or when a participant leaves before the study ends; the
    true event time is unknown but is known to exceed the censoring time.  Right-censoring
    (the most common form) occurs when participants are lost to follow-up or the study concludes.

<span id="char_ngram">Character n-gram</span>
:   A sequence of $n$ consecutive characters in a text, including spaces and
    punctuation; for a text of length $L$ there are $L - n + 1$ overlapping n-grams.
    Character n-grams capture unconscious stylistic patterns such as preferred
    letter combinations and word-boundary habits, making them useful for
    authorship attribution.

<span id="cohens_kappa">Cohen's kappa</span>
:   A chance-corrected measure of inter-rater agreement:
    $\kappa = (P_o - P_e) / (1 - P_e)$, where $P_o$ is the proportion of items
    on which raters agree and $P_e$ is the agreement expected under independence.
    $\kappa = 0$ at chance, $\kappa = 1$ at perfect agreement, $\kappa < 0$
    when observed agreement falls below chance.

<span id="collapsed_gibbs_sampling">Collapsed Gibbs sampling</span>
:   An MCMC algorithm for Bayesian models in which some latent variables (here,
    the document-topic and topic-word distributions) are analytically integrated
    out before sampling; the remaining variables (topic assignments) are sampled
    iteratively.  "Collapsed" refers to the reduction in the number of explicit
    variables, which improves mixing speed and simplifies implementation.

<span id="confidence_interval_parameter">Confidence interval (parameter)</span>
:   An interval constructed from data such that, over many repetitions of the
    experiment, the true parameter value falls within the interval at the stated
    rate (e.g., 95%); for nonlinear least squares the interval is formed as
    $\hat{\theta} \pm z \cdot \text{SE}(\hat{\theta})$ where
    $\text{SE}(\hat{\theta}) = \sqrt{\text{diag}(\text{pcov})}$ and $z = 1.96$
    for a 95% CI under asymptotic normality.

<span id="confusion_matrix">Confusion matrix</span>
:   A $2\times2$ (or larger) table that cross-tabulates true class labels against predicted
    class labels; for binary classification it contains true negatives (TN), false positives
    (FP), false negatives (FN), and true positives (TP), enabling computation of precision,
    recall, and F1 score alongside overall accuracy.

<span id="connected_component">Connected component</span>
:   A maximal set of pixels (or grid cells) that are all above a threshold and are connected
    to one another through shared edges or corners; each component is treated as a single object.

<span id="contingency_table_raters">Contingency table (raters)</span>
:   A $K \times K$ integer matrix whose entry $C_{ij}$ counts the number of
    observations for which rater A assigned category $i$ and rater B assigned
    category $j$; diagonal entries are agreements and off-diagonal entries are
    disagreements; used to compute Cohen's kappa.

<span id="core_point">Core point</span>
:   In DBSCAN, a point whose $\varepsilon$-neighborhood contains at least
    `min_samples` points (including itself); core points are the seeds from
    which clusters are expanded by recursively adding all $\varepsilon$-reachable
    neighbors.

<span id="cosine_similarity">Cosine similarity</span>
:   A measure of the angle between two vectors:
    $\text{sim}(\mathbf{a}, \mathbf{b}) = (\mathbf{a}\cdot\mathbf{b}) / (\|\mathbf{a}\|\|\mathbf{b}\|)$;
    ranges from 0 (orthogonal, no shared features) to 1 (identical direction).
    Used to compare n-gram frequency profiles because it is independent of text
    length: profiles with the same relative frequencies score 1 regardless of
    how many tokens produced them.

<span id="cost_surface">Cost surface</span>
:   A raster (2-D grid) in which each cell stores the difficulty or energy cost
    of moving through that location; derived from terrain attributes such as
    elevation, slope, or land cover.  Used in least-cost path analysis to convert
    a geographic landscape into a weighted graph suitable for Dijkstra's algorithm.

<span id="covariance_matrix">Covariance matrix</span>
:   A symmetric matrix whose diagonal entries are the variances of fitted parameters and whose
    off-diagonal entries are the covariances between pairs of parameters; returned by least-squares
    fitting routines to quantify parameter uncertainties.

<span id="cramer_rao_bound">Cramér-Rao bound</span>
:   FIXME

<span id="criterion_sdt">Criterion (signal detection)</span>
:   The threshold on the internal evidence axis above which an observer responds
    "signal present"; $c = -\frac{1}{2}(\Phi^{-1}(\text{HR}) + \Phi^{-1}(\text{FAR}))$;
    $c = 0$ for an unbiased observer, $c > 0$ for a conservative observer, and
    $c < 0$ for a liberal observer.

<span id="cross_entropy">Cross-entropy loss</span>
:   A loss function for classification: $-[y\log p + (1-y)\log(1-p)]$ for binary problems,
    where $y$ is the true label and $p$ is the predicted probability; penalises confident
    wrong predictions more heavily than uncertain ones.

<span id="cross_validation_loo">Leave-one-out cross-validation</span>
:   A model-evaluation procedure in which each observation is held out in turn,
    the model is fitted on the remaining observations, and the prediction error
    for the held-out point is recorded; averaging over all held-out errors
    estimates prediction skill on new data without requiring a separate test set.

<span id="cusum">Cumulative sum (CUSUM) statistic</span>
:   $C_t = \sum_{s=0}^{t} \hat{e}_s$, the running total of OLS residuals; used to detect
    structural breaks because a shift in the series mean causes residuals to share a
    systematic sign, producing a drift in $C_t$ that reverses direction at the break.
    The estimated break location is the index where $|C_t|$ is largest.

## D

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

<span id="depth_first_search">Depth-first search</span>
:   A graph traversal algorithm that explores as far as possible along each branch before
    backtracking, implemented with a stack (iteratively) or recursion; used here to test
    whether a path of open cells connects the top row to the bottom row of a grid.

<span id="diachronic_analysis">Diachronic analysis</span>
:   The study of how a linguistic feature (such as word frequency or grammatical
    construction) changes across time; contrasted with synchronic analysis, which
    examines a single point in time.  In computational linguistics, diachronic
    analysis typically involves aggregating text by period and tracking normalized
    frequencies over time.

<span id="diffusion_equation">Diffusion equation</span>
:   The partial differential equation $\partial c/\partial t = D\,\partial^2 c/\partial x^2$
    that describes how a dissolved substance or heat spreads through a medium at a rate
    proportional to the curvature of its concentration profile.

<span id="dijkstras_algorithm">Dijkstra's algorithm</span>
:   A shortest-path algorithm that processes nodes in order of increasing
    accumulated cost from a source, using a priority queue; at each step it
    relaxes the edges of the cheapest unvisited node and stops when the
    destination is reached.  For a grid with $V$ cells and $E$ edges,
    runtime is $O((V + E)\log V)$ with a binary heap.

<span id="dirichlet_distribution">Dirichlet distribution</span>
:   A distribution over probability vectors (vectors whose entries are
    non-negative and sum to 1); parameterised by a concentration vector
    $\boldsymbol{\alpha}$ whose magnitude controls how concentrated the samples
    are.  Small $\alpha_k$ values produce sparse distributions (most mass on
    one component); large values produce uniform distributions.  The Dirichlet
    is the conjugate prior for the categorical distribution and is used in LDA
    to model both document-topic and topic-word distributions.

<span id="distance_matrix">Distance matrix</span>
:   A square symmetric matrix $D$ where entry $D(i,j)$ stores the evolutionary (or other
    pairwise) distance between taxa $i$ and $j$; the input to tree-reconstruction algorithms.

<span id="dynamic_programming">Dynamic programming</span>
:   An algorithmic strategy that solves a problem by breaking it into overlapping subproblems,
    computing each subproblem once, and storing the results in a table to avoid redundant work.

## E

<span id="euler_mascheroni">Euler-Mascheroni constant</span>
:   The constant $\gamma_E = \lim_{n\to\infty}(\sum_{k=1}^n 1/k - \ln n) \approx 0.5772$;
    appears in the mean of the Gumbel extreme-value distribution as $\mathrm{E}[X] = \mu + \gamma_E \beta$.

<span id="extreme_value_distribution">Extreme value distribution</span>
:   A family of distributions that arise as limiting distributions of sample maxima or minima;
    the Gumbel (Type I) member is commonly used to model annual maximum river flows and other
    environmental extremes.

## F

<span id="false_alarm_rate">False alarm rate</span>
:   The proportion of noise-only trials on which an observer responds "signal
    present": $\text{FAR} = P(\text{yes} \mid \text{noise}) = 1 - \Phi(c)$;
    also called the false positive rate or $1 - \text{specificity}$.

<span id="first_integral">First integral</span>
:   A function of the state variables whose value is constant along every trajectory of a
    dynamical system; also called a conserved quantity or invariant.

<span id="flow_network">Flow network</span>
:   A directed graph in which each edge carries a capacity or weight representing the rate at
    which material (water, traffic, data) moves from source to destination; used here to model
    pollutant transport in a river system.

## G

<span id="gaussian_filter">Gaussian filter</span>
:   A smoothing operation that replaces each pixel (or grid point) with a weighted average of
    its neighbours, where the weights follow a Gaussian (bell-curve) shape centred on the point.

<span id="ghost_cell">Ghost cell</span>
:   An extra grid point added outside the physical boundary of a numerical simulation solely
    to store a boundary value; it allows interior update formulas to be applied uniformly at
    the edge without special-casing.

<span id="gini_coefficient">Gini coefficient</span>
:   A scalar measure of inequality ranging from 0 (perfect equality) to $(n-1)/n$
    (one agent holds all wealth).  For sorted wealth values $w_{(1)} \leq \cdots \leq w_{(n)}$:
    $G = (2\sum_{i=1}^n i\,w_{(i)} - (n+1)\sum w) / (n\sum w)$.
    Geometrically, $G$ is twice the area between the Lorenz curve and the 45-degree line
    of equality.

<span id="global_alignment">Global alignment</span>
:   An alignment that spans both sequences from end to end, inserting gaps wherever necessary
    to align every character; the Needleman-Wunsch algorithm finds the highest-scoring global
    alignment using dynamic programming.

<span id="gradient_descent">Gradient descent</span>
:   An iterative optimisation algorithm that updates parameters in the direction of the
    negative gradient of the loss function; at each step, $\theta \leftarrow \theta - \eta \nabla L$
    where $\eta$ is the learning rate.  For convex losses such as binary cross-entropy,
    gradient descent converges to the global minimum.

<span id="gumbel_distribution">Gumbel distribution</span>
:   FIXME

<span id="gumbel_paper">Gumbel probability paper</span>
:   A plotting technique that rescales the horizontal axis by the reduced variate
    $y = -\ln(-\ln p)$, so that data following a Gumbel distribution plot as a straight line;
    departures from linearity indicate poor fit.

## H

<span id="hamming_distance">Hamming distance</span>
:   The number of positions at which two sequences of equal length differ; when
    normalized by the sequence length, it gives the fraction of positions that differ.
    Used in stemma reconstruction as a measure of how many variant loci separate
    two manuscripts, and in information theory to measure the number of bit errors
    between transmitted and received strings.

<span id="heat_flux">Heat flux</span>
:   The rate of heat energy transfer per unit area through a surface, measured in watts per
    square metre (W m⁻²); in steady-state conduction it equals $-k\,dT/dx$ and is uniform
    throughout any composite wall.

<span id="hit_rate">Hit rate</span>
:   The proportion of signal trials on which an observer correctly responds
    "signal present": $\text{HR} = P(\text{yes} \mid \text{signal}) = 1 - \Phi(c - d')$;
    also called the true positive rate or sensitivity (not to be confused with
    $d'$ sensitivity).

<span id="hold_out">hold out</span>
:   FIXME

## I

<span id="inter_rater_agreement">Inter-rater agreement</span>
:   The degree to which two or more independent raters assign the same category
    to the same observations; raw percent agreement is easy to compute but is
    inflated by chance agreement; Cohen's kappa corrects for this inflation and
    is the standard measure in psychology, clinical research, and annotation.

<span id="inverse_distance_weighting">Inverse-distance weighting (IDW)</span>
:   A spatial interpolation method that estimates the value at a query point as
    a weighted average of observed station values, where each station's weight
    is $d_i^{-p}$ ($d_i$ is the distance from the query point, $p$ is the power
    parameter); larger $p$ concentrates influence on the nearest stations.

## J

<span id="jacobi_iteration">Jacobi iteration</span>
:   An iterative method for solving systems of equations in which each unknown is updated
    to the value that would satisfy its equation if all other unknowns are held at their
    previous values; updates are applied simultaneously to all unknowns in each sweep.
    For the steady-state heat equation on a 1D grid, each interior node is replaced by the
    conductivity-weighted average of its two neighbours, and sweeps continue until
    successive solutions differ by less than a prescribed tolerance.

## K

<span id="k_means">K-means clustering</span>
:   An iterative algorithm that partitions $n$ data points into $K$ clusters by alternating
    between two steps: assigning each point to its nearest centroid (using Euclidean distance)
    and updating each centroid as the coordinate-wise mean of all points assigned to it.
    The algorithm stops when assignments no longer change.  Because initialization is random,
    results can vary across runs; the number of clusters $K$ must be chosen in advance.

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

## L

<span id="landscape_archaeology">Landscape archaeology</span>
:   A subfield of archaeology that studies the spatial distribution of human
    activity across the physical environment; methods include least-cost path
    analysis (reconstructing movement corridors), viewshed analysis, and
    site-catchment analysis.

<span id="latent_dirichlet_allocation">Latent Dirichlet Allocation (LDA)</span>
:   A generative probabilistic model (Blei, Ng, Jordan 2003) for text corpora
    in which each document is represented as a mixture of topics and each topic
    is a distribution over words; both mixtures are drawn from Dirichlet priors
    with concentration parameters $\alpha$ (document-topic) and $\beta$ (topic-word).
    Topics and mixtures are latent (unobserved) and must be inferred from the
    observed words.

<span id="learning_curve">Learning curve</span>
:   A plot of performance (such as reaction time or error rate) against the
    amount of practice (trial number or hours of training); empirically follows
    a power law: $\text{RT}(n) = A \cdot n^{-b}$, where $A$ is the initial
    performance and $b > 0$ is the learning rate exponent.

<span id="least_cost_path">Least-cost path</span>
:   The route through a cost surface that minimises total accumulated travel cost
    from a source to a destination; found by applying Dijkstra's algorithm to a
    grid in which each cell's value represents movement difficulty.  Paths favour
    valleys and passes over ridges when elevation is used as the cost proxy.

<span id="local_alignment">Local alignment</span>
:   An alignment that finds the highest-scoring matching subsequence anywhere within two
    sequences, rather than aligning them from end to end; used to locate conserved domains
    within longer sequences.

<span id="log_log_regression">Log-log regression</span>
:   A linear regression of $\ln y$ on $\ln x$; the OLS slope directly estimates the exponent
    of an underlying power-law relationship $y = A x^b$, and is used in economics to estimate
    price elasticity of demand.

<span id="log_normal_distribution">Log-normal distribution</span>
:   A probability distribution for a positive random variable $X$ such that $\ln X$ follows
    a normal distribution; characterised by its log-mean $\mu_y$ and log-standard-deviation
    $\sigma_y$, and widely used in hydrology to model annual maximum river flows.

<span id="logistic_regression">Logistic regression</span>
:   A classification model that estimates the probability of class membership using a linear
    combination of features passed through the sigmoid function; fitted by minimising binary
    cross-entropy loss with gradient descent.

<span id="lomb_scargle">Lomb-Scargle periodogram</span>
:   FIXME

<span id="lorenz_curve">Lorenz curve</span>
:   A plot of the cumulative share of total wealth held by the bottom $x$ fraction of
    the population (sorted from poorest to richest); a perfectly equal distribution
    produces the 45-degree diagonal, while any inequality bows the curve below it.
    The Gini coefficient equals twice the area between the Lorenz curve and the diagonal.

<span id="lotka_volterra">Lotka-Volterra model</span>
:   A pair of ordinary differential equations describing the coupled dynamics of a prey
    population and a predator population, producing oscillating cycles when the system is
    displaced from its equilibrium.

## M

<span id="mattr">Moving-Average Type-Token Ratio (MATTR)</span>
:   A length-independent measure of vocabulary richness: TTR is computed over each
    overlapping window of fixed width $w$ and the results are averaged.  Because every
    window has the same length, MATTR can fairly compare texts of different total sizes,
    unlike the global TTR which falls as text length increases.

<span id="method_of_moments">Method of moments</span>
:   A parameter-estimation technique that sets the distribution's theoretical moments (mean,
    variance, etc.) equal to their sample counterparts and solves for the unknown parameters;
    simpler to compute than maximum likelihood but generally less statistically efficient.

<span id="moore_neighborhood">Moore neighbourhood</span>
:   The set of up to 8 cells immediately surrounding a cell in a 2-D grid: the
    4 horizontal/vertical neighbours and 4 diagonal neighbours.  Cells on the grid
    boundary have fewer than 8 neighbours.  Used in the Schelling model and in
    cellular automata to define local interactions.

<span id="moving_average">Moving average</span>
:   A smoothing filter that replaces each value in a series with the mean of a fixed-width
    window of neighbouring values, reducing point-to-point noise variance by a factor equal
    to the window width.

## N

<span id="needleman_wunsch">Needleman-Wunsch algorithm</span>
:   A dynamic programming algorithm (Needleman and Wunsch, 1970) for global sequence alignment.
    The first row and column of the scoring matrix are initialised to cumulative gap penalties,
    and the recurrence fills remaining cells as the maximum of a diagonal (match/mismatch) move,
    an upward (gap in the second sequence) move, or a leftward (gap in the first sequence) move.

<span id="neighbor_joining">Neighbor-joining</span>
:   A distance-based algorithm (Saitou and Nei, 1987) that reconstructs a phylogenetic tree
    by iteratively joining the pair of taxa with the smallest corrected distance, running in
    $O(N^3)$ time.

<span id="ngram_profile">N-gram profile</span>
:   The relative frequency distribution of all observed n-grams in a text or
    collection of texts; constructed by counting every n-gram and dividing by
    the total count.  As a probability distribution it can be compared between
    authors using cosine similarity or other distance measures.

<span id="noise_point">Noise point</span>
:   In DBSCAN, a point that is not a core point and is not within distance
    $\varepsilon$ of any core point; labelled $-1$ and not assigned to any cluster.
    Noise points correspond to outliers or isolated observations that do not belong
    to any dense region.

<span id="non_maximum_suppression">Non-maximum suppression</span>
:   A post-processing step that scans a list of candidate detections and discards any candidate
    that is not the tallest within a specified neighbourhood, preventing one broad peak or blob
    from being reported as multiple detections.

<span id="normalized_frequency">Normalized frequency</span>
:   A word's count in a period divided by the total token count for the same period,
    expressing the word's share of the corpus rather than its raw occurrence count.
    Normalized frequencies sum to 1.0 within each period and are comparable across
    periods of different sizes, unlike raw counts.

## O

<span id="ordinary_least_squares">Ordinary least squares</span>
:   A method for fitting a linear model $y = Xb$ by minimising the sum of squared residuals
    $\|y - Xb\|^2$; the closed-form solution is $\hat{b} = (X^TX)^{-1}X^Ty$, and the slope
    uncertainty is quantified by the standard error $\text{SE}(\hat{b}) = \sqrt{\hat{\sigma}^2(X^TX)^{-1}}$.

## P

<span id="percolation_threshold">Percolation threshold</span>
:   The critical probability $p_c$ at which a large random network transitions from almost
    certainly disconnected to almost certainly connected; for 2D site percolation on a square
    lattice with 4-neighbor connectivity, $p_c \approx 0.5927$.

<span id="phase_portrait">Phase portrait</span>
:   A plot of one state variable against another (e.g., predator vs. prey population) showing
    the family of trajectories a dynamical system can follow, without reference to time.

<span id="phylogenetic_tree">Phylogenetic tree</span>
:   A branching diagram showing the inferred evolutionary relationships among a set of taxa,
    with leaves representing observed taxa and internal nodes representing their common ancestors.

<span id="power_law">Power law</span>
:   A mathematical relationship of the form $y = A x^b$; on a log-log plot the
    relationship appears as a straight line with slope $b$.  In learning-curve
    analysis $b > 0$ is the learning rate exponent, quantifying how rapidly
    performance improves with practice.

<span id="price_elasticity">Price elasticity of demand</span>
:   The percentage change in quantity demanded for a 1% change in price:
    $\varepsilon = \partial \ln Q / \partial \ln P$; values below $-1$ indicate elastic demand
    (quantity is highly responsive to price) and values between $-1$ and $0$ indicate inelastic
    demand.

## Q

<span id="q_matrix">Q-matrix</span>
:   A corrected distance matrix used in the neighbor-joining algorithm where each entry
    $Q(i,j) = (n-2)D(i,j) - \sum_k D(i,k) - \sum_k D(j,k)$ removes the bias introduced by
    branches of unequal length.

## R

<span id="radial_velocity">Radial velocity</span>
:   The component of a star's velocity along the observer's line of sight; measured via
    Doppler shifts in spectral lines and used to detect the gravitational wobble caused by
    an orbiting planet.

<span id="reduced_variate">Reduced variate</span>
:   The dimensionless quantity $y = -\ln(-\ln p)$ used in extreme-value analysis; it linearises
    the Gumbel CDF so that data following a Gumbel distribution plot as a straight line against
    the corresponding quantiles on Gumbel probability paper.

<span id="return_period">Return period</span>
:   Also called recurrence interval; the average time between events that exceed a given
    threshold.  A $T$-year event has probability $1/T$ of being exceeded in any single year
    and probability $1-(1-1/T)^T \approx 63\%$ of being exceeded at least once in $T$ years.

<span id="riemann_sum">Riemann sum</span>
:   FIXME

<span id="right_censoring">Right-censoring</span>
:   A form of censoring in survival analysis where the true event time is known only to exceed
    the observation time; arises when a study ends before all participants experience the event
    or when participants withdraw.  The Kaplan-Meier estimator handles right-censored data
    without bias.

<span id="roc_curve">ROC curve</span>
:   Receiver Operating Characteristic curve; a plot of hit rate against
    false-alarm rate as the decision criterion varies from very conservative
    to very liberal; summarized by the area under the curve (AUC), which equals
    the probability that a randomly chosen signal trial produces higher internal
    evidence than a randomly chosen noise trial; AUC = 0.5 at chance and
    AUC = 1.0 at perfect sensitivity.

<span id="rolling_window">Rolling window</span>
:   A fixed-width buffer of the $w$ most recent observations used to compute local summary
    statistics (mean, variance) that adapt to gradual changes in the signal; also called a
    moving window or sliding window.

<span id="runge_kutta">Runge-Kutta method</span>
:   FIXME

## S

<span id="schelling_model">Schelling model</span>
:   An agent-based simulation of residential segregation (Schelling, 1971) in which
    agents on a grid move to random empty cells whenever fewer than a threshold fraction
    of their occupied neighbours share their type; even mild thresholds (around 30%)
    produce strong large-scale segregation, illustrating that macro-level patterns
    can emerge from micro-level rules without any deliberate collective intent.

<span id="semi_amplitude">Semi-amplitude</span>
:   The quantity $K$ in a sinusoidal radial-velocity model, equal to the maximum speed of the
    star relative to the centre of mass of the star-planet system; related to the planet's
    minimum mass and orbital period.

<span id="sigmoid_function">Sigmoid function</span>
:   The function $\sigma(z) = 1/(1 + e^{-z})$ that maps any real number to the open interval
    $(0,1)$; used in logistic regression to convert a linear score into a probability.

<span id="signal_detection_theory">Signal detection theory</span>
:   A framework for separating an observer's perceptual sensitivity from their
    response tendency by modeling the internal decision variable as two overlapping
    normal distributions (signal and noise) and fitting both the hit rate and
    false-alarm rate jointly; the key measures are $d'$ (sensitivity) and
    criterion $c$ (response bias).

<span id="signal_to_noise">signal-to-noise ratio</span> (SNR)
:   FIMXE

<span id="sir_model">SIR model</span>
:   A compartmental epidemic model that divides a fixed population into Susceptible, Infectious,
    and Recovered compartments; individuals move irreversibly from S to I at rate $\beta SI/N$
    and from I to R at rate $\gamma I$, producing a single epidemic wave when $R_0 = \beta/\gamma > 1$.

<span id="site_percolation">Site percolation</span>
:   A percolation model in which each site (cell) of a lattice is independently declared open
    with probability $p$; the question is whether open sites form a connected path from one
    boundary to the other.  Contrast with bond percolation, where edges rather than sites are opened.
:   The function $\sigma(z) = 1/(1 + e^{-z})$ that maps any real number to the open interval
    $(0,1)$; used in logistic regression to convert a linear score into a probability.

<span id="smith_waterman">Smith-Waterman algorithm</span>
:   A dynamic-programming algorithm (Smith and Waterman, 1981) that computes the optimal local
    alignment of two sequences by filling a scoring matrix with a recurrence that includes a
    zero floor, allowing alignments to start anywhere.

<span id="spatial_clustering">Spatial clustering</span>
:   The task of partitioning geographic point locations into groups whose members
    are spatially proximate to each other, without specifying the number of groups
    in advance; used in landscape archaeology, ecology, and epidemiology to
    identify concentrations of sites, organisms, or cases.

<span id="spatial_interpolation">Spatial interpolation</span>
:   The estimation of a continuous spatial field (such as temperature or
    precipitation) at unsampled locations from observations at a discrete set of
    known locations; methods include inverse-distance weighting, kriging, and
    splines; all rely on the principle of spatial autocorrelation.

<span id="spike_outlier">Spike outlier</span>
:   An isolated measurement that is far from the local baseline and immediately returns to
    normal; contrasted with a step change, which is a sustained shift.  A rolling z-score
    detector flags the spike reading but quickly returns to normal z-scores once the spike
    leaves the window.

<span id="stemma">Stemma</span>
:   The family tree of manuscript copies of a historical text, showing which copies
    derive from which others; internal nodes represent lost intermediate ancestors and
    leaves represent surviving manuscripts.  In classical philology the stemma is used
    to reconstruct the most likely original reading when manuscripts disagree.

<span id="stemma_reconstruction">Stemma reconstruction</span>
:   The computational task of recovering the copying tree of a set of manuscripts
    from patterns of shared variant readings; analogous to phylogenetic tree
    reconstruction in evolutionary biology, using the same neighbor-joining algorithm
    applied to a Hamming-distance matrix rather than a DNA substitution matrix.

<span id="step_change">Step change</span>
:   A sudden, sustained shift in the baseline level of a time series; the rolling-window
    z-score detector flags readings near the transition but adapts once the window has fully
    moved into the new regime.

<span id="structural_break">Structural break</span>
:   A point in time at which the statistical properties of a time series (mean, variance,
    or trend) shift abruptly and permanently; also called a change point or regime change.
    Failing to account for a break leads to biased parameter estimates and unreliable
    forecasts when a regression is fitted over a period that straddles the break.

<span id="survival_function">Survival function</span>
:   The probability that a randomly chosen individual has not yet experienced the event of
    interest by time $t$: $S(t) = P(T > t)$; always starts at 1, is non-increasing, and
    approaches 0 as $t \to \infty$ if all individuals eventually experience the event.

## T

<span id="term_frequency">Term frequency (TF)</span>
:   The count of how many times each word in the vocabulary appears in a given document,
    stored as a vector with one entry per vocabulary word.  Raw TF counts are proportional
    to document length, so longer documents produce larger vectors; dividing by the document's
    L2 norm (or total token count) gives a length-normalized vector that reflects the
    shape of word use rather than total volume.

<span id="thermal_conductivity">Thermal conductivity</span>
:   A material property $k$ (W m⁻¹ K⁻¹) measuring how readily heat flows through a material;
    high $k$ (e.g. metals) allows large heat flux for a small temperature gradient.

<span id="thermal_resistance">Thermal resistance</span>
:   For a uniform layer of thickness $L$ and conductivity $k$, the resistance $R = L/k$
    (m² K W⁻¹) represents the temperature drop per unit heat flux; layers in series add.

<span id="transfer_matrix">Transfer matrix</span>
:   A square matrix $T$ where entry $T[i,j]$ gives the fraction of material at node $j$ that
    moves to node $i$ in one time step; when every column sums to 1 (column-stochastic), the
    total amount of material is exactly conserved at every step.

<span id="trapezoidal_rule">trapezoidal rule</span>
:   FIXME

<span id="tridiagonal_system">Tridiagonal system</span>
:   A linear system $A\mathbf{x} = \mathbf{b}$ in which $A$ has nonzero entries only on the
    main diagonal and the two diagonals immediately above and below it; arises from 1D
    finite-difference discretization and can be solved in $O(n)$ time.

<span id="truncation_error">Truncation error</span>
:   The error introduced at each time step by approximating continuous derivatives with finite
    differences; for the explicit diffusion scheme the global truncation error scales as
    $O(\Delta t + \Delta x^2)$.

<span id="type_token_ratio">Type-token ratio (TTR)</span>
:   The number of distinct word types divided by the total number of word tokens in a
    text: $\text{TTR} = V/T$.  A value near 1 indicates high lexical diversity (few
    repetitions); a value near 0 indicates heavy repetition.  TTR is sensitive to text
    length — it decreases for longer texts even when richness is constant — so MATTR
    is preferred for cross-text comparisons.

## U

<span id="upgma">UPGMA</span>
:   Unweighted Pair Group Method with Arithmetic Mean; a distance-based algorithm that
    reconstructs a rooted phylogenetic tree by iteratively merging the pair of taxa (or
    clusters) with the smallest average pairwise distance, placing each new node at height
    $D(i,j)/2$.  UPGMA assumes a molecular clock (constant evolutionary rate across all
    lineages); when rates vary, the recovered topology may be incorrect.

## V

<span id="variant_locus">Variant locus</span>
:   A specific position in a text where at least two manuscripts have different
    readings; the collection of variant loci across a set of manuscripts provides
    the character data used to compute pairwise Hamming distances for stemma
    reconstruction.

<span id="von_neumann_stability">von Neumann stability condition</span>
:   FIXME

## W

<span id="word_shift">Word shift</span>
:   A change in the relative frequency of a word across time periods; a positive
    shift means the word's share of tokens rose, a negative shift means it fell.
    Quantified as the OLS slope of normalized frequency against decade index.

## X

## Y

<span id="yardsale">yardsale</span>
:   FIXME

## Z

<span id="z_score">Z-score</span>
:   The number of standard deviations by which an observation deviates from a reference mean:
    $z = (x - \bar{x}) / \hat{\sigma}$; used in anomaly detection to flag readings that are
    unusually far from the local rolling mean.

<span id="zipf_law">Zipf's law</span>
:   The empirical regularity (Zipf, 1949) that the $k$-th most frequent word in a large
    corpus appears roughly $1/k$ times as often as the most frequent word; equivalently,
    word frequency is approximately proportional to $1/\text{rank}$.  The resulting
    distribution has a heavy tail: a few words are extremely common and a large number
    of words are rare.  Used here to generate synthetic text corpora that mimic the
    statistical properties of natural language.
