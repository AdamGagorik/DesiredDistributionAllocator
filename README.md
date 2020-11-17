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
python -m allocate --config allocate.yaml
```

## Input

```yaml
# allocate.yaml
```
