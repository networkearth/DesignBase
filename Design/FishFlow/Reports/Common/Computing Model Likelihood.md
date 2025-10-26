This function efficiently computes the likelihood of each model given some dataset $D$ in the family of models spanned by a model and its reference model. 

##### Definitions:
-  $N_D$: number of decisions in the dataset $D$. 
- $N_C$: maximum number of choices across all decisions in $D$.
## `log_likelihood_member`: Log Likelihood for an $\epsilon$

### Interfaces

```python
log_likelihood_member(
	epsilon, reference_model_matrix, model_matrix, selections_matrix
) --> log_likelihood
```
See below for more detail. 
### Build

##### Inputs:
- $\epsilon$: a number ranging between $0$ and $1$.
- $G_{B}$:  an $N_D$ by $N_C$ matrix with the with the probabilities for each choice in each decision for the reference model. 
- $G_{H}$: an $N_D$ by $N_C$ matrix with the with the probabilities for each choice in each decision for the non-reference model. 
- $C$: a binary $N_D$ by $N_C$ matrix indicating which choice was selected for each decision. That is the sum of each row is exactly $1$. 
##### Outputs
- Log likelihood of the data $D$ given the distribution family member defined by $G_B$, $G_H$, and $\epsilon$. 
##### Steps:
First we'll compute the odds given by this member of the distribution family: 

$$O=\epsilon G_H+(1-\epsilon)G_B$$
and the $G_{\epsilon_k}$ given by:

$$G_{\epsilon}=\frac{o_{ij}}{\sum_{j} o_{ij}}$$
where $o_{ij}$ represents each element of $O$. I.e., we are dividing each element by its row sum to produce a probability. 

From this the likelihood of each datapoint is:

$$P(D_i | \epsilon)=\sum_{row}G_{\epsilon}\bullet C$$
where the $\bullet$ indicates element wise multiplication. (We are only pulling the probabilities associated with the choices that were actually made) This will result in a single column with a probability for each decision's choice given $G_{\epsilon}$. 

We can then get the log likelihood of the data given the guess $G_{\epsilon}$ as:

$$\sum_i \log{P(D_i| \epsilon)}$$
#### Placement

```
fishflow
|
+-- reports
|   |
|   +-- fishflow
|   |   |
|   |   +-- common
|   |   |   |
|   |   |   +-- support.py <--
```
### Constraints

`numpy` should be used for matrix operations.
## Function `prob_members`: Compute Likelihood of Members

### Interfaces

```python
prob_members(
	reference_model_matrix,
	model_matrix,
	selections_matrix,
	epsilons,
	prior_probs=None
) --> likelihoods
```

See below for further detail

### Build
##### Inputs:
- $G_{B}$:  an $N_D$ by $N_C$ matrix with the with the probabilities for each choice in each decision for the reference model. 
- $G_{H}$: an $N_D$ by $N_C$ matrix with the with the probabilities for each choice in each decision for the non-reference model. 
- $C$: a binary $N_D$ by $N_C$ matrix indicating which choice was selected for each decision. That is the sum of each row is exactly $1$. 
- $E$: an array of $\epsilon_i$ ranging from $0$ to $1$. Each member of the family is defined by one of these $\epsilon_i$.
- Optional $P(\epsilon_i)$: prior likelihoods for each $\epsilon_i$. Defaults to even likelihood for all $\epsilon_i$. 
##### Outputs
- $P(\epsilon_i | D)$: the likelihood of the guess defined by $\epsilon_i$ given the data $D$ and prior $P(\epsilon_i)$ 

##### Steps

If $\epsilon_k$ is the minimum $\epsilon_i \in E$ then compute:

$$L_k=\log{P(\epsilon_0)}+\sum_j \log{P(D_j| \epsilon_k)}$$
using `log_likelihood_member`. Now for each other $\epsilon_i$ compute:

$$L_i=\log{P(\epsilon_i)}+\sum_j \log{P(D_j| \epsilon_i)}$$
Then we can compute:

$$r_i=e^{L_i - L_k}$$
Note that this corresponds to:

$$r_i=\frac{P(\epsilon_i)\prod_j P(D_j| \epsilon_i)}{P(\epsilon_k)\prod_j P(D_j| \epsilon_k)}$$
but by using the logarithms it is numerically stable. This ratio is equal to the ratio of $P(\epsilon_i |D)/P(\epsilon_k|D)$ in the posterior distribution. Therefore we can compute:

$$P(\epsilon_i|D)=\frac{r_i}{\sum_j r_j}$$
and return our result!

#### Placement

```
fishflow
|
+-- reports
|   |
|   +-- fishflow
|   |   |
|   |   +-- common
|   |   |   |
|   |   |   +-- support.py <--
```

### Constraints

`numpy` should be used for matrix operations.