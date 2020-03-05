# Xclusion_criteria

Generate interactive, user-defined visualisations to help defining inclusion/exclusion criteria on a metadata table.

## Description

Defining inclusion/exclusion criteria can be trouble some and the subsetting of metadata file for non-expert users 
can be a challenge. This tools allows to apply a series of inclusion/exclusion criteria in a given order and allows
retrieving both the included and excluded sample selection along with user-defined visualization hat allows scrutinizing
categories that miught be of interest for a future study (e.g. to make sure that partucular study groups are balanced.)    

## Installation

```
git clone https://github.com/FranckLejzerowicz/Xclusion_criteria.git
cd Xclusion_criteria
pip install -e .
```

*_Note that python and pip should be python3_

## Input

Metadata table.

- _option_ `-m`: Path to the metadata file (can read a tab-, comma- or semi-colon-separated table. The names will be 
lower-cased and the sample IDs column will be renamed `sample_name`).

Inclusion/Exclusion criteria can be passed either through a simple yaml file (`-y`), or directly in command line (`-c`): 
- _option_ `-y`: Path the a yaml file containing the criteria.
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
    The format is simple and consists in providing 3 information for each variable
    on which to filter (multi-variable  filtering will soon be possible!):
    1. the variable name (as in the metadata but lower case), e.g. `antibiotic_history`
    2. a numeric indicator telling whether the filtering based on the variable's content should be a 
    "remove it", "keep it" or "must be in range",  e.g. the `0` in `antibiotic_history,0:`:
        * "remove it": `0`
        * "keep it": `1`
        * "must be in range": `2`
    3. the list of factors that are considered for the filtering based on the
    variable (must be exactly as in the table), e.g. for `antibiotic_history,0:`
        ```
        - "I have not taken antibiotics in the past year."
        - "Year"
        ```
    For the  numeric indicator `2`, the range **must** be composed of two values:
    a minimum and a maximum (in this order), e.g.
    ```
    age,2:
      - 10
      - 70
    ```
    It is possible to not set a minimum or a maximum bound, by writing "None" instead, e.g.   
    ```
    age,2:
      - 10
      - None
    ```
    (but there must be 2 items...)
    
    The key `no_nan` is special: if present, it lists the variables that will be filtered so that no sample will be left
    that has a _missing value_ for these variables. These _missing values_ are formal NumPy's "nan" (`np.nan`), as
    well as any of these terms:
    - unknown
    - unspecified
    - not provided
    - not applicable
    - missing
    - nan
    
    (this default _missing values_ vocabulary can be edited, in file `./Xclusion_criteria/resources/nulls.txt`)

- _option_ `-c`: One criteria, composed of three space-separated elements (overrides the criteria if exists in the yaml 
file for the same `(variable + selection indicator)`. Can be used multiple times, e.g.
    - `-c sex 1 Male -c age_cat 0 "baby/teen"`. This commands will (i) keep males **and** (ii) remove babies and teens, 
    respectively.
- _option_ `-z`: Path to a yaml file containing the plotting's categorical variables, e.g.:
    ```
    categories:
      - bmi_cat
      - age_years
      - types_of_plants
    ```
    There will be barplot bars for each factor of each of these categorical variables (see image below).
## Outputs

- _option_ `-in`: Metadata table reduced to the samples satisfying all the inclusion criteria (the **selecion**).
- _option_ `-ex`: Metadata table reduced to the samples not satisfying a least one inclusion criteria.
- _option_ `-viz`: Interactive visualization composed of three panels (see below).

## Example

This command:
```
 Xclusion_criteria \
    -m Xclusion_criteria/tests/metadata/md.tsv \
    -y Xclusion_criteria/examples/criteria.yml \
    -z Xclusion_criteria/examples/plot.yml \
    -in Xclusion_criteria/tests/output/md_out.tsv \
    -viz Xclusion_criteria/tests/output/md_viz.html
```
With return this text on your screen:
```
[Warning] Subset values for variable age_cat for not in table
 - teen
 - baby
        Input_metadata_99 -> antibiotic_history_80
        antibiotic_history_80 -> ibd_75
        ibd_75 -> No_age_cat_69
        No_age_cat_69 -> No_bmi_57
```
This tells you about the encountered issues. For our example, there are two inclusion/exclusion criteria factors 
that are not present in the metadata, and therefore that are not accounted for into the filtering/selection process.

#### Interactive visualization

the `-viz` html output has 3 panels:
1. Samples selection progression at each inclusion/exclusion criteria step is reported.
![Selection](./Xclusion_criteria/resources/images/selection_popup.png)
_(interaction: hovering on the steps/dots with the mouse shows
the variable and variable's factors used for selection)_

2. Samples on a scatter plot which x and y axes could be changed using a dropdown menu.
![Dropdown](./Xclusion_criteria/resources/images/dropdown_numeric.png)

3. Barplots showing the number of samples for each of the different factors of the user-defined catergories. By 
 default, these are for all the samples of the final selection. This selection can be further refined by selecting
 samples using click-and-brush on the scatter.
![brush](./Xclusion_criteria/resources/images/brush_samples.png)

### Optional arguments

``` 
  -m, --m-metadata-file TEXT    Metadata file on which to apply
                                included/exclusion criteria.  [required]
  -c, --p-criterion TEXT...     Criterion to use for metadata filtering. Use 3
                                space-separated terms for filtering: (i) the
                                variable, (ii) a numeric indicator (0, 1 or 2)
                                and (iii) the '/'-separated variable factors,
                                e.g.: '-p sample_type 1 Stool' (to include
                                only stool sample types), or '-p sample_type 0
                                Stool/Skin' (to exclude all stool and skin
                                sample types). The '2' indicator indicates a
                                numeric data subsetting. In this case, the
                                '/'-separated variable factors must start with
                                either '>',  '>=', '<' or '<='.
  -y, --i-criteria TEXT         Must be a yaml file (see README or
                                'examples/criteria.yml').
  -z, --i-plot-groups TEXT      Must be a yaml file (see README or
                                'examples/criteria.yml').
  -ex, --o-excluded TEXT        Output metadata for the excluded samples only.
  -in, --o-included TEXT        Output metadata for the included samples only.
                                [required]
  -viz, --o-visualization TEXT  Output metadata explorer for the included
                                samples only.  [required]
  --version                     Show the version and exit.
  --help                        Show this message and exit.
```



### Bug Reports

contact `flejzerowicz@health.ucsd.edu`