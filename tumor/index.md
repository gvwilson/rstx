# Tumor Classification by Logistic Regression

## The Problem

-   Computational pathology extracts quantitative features from tissue images — cell size,
    shape irregularity, nuclear-to-cytoplasm ratio — and uses them to predict whether a
    sample is benign or malignant.
-   Logistic regression is the simplest model that outputs
    a probability rather than a raw score: the predicted class-1 probability lies in $(0, 1)$
    so it can be interpreted directly as a risk estimate.
-   It fits a linear boundary in feature space and is easy to train, interpret, and test;
    more complex models often offer little additional accuracy when the classes are linearly separable.

## The Logistic Regression Model

-   A linear combination of features $\mathbf{x}$ produces a score $z = \mathbf{w} \cdot \mathbf{x} + b$.
-   The sigmoid function $\sigma(z) = 1/(1 + e^{-z})$ maps $z$ to a
    probability in $(0, 1)$:

<p>$$p = \sigma(z) = \frac{1}{1 + e^{-z}}$$</p>

-   At $z = 0$ the model is completely uncertain: $\sigma(0) = 0.5$.
-   The predicted class is 1 when $p \geq 0.5$, which is equivalent to $z \geq 0$.

[%inc tumor.py mark="sigmoid"%]

[%inc tumor.py mark="model"%]

<div class="forma-numeric-entry" data-correct="0.731" data-tolerance="0.002" data-lang="en" markdown="1">

A logistic regression model with $\mathbf{w} = [1, 0]$ and $b = 1$ receives input
$\mathbf{x} = [0, 0]$.  Compute $\sigma(0 \cdot 1 + 0 \cdot 0 + 1) = \sigma(1)$ to three decimal places.

</div>

## Training: Minimising Binary Cross-Entropy

-   The binary cross-entropy loss penalises confident wrong predictions:

<p>$$L(\mathbf{w}, b) = -\frac{1}{n} \sum_{i=1}^{n} \left[ y_i \log p_i + (1 - y_i) \log(1 - p_i) \right]$$</p>

-   [%g gradient_descent "Gradient descent" %] iteratively moves $\mathbf{w}$ and $b$ downhill:

<p>$$\frac{\partial L}{\partial \mathbf{w}} = \frac{1}{n} X^T (\mathbf{p} - \mathbf{y}) \qquad \frac{\partial L}{\partial b} = \frac{1}{n} \sum_i (p_i - y_i)$$</p>

-   The update rule at each step is $\mathbf{w} \leftarrow \mathbf{w} - \eta \partial L / \partial \mathbf{w}$
    where $\eta$ is the learning rate.

[%inc tumor.py mark="train"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

In the gradient update `w -= lr * (X.T @ residual) / n`, what does `residual` represent?

The difference between predicted probability and the true label for each sample
:   Correct: `residual = proba - y` is the error vector $(p_i - y_i)$ for all $n$ samples; the gradient is its weighted sum.

The difference between the current loss and the minimum possible loss
:   Wrong: the residual is per-sample, not a scalar measuring how far we are from the optimum.

The weight vector from the previous iteration
:   Wrong: the weight vector is `w`; `residual` measures how wrong the current predictions are.

The learning rate scaled by the sample size
:   Wrong: the learning rate is a separate scalar `lr`; `residual` is a vector of prediction errors.

</div>

## Generating Synthetic Data

-   Two isotropic Gaussian clusters in 2D simulate benign (centred at $[1.5, 1.5]$) and
    malignant (centred at $[3.5, 3.5]$) cell populations.
-   The Euclidean distance between class means is $\sqrt{8} \approx 2.83$ standard deviations,
    making the classes well-separated but not trivially so.

[%inc generate_tumor.py mark="constants"%]

[%inc generate_tumor.py mark="generate"%]

## Evaluating the Classifier

-   A [%g confusion_matrix "confusion matrix" %] tabulates the four combinations of actual and
    predicted class: true negatives (TN), false positives (FP), false negatives (FN), and true
    positives (TP).
-   False negatives (malignant predicted as benign) are typically more harmful than false positives
    in cancer screening, which motivates choosing a threshold below 0.5 in practice.

[%inc tumor.py mark="evaluate"%]

<div class="forma-labeling" data-lang="en" markdown="1">

Label each cell of the 2X2 confusion matrix [[TN, FP], [FN, TP]].

| Cell | Meaning |
| ---- | ------- |
| TN (top-left) | Sample is benign and model predicted benign — a correct negative |
| FP (top-right) | Sample is benign but model predicted malignant — a false alarm |
| FN (bottom-left) | Sample is malignant but model predicted benign — a missed cancer |
| TP (bottom-right) | Sample is malignant and model predicted malignant — a correct positive |

</div>

## Visualizing the Decision Boundary

[%inc tumor.py mark="plot"%]

[%figure
  slug="tumor-boundary"
  img="tumor.svg"
  alt="2D scatter plot of 300 samples in two colours (benign=blue, malignant=red) separated by a dashed diagonal decision boundary."
  caption="Logistic regression applied to 300 synthetic tumour samples. The dashed black line is the learned decision boundary $w_1 x_1 + w_2 x_2 + b = 0$. Test accuracy 96.7%: two benign samples misclassified as malignant, zero malignant samples missed."
%]

## Testing

-   Sigmoid exact values
    -   $\sigma(0) = 0.5$ is an exact algebraic identity; no tolerance is needed.
    -   $\sigma(\pm 100)$ saturates to $1$ or $0$ to within $10^{-10}$; this catches any sign
        error in the exponent argument.
-   Zero weights produce constant probability
    -   With $\mathbf{w} = \mathbf{0}$ and $b = 0$ the model outputs $0.5$ for every input; this
        verifies that `predict_proba` correctly passes the linear combination through `sigmoid`.
-   Confusion matrix — perfect and all-wrong classifiers
    -   A perfect classifier has $\text{TP} = \text{TN} = 2$ and $\text{FP} = \text{FN} = 0$;
        the all-wrong classifier swaps TN/TP with FP/FN.
    -   Using a 4-sample input makes every cell of the $2\times2$ matrix exactly one or two,
        allowing integer comparison without any tolerance.
-   Accuracy
    - A perfect match gives accuracy 1.0; an all-wrong match gives 0.0.  Both are exact.
-   Training converges on separable data
    -   Class means 3.3 standard deviations apart in each feature; 2000 iterations at
        learning rate 0.1.  Accuracy above 95% is a conservative bound — the measured value
        is 97.7% on the full dataset.  The safety factor of $\approx 1.03$ above the threshold
        accommodates random seeds that produce slightly less-separated draws.

[%inc test_tumor.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Logistic regression key terms

Sigmoid function $\sigma(z)$
:   $1/(1+e^{-z})$; maps any real score to $(0,1)$ and equals 0.5 at $z=0$, where the model is uncertain

Binary cross-entropy
:   Loss function $-[y\log p + (1-y)\log(1-p)]$; heavily penalises confident wrong predictions (e.g. $p \approx 0$ when $y = 1$)

Gradient descent
:   Iteratively subtracts a learning-rate-scaled gradient from the weights; converges to a local minimum for convex losses like cross-entropy

Decision boundary
:   The hyperplane $\mathbf{w}\cdot\mathbf{x} + b = 0$ where predicted probability is exactly 0.5; samples on either side receive different class labels

Confusion matrix
:   A $2\times2$ table of TN, FP, FN, TP counts; shows not just overall accuracy but the types of errors the model makes

</div>

<section class="exercises" markdown="1">

## Exercises

### Feature normalisation

Logistic regression is sensitive to feature scale: a feature with large absolute values
dominates the dot product before training has adjusted the corresponding weight.
Normalise each feature to zero mean and unit variance before training:
$x' = (x - \bar{x}) / \hat{\sigma}$.
Show that normalisation speeds up convergence (reaches the same accuracy in fewer iterations)
when the two features have very different scales (e.g. feature 1 in $[0, 100]$ and feature 2
in $[0, 1]$).

### Precision, recall, and F1

Overall accuracy can be misleading when classes are imbalanced.
Implement functions for precision $= \text{TP}/(\text{TP}+\text{FP})$,
recall $= \text{TP}/(\text{TP}+\text{FN})$, and
$F_1 = 2 \cdot \text{precision} \cdot \text{recall} / (\text{precision} + \text{recall})$.
Generate a dataset where class 1 is 10% of the data and show that high accuracy is achievable
by predicting class 0 always — while precision, recall, and $F_1$ expose the failure.

### Decision threshold adjustment

The default threshold of 0.5 minimises misclassification rate on balanced classes.
For cancer screening, false negatives (missed malignancies) should be penalised more than
false positives.
Plot precision and recall as functions of the decision threshold from 0.1 to 0.9.
Find the threshold that achieves recall $\geq 0.98$ with the highest possible precision.

### Multinomial extension

Extend the binary classifier to three classes (benign, low-grade malignant, high-grade malignant).
Generate three Gaussian clusters and implement softmax regression using the one-vs-rest
strategy: train one binary classifier per class and predict the class with the highest
predicted probability.  Report the three-class confusion matrix.

</section>
