#  Desired Distribution Allocator

This is a script to solve a math problem.

> We have a histogram and want to morph it into a new shape

  1)  Given a set of labeled buckets with known item counts...
  2)  Given a new amount of items to place into the buckets...
  3)  Given a desired distribution of items for the buckets...

How should we place the new items into the buckets?

## Motivation

I have a few investment funds and want them each to have a certain percent of my savings.  I want to add money to my savings.  I need to know which funds to put the money in to reach my desired allocation.

## Setup

1.  Clone the repository.
2.  Create a conda environment.

```bash
conda env create -f environment.yml
conda activate DesiredDistributionAllocator
```

## Usage

```bash
python -m allocate --config allocate.yaml --solver add_value_only
```

## Input

The input is a hierarchy of bins with current values and desired ratios.

#### yaml

The input can be given as a YAML file.

```yaml
# allocate.yaml
- { label: '0', optimal_ratio: 100, current_value: 5500, amount_to_add: 10000, children: ['A', 'B', 'C'] }
- { label: 'A', optimal_ratio:  45, current_value: 1000, amount_to_add:     0, children: [] }
- { label: 'B', optimal_ratio:  20, current_value: 1500, amount_to_add:     0, children: [] }
- { label: 'C', optimal_ratio:  35, current_value: 3000, amount_to_add:     0, children: ['Q', 'R'] }
- { label: 'Q', optimal_ratio:  65, current_value: 1200, amount_to_add:     0, children: [] }
- { label: 'R', optimal_ratio:  35, current_value: 1800, amount_to_add:     0, children: [] }
```

#### csv

The input can be given as a CSV file.

```csv
label  optimal_ratio  current_value  amount_to_add   children
    0          100.0         5500.0        10000.0      A;B;C
    A           45.0         1000.0            0.0
    B           20.0         1500.0            0.0
    C           35.0         3000.0            0.0        Q;R
    Q           65.0         1200.0            0.0
    R           35.0         1800.0            0.0
```

#### graph

The following graph will be generated from the above input.

```
0        level=[0] current_value=[ 5,500.00] optimal_ratio=[1.000] amount_to_add=[10,000.00]
 ├─A     level=[1] current_value=[ 1,000.00] optimal_ratio=[0.450] amount_to_add=[     0.00]
 ├─B     level=[1] current_value=[ 1,500.00] optimal_ratio=[0.200] amount_to_add=[     0.00]
 └─C     level=[1] current_value=[ 3,000.00] optimal_ratio=[0.350] amount_to_add=[     0.00]
    ├─Q  level=[2] current_value=[ 1,200.00] optimal_ratio=[0.650] amount_to_add=[     0.00]
    └─R  level=[2] current_value=[ 1,800.00] optimal_ratio=[0.350] amount_to_add=[     0.00]
```

## Output

Given the input above, the amounts to add to each node of the graph are calculated.

```
0        level=[0] results_value=[15,500.00] results_ratio=[1.000] amount_to_add=[     0.00]
 ├─A     level=[1] results_value=[ 6,975.00] results_ratio=[0.450] amount_to_add=[ 5,975.00]
 ├─B     level=[1] results_value=[ 3,100.00] results_ratio=[0.200] amount_to_add=[ 1,600.00]
 └─C     level=[1] results_value=[ 5,425.00] results_ratio=[0.350] amount_to_add=[     0.00]
    ├─Q  level=[2] results_value=[ 3,526.25] results_ratio=[0.650] amount_to_add=[ 2,326.25]
    └─R  level=[2] results_value=[ 1,898.75] results_ratio=[0.350] amount_to_add=[    98.75]
```

The problem can be solved in a constrained way (only add values to buckets) or an unconstrained way (add or remove existing values to buckets).
