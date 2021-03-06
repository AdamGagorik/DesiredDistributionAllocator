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
# The problem will be solved in an unconstrained way by default
# Values can be added or removed from existing bins
python -m allocate --config allocate.yaml

# The problem can be solved in a constrained way as well
# Values can only be added to bins
python -m allocate --config allocate.yaml --constrained

# A Monte Carlo based solver also exists, which is non-deterministic
# Values can be added in fixed sizes
python -m allocate --config allocate.yaml --constrained --montecarlo --stepsize 25
```

## Input

The input is a hierarchy of bins with current values and desired ratios.

#### yaml

The input can be given as a YAML file.

```yaml
- { label: 'TOTAL', optimal_ratio: 100, current_value: 6000, amount_to_add: 8000, children: [
    'VIGAX', 'VVIAX', 'VMGMX', 'VMVAX', 'VSGAX', 'VSIAX'] }
- { label: 'VIGAX', optimal_ratio:  22, current_value: 1000, amount_to_add:    0, children: [] }
- { label: 'VVIAX', optimal_ratio:  28, current_value: 1000, amount_to_add:    0, children: [] }
- { label: 'VMGMX', optimal_ratio:  10, current_value: 1000, amount_to_add:    0, children: [] }
- { label: 'VMVAX', optimal_ratio:  15, current_value: 1000, amount_to_add:    0, children: [] }
- { label: 'VSGAX', optimal_ratio:  10, current_value: 1000, amount_to_add:    0, children: [] }
- { label: 'VSIAX', optimal_ratio:  15, current_value: 1000, amount_to_add:    0, children: [] }
```

You can use regular expressions when specifying the children of a category.

```yaml
- { label: 'TOTAL', optimal_ratio: 100, current_value: 6000, amount_to_add: 8000, children: ['regex::.*'] }
...
```

#### csv

The input can be given as a CSV file.

```csv
   label  optimal_ratio  current_value  amount_to_add                             children
0  TOTAL          100.0         6000.0         8000.0  VIGAX;VVIAX;VMGMX;VMVAX;VSGAX;VSIAX
1  VIGAX           22.0         1000.0            0.0
2  VVIAX           28.0         1000.0            0.0
3  VMGMX           10.0         1000.0            0.0
4  VMVAX           15.0         1000.0            0.0
5  VSGAX           10.0         1000.0            0.0
6  VSIAX           15.0         1000.0            0.0
```

#### graph

The following graph will be generated from the above input.

```
TOTAL     level=[0] current_value=[ 6,000.00] optimal_ratio=[1.000] amount_to_add=[ 8,000.00]
 ??????VIGAX  level=[1] current_value=[ 1,000.00] optimal_ratio=[0.220] amount_to_add=[     0.00]
 ??????VVIAX  level=[1] current_value=[ 1,000.00] optimal_ratio=[0.280] amount_to_add=[     0.00]
 ??????VMGMX  level=[1] current_value=[ 1,000.00] optimal_ratio=[0.100] amount_to_add=[     0.00]
 ??????VMVAX  level=[1] current_value=[ 1,000.00] optimal_ratio=[0.150] amount_to_add=[     0.00]
 ??????VSGAX  level=[1] current_value=[ 1,000.00] optimal_ratio=[0.100] amount_to_add=[     0.00]
 ??????VSIAX  level=[1] current_value=[ 1,000.00] optimal_ratio=[0.150] amount_to_add=[     0.00]
```

## Output

Given the input above, the amounts to add to each node of the graph are calculated.

```
TOTAL     level=[0] results_value=[14,000.00] results_ratio=[1.000] amount_to_add=[     0.00]
 ??????VIGAX  level=[1] results_value=[ 3,080.00] results_ratio=[0.220] amount_to_add=[ 2,080.00]
 ??????VVIAX  level=[1] results_value=[ 3,920.00] results_ratio=[0.280] amount_to_add=[ 2,920.00]
 ??????VMGMX  level=[1] results_value=[ 1,400.00] results_ratio=[0.100] amount_to_add=[   400.00]
 ??????VMVAX  level=[1] results_value=[ 2,100.00] results_ratio=[0.150] amount_to_add=[ 1,100.00]
 ??????VSGAX  level=[1] results_value=[ 1,400.00] results_ratio=[0.100] amount_to_add=[   400.00]
 ??????VSIAX  level=[1] results_value=[ 2,100.00] results_ratio=[0.150] amount_to_add=[ 1,100.00]
```
