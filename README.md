# Xclusion_criteria

Generate interactive, user-defined visualisations to help defining inclusion/exclusion criteria on a metadata table.

## Description

Defining inclusion/exclusion criteria can be trouble some and the subsetting of metadata file for non-expert users 
can be a challenge. This tools allows to apply a series of inclusion/exclusion criteria in a given order and allows
retrieving both the included and excluded sample selection along with user-defined visualization hat allows scrutinizing
categories that miught be of interest for a future study (e.g. to make sure that partucular study groups are balanced.)    

## Installation

```
pip install git+https://github.com/FranckLejzerowicz/Xclusion_criteria.git
```
or 
```
pip install --upgrade git+https://github.com/FranckLejzerowicz/Xclusion_criteria.git
```

*_Note that python and pip should be python3_

## Input

- 
```
antibiotic_history,0:
  - "I have not taken antibiotics in the past year."
  - "Year"
ibd,0:
  - "I do not have this condition"
age_cat,0:
  - NULLS
  - "70+"
  - "child"
  - "teen"
  - "baby"
no_nan:
  - bmi
```

## Outputs



### Optional arguments

``` 
  -m, --m-metadata-file TEXT  Metadata file on which to apply
                              included/exclusion criteria.  [required]
  -c, --p-criterion TEXT...   Criterion to use for metadata filtering. Use 3
                              space-separated terms for filtering: (i) the
                              variable, (ii) a numeric indicator (0, 1 or 2)
                              and (iii) the '/'-separated variable factors,
                              e.g.: '-p sample_type 1 Stool' (to include only
                              stool sample types), or '-p sample_type 0
                              Stool/Skin' (to exclude all stool and skin
                              sample types). The '2' indicator indicates a
                              numeric data subsetting. In this case, the
                              '/'-separated variable factors must start with
                              either '>',  '>=', '<' or '<='.
  -y, --p-criteria TEXT       Must be a yaml file (see README or
                              'examples/criteria.yml').
  -ex, --o-excluded TEXT      Output metadata for the excluded samples only.
  -in, --o-included TEXT      Output metadata for the included samples only.
  --version                   Show the version and exit.
  --help                      Show this message and exit.

```



### Bug Reports

contact `flejzerowicz@health.ucsd.edu`