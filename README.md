# Xclusion_criteria

Generate interactive, user-defined visualisations to help defining 
inclusion/exclusion criteria on a metadata table.

## Description

Defining inclusion/exclusion criteria can be trouble some and the 
subsetting of metadata file for non-expert users can be a challenge. 
This tools allows to apply a series of inclusion/exclusion criteria 
in a given order and allows retrieving both the included and excluded 
sample selection along with user-defined visualization hat allows 
scrutinizing categories that miught be of interest for a future study 
(e.g. to make sure that particular study groups are balanced.)

Optionally, the tool can also fetch from Qiita the 16S data for the 
samples left in the selection and apply basic filters on it (for this, the 
thrid-party tool [Xrbfetch](https://github.com/FranckLejzerowicz/Xrbfetch)
must be installed).

## Installation

```
git clone https://github.com/FranckLejzerowicz/Xclusion_criteria.git
cd Xclusion_criteria
pip install -e .
```

*_Note that python and pip should be python3_

#### Requisites

If you want to make use of the functionality allowinf the fetching of 
16S data from Qiita, please install [Xrbfetch](https://github.com/FranckLejzerowicz/Xrbfetch)

## Input

- **[REQUIRED]** _option_ `-m`: Path to the metadata file (can read a tab-, comma- 
or semi-colon-separated table. The names will be  lower-cased and 
the sample IDs column will be renamed `sample_name`).

- **[REQUIRED]** _option_ `-c`: Path the a yaml file containing the criteria.
    ```
    init:
      antibiotic_history,1:
        - 'I have not taken antibiotics in the past year.'
        - 'Year'
      age_cat,0:
        - 'NULLS'
        - '70+'
        - 'child'
        - 'teen'
        - 'baby'
      bmi,2:
        - '18'
        - 'None'
    add:
      alcohol_consumption,1:
        - 'No'
    filter:
      alcohol_types_red_wine,1:
        - 'Yes'
    no_nan:
      - bmi
    ```
    There are four possible main filtering steps:
    - `init`
    - `add`
    - `filter`
    - `no_nan`
    
    For the three first steps (`init`, `add` and `filter`), the format is exactly 
    the  same and consists in providing 3 pieces of information for each variable
    based on which to filter (_multi-variable filtering will soon be possible!_):
    1. the variable name (as in the metadata but lower case), e.g. `antibiotic_history`
    2. a numeric indicator telling whether the filtering based on the variable's content 
    should be a  "remove it", "keep it" or "must be in range", e.g. the `0` in 
    `antibiotic_history,0:`:
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
    
    The fourth key `no_nan` is special: if present, it lists the variables that will be 
    filtered so that no sample will be left that has a _missing value_ for these variables. 
    These _missing values_ are formal NumPy's "nan" (`np.nan`), as well as any of these terms:
    - unknown
    - unspecified
    - not provided
    - not applicable
    - missing
    - nan
    
    (this default _missing values_ vocabulary can be edited, 
    in file `./Xclusion_criteria/resources/nulls.txt`)

- _option_ `-p`: Path to a yaml file containing the plotting's categorical variables, e.g.:
    ```
    categories:
      - bmi_cat
      - age_years
      - types_of_plants
    ```
    There will be barplot bars for each factor of each 
    of these categorical variables (see image below).

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
Usage: Xclusion_criteria [OPTIONS]

Options:
  -m, --m-metadata-file TEXT    Metadata file on which to apply
                                included/exclusion criteria.  [required]
  -c, --i-criteria TEXT         Must be a yaml file (see README or
                                'examples/criteria.yml').  [required]
  -p, --i-plot-groups TEXT      Must be a yaml file (see README or
                                'examples/criteria.yml').
  -in, --o-included TEXT        Output metadata for the included samples only.
                                [required]
  -ex, --o-excluded TEXT        Output metadata for the excluded samples only.
  -viz, --o-visualization TEXT  Output metadata explorer for the included
                                samples only.  [required]
  --fetch / --no-fetch          Get the 16S data from RedBiom and apply
                                microbiome filters.  [default: False]
  -r, --p-redbiom-context TEXT  [if --fetch] Redbiom context for fetching 16S
                                data from Qiita.  [default: Deblur-
                                Illumina-16S-V4-150nt-780653]
  -b, --p-bloom-sequences TEXT  [if --fetch] Fasta file containing the
                                sequences known to bloom in fecal samples
                                (defaults to 'newblooms.all.fasta' file from
                                package's folder 'resources').
  -f, --p-reads-filter INTEGER  [if --fetch] Minimum number of reads per
                                sample.  [default: 1500]
  --unique / --no-unique        [if --fetch] Keep a unique sample per host
                                (most read, or most features).  [default:
                                True]
  --update / --no-update        [if --fetch] Update the sample names to remove
                                Qiita-prep info.  [default: True]
  --dim / --no-dim              [if --fetch] Add the number of samples in the
                                final biom file name before extension (e.g.
                                for '-b out.biom' it becomes
                                'out_1000s.biom').  [default: True]
  --verbose / --no-verbose      [if --fetch] Show missing, non-fetched samples
                                and duplicates.  [default: True]
  --version                     Show the version and exit.
  --help                        Show this message and exit.
```



### Bug Reports

contact `flejzerowicz@health.ucsd.edu`