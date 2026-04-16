# Mineral Classification by Geochemistry

## The Problem

-   Geochemists measure rock samples as oxide weight percentages (wt%),
    which is the fraction of each chemical compound in the rock
-   A classifier that assigns samples to mineral classes from their chemistry
    automates a task that otherwise requires expert visual inspection of thin sections under a microscope
-   We train a [%g logistic_regression "logistic regression" %] model on
    $\text{SiO}_2$ (silica) and $\text{Al}_2\text{O}_3$ (alumina)
    to separate felsic rocks (granite-like, silica-rich) from mafic rocks (basalt-like, silica-poor)

## Generating Synthetic Geochemical Data

-   We start with synthetic data drawn from two Gaussian distributions
    that mimic the composition ranges reported in igneous petrology textbooks
-   Felsic rocks average 70 wt% $\text{SiO}_2$ and 14 wt% $\text{Al}_2\text{O}_3$
    -   Mafic rocks average 50 wt% $\text{SiO}_2$ and 9 wt% $\text{Al}_2\text{O}_3$
-   The two distributions overlap because real mineral classification is never perfectly clean

[%inc generate_mineral.py mark="constants"%]
[%inc generate_mineral.py mark="make-data"%]

## The Logistic Regression Model

-   The model predicts the probability that a sample is mafic (class 1):

<p>$$p = \sigma(w_0 \cdot x_0 + w_1 \cdot x_1 + b) = \frac{1}{1 + e^{-(w_0 x_0 + w_1 x_1 + b)}}$$</p>

-   $\sigma$ is the [%g sigmoid_function "sigmoid function" %], which maps any real number to $(0, 1)$
-   $x_0$ and $x_1$ are the (normalised) $\text{SiO}_2$ and $\text{Al}_2\text{O}_3$ concentrations
-   $w_0$, $w_1$, and $b$ are learned from data

[%inc mineral.py mark="sigmoid"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why must features be normalized before training logistic regression with gradient descent?

Normalisation makes the sigmoid output exactly 0.5 at the start of training.
:   Wrong: initial weights are zero, so $z = 0$ and $\sigma(0) = 0.5$ regardless of feature scale.

Features on very different scales cause gradient descent to take very small steps along
one axis and large steps along another, slowing convergence.
:   Correct: unnormalized gradients have components proportional to feature magnitude,
    creating an elongated loss surface that makes convergence slow and erratic.

Normalization ensures the model cannot overfit by constraining the weight magnitudes.
:   Wrong: normalization changes the input scale, not the weight values; regularization
    is the standard tool for constraining weights.

The sigmoid function is only defined for inputs in $[0, 1]$.
:   Wrong: the sigmoid is defined for all real numbers; the $[0, 1]$ interval is its output range.

</div>

[%inc mineral.py mark="normalize"%]

## Training by Gradient Descent

-   At each iteration, the model computes the [%g cross_entropy "binary cross-entropy" %] loss:

<p>$$\mathcal{L} = -\frac{1}{n}\sum_{i=1}^n \left[ y_i \log p_i + (1 - y_i) \log(1 - p_i) \right]$$</p>

-   The gradient of $\mathcal{L}$ with respect to the weights is $\mathbf{X}^\top (\mathbf{p} - \mathbf{y}) / n$,
    and with respect to the bias is $\text{mean}(\mathbf{p} - \mathbf{y})$
-   Each gradient-descent step subtracts the gradient scaled by the learning rate

[%inc mineral.py mark="train"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Put the steps of one gradient-descent iteration in the correct order.

1.  Compute the linear combination $z = X w + b$
1.  Apply the sigmoid to get predicted probabilities $\hat{p} = \sigma(z)$
1.  Evaluate the binary cross-entropy loss
1.  Compute gradients $\partial \mathcal{L}/\partial w$ and $\partial \mathcal{L}/\partial b$
1.  Update weights: $w \leftarrow w - \alpha \cdot \partial \mathcal{L}/\partial w$

</div>

## Decision Boundary and Classification

-   The decision boundary is the line where $p = 0.5$, i.e., where $w_0 x_0 + w_1 x_1 + b = 0$
-   Rearranging for $x_1$ ($\text{Al}_2\text{O}_3$) as a function of $x_0$ ($\text{SiO}_2$) gives:

<p>$$x_1 = -\frac{w_0 x_0 + b}{w_1}$$</p>

-   Because features were normalised during training,
    the boundary must be mapped back to original units before plotting

[%inc mineral.py mark="boundary"%]
[%inc mineral.py mark="predict"%]

[%figure
  slug="mineral-boundary"
  img="mineral.svg"
  alt="Scatter plot of SiO₂ vs Al₂O₃ with felsic (blue circles) and mafic (red triangles) training samples and a dashed decision boundary."
  caption="Training data for 120 samples (80% of 160 total). The dashed line is the learned decision boundary. The two classes are well separated in SiO₂ but overlap slightly in Al₂O₃."
%]

<div class="forma-matching" data-lang="en" markdown="1">

Match each component of the logistic regression model to its role.

| Component | Role |
| --------- | ---- |
| $w_0 x_0 + w_1 x_1 + b$ | Separating hyperplane in feature space |
| $\sigma(\cdot)$ | Maps the linear score to a probability |
| $\mathcal{L}$ | Penalises confident wrong predictions more heavily than uncertain ones |
| Decision boundary | The surface where the model is maximally uncertain ($p = 0.5$) |

</div>

## Testing

Sigmoid known values
:   $\sigma(0) = 0.5$ exactly,
    $\sigma(z) \to 1$ as $z \to +\infty$,
    and $\sigma(z) \to 0$ as $z \to -\infty$.
    These are identities that must hold regardless of the training data.

Normalization properties
:   After normalization, each feature column must have mean 0 and standard deviation 1.
    Applying training statistics to test data must reproduce $(\mathbf{x} - \mu) / \sigma$
    without recomputing $\mu$ or $\sigma$ from the test set.

Loss decreases during training
:   A correct gradient-descent implementation
    must reduce the cross-entropy loss monotonically over the first 100 iterations.
    An increase would indicate a sign error in the gradient or an excessively large learning rate.

Accuracy on well-separated data
:   The two classes are separated by roughly 6.7 standard deviations in $\text{SiO}_2$.
    A correctly trained classifier must achieve at least 95% accuracy; a lower score indicates a bug.

Accuracy with seed=42
:   With default parameters, held-out test accuracy must reach at least 95%.
    The tolerance of 5% is wide enough to accommodate small variations between random seeds
    while still catching a failed classifier.

Predict with known weights
:   With $w = [10, 0]$ and $b = 0$, the boundary is at $x_0 = 0$.
    A sample with $x_0 = 1$ must be predicted class 1
    and a sample with $x_0 = -1$ must be predicted class 0.

[%inc test_mineral.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Mineral classification key terms

Felsic rock
:   Silica-rich igneous rock (granite, rhyolite); typically $\text{SiO}_2 > 63$ wt%

Mafic rock
:   Silica-poor, magnesium- and iron-rich igneous rock (basalt, gabbro); typically $\text{SiO}_2 < 52$ wt%

Sigmoid function
:   $\sigma(z) = 1/(1 + e^{-z})$; maps any real number to the open interval $(0, 1)$ for use as a probability

Binary cross-entropy
:   $-[y \log p + (1-y)\log(1-p)]$; loss function that penalises confident wrong predictions

Decision boundary
:   The surface in feature space where the model assigns equal probability to both classes; a line for two features

Gradient descent
:   Iterative optimisation that moves weights in the direction that most rapidly decreases the loss

</div>

<section class="exercises" markdown="1">

## Exercises

### Do the math

The Mahalanobis distance between two univariate Gaussians with means $\mu_1$, $\mu_2$ and
equal standard deviation $\sigma$ is $|\mu_1 - \mu_2| / \sigma$.
Using `FELSIC_MEAN[0] = 70`, `MAFIC_MEAN[0] = 50`, `FELSIC_STD[0] = 3`,
what fraction of the $\text{SiO}_2$ distributions overlap?
(Hint: use the 68-95-99.7 rule: the distance is about $6.7\sigma$, so overlap $\approx 0$.)

### Three-class classification

Add a third class (ultramafic rocks, e.g. peridotite, with $\text{SiO}_2 \approx 42$ wt% and $\text{Al}_2\text{O}_3 \approx 3$ wt%).
Extend `train` to use the softmax function and categorical cross-entropy loss instead of the
binary formulation.  Report per-class precision and recall on a held-out test set.

### Learning-rate sensitivity

Run `train` with learning rates $\alpha \in \{0.001, 0.01, 0.1, 1.0, 10.0\}$ for 500
iterations each.  Plot the final training loss as a function of $\alpha$ and identify the
range where gradient descent converges reliably.  Explain why very large learning rates
cause divergence.

### Decision boundary as a function of iteration count

Save the weights $w$ and bias $b$ every 50 iterations during training.  Plot the decision
boundary at each checkpoint on the same scatter plot.  Show that the boundary rotates and
shifts as training progresses and stabilises near the optimum.

### Effect of class imbalance

Generate a dataset with 160 felsic samples and 20 mafic samples.  Train the classifier and
report the confusion matrix.  Show that the model achieves high overall accuracy by
predicting felsic almost everywhere, then implement class-weighted cross-entropy loss
(multiply the mafic term by `n_felsic / n_mafic`) and show that it recovers better
detection of the minority class.

</section>
