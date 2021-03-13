# Xclusion_criteria

Generate interactive, user-defined visualisations to help defining 
inclusion/exclusion criteria on a metadata table.

## Description

Defining inclusion/exclusion criteria can be trouble some and the 
subsetting of metadata file for non-expert users can be a challenge. 
This tools allows to apply a series of inclusion/exclusion criteria 
in a given order and allows retrieving both the included and excluded 
sample selection along with user-defined visualization hat allows 
scrutinizing categories that might be of interest for a future study 
(e.g. to make sure that particular study groups are balanced.)

## Installation

```
git clone https://github.com/FranckLejzerowicz/Xclusion_criteria.git
cd Xclusion_criteria
pip install -e .
```
and then if there are updates
```
pip install --upgrade git+https://github.com/FranckLejzerowicz/Xclusion_criteria.git
```

*_Note that python and pip should be python3_

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

- **[REQUIRED]** _option_ `-in`: Metadata table reduced to the samples satisfying all the inclusion criteria (the **selecion**).
- _option_ `-ex`: Metadata table reduced to the samples not satisfying a least one inclusion criteria.
- _option_ `-v`: Interactive visualization composed of three panels (see below).

## Example

This command:
```
 Xclusion_criteria \
    -m Xclusion_criteria/tests/metadata/md.tsv \
    -c Xclusion_criteria/examples/criteria_nonempty_output.yml \
    -p Xclusion_criteria/examples/plot.yml \
    -in Xclusion_criteria/tests/output/md_out.tsv \
    -v Xclusion_criteria/tests/output/md_viz.html
```
Prints out:
```
- read input metadata... Done.
- get yml content, i.e. all inclusion/exclusion criteria...
Problems encountered during criteria parsing:
[Warning] Subset values for variable age_cat not in table
 - teen
 - baby
- infer dtypes... Done.
- get the numerical and categorical metadata variables... Done.
- apply filtering criteria to subset the metadata... Done.
- write the metadata for criteria-included samples... Done.
- check there are min 3 categorical and 2 numerical variables...
  [numerical] age_years (n=16/16)
  ...
  [numerical] weight_kg (n=16/16)

  [categorical] acne_medication (n=1: No:15)
  ...
  [categorical] whole_grain_frequency (n=2: Never:2,Occasional:1)
- build the three-panel criteria-based filtering figure...
 --> 3 passed "numerical" variables that are not numerical:
        * vioscreen_micromacro__added_sugars__by_total_sugars__in_g
        * vioscreen_micromacro__energy_in_kcal
        * vioscreen_micromacro__alcohol_in_g
Start making the chart (html) figure
   * make filtering figure... Done
 - get numeric melted table... 
 - get categorical melted table... 
 - merge numeric and categorical tables... 
   * make scatter figure... Done
   * make barplots figure...Done
 - Write figure... Done: Xclusion_criteria/tests/output/md_viz.html
```


#### Interactive visualization

the `-o` html output has 3 panels:
1. Samples selection progression at each inclusion/exclusion criteria step is reported.
![Selection](./Xclusion_criteria/resources/images/selection_popup.png)
_(interaction: hovering on the steps/dots with the mouse shows
the variable and variable's factors used for selection)_

2. Samples on a scatter plot which x and y axes could be changed using a dropdown menu.
![Dropdown](./Xclusion_criteria/resources/images/dropdown_numeric.png)

3. Barplots showing the number of samples for each of the different factors of the user-defined categories. By 
 default, these are for all the samples of the final selection. This selection can be further refined by selecting
 samples using click-and-brush on the scatter.
![brush](./Xclusion_criteria/resources/images/brush_samples.png)


## Data fetching

It is possible to perform the downloading and filtering of the microbiome data 
directly, and perform filtering, by subprocessing another unittested package: 
[Xrbfetch](https://github.com/FranckLejzerowicz/Xrbfetch). It applies "technical"
exclusion criteria on the microbiome data (while the above only appl) yield sample counts 
change that are also plotted, and are given in command line:

Parameters:
  - _option_ `--fetch`: fetch data using [redbiom](https://github.com/biocore/redbiom) using 
  [Xrbfetch](https://github.com/FranckLejzerowicz/Xrbfetch)
  - _option_ `-r`: data to fetch, default is `Deblur-Illumina-16S-V4-150nt-780653`
  - _option_ `-s`: fasta file with sequences to filter out (see default at [Xrbfetch](https://github.com/FranckLejzerowicz/Xrbfetch))
  - _option_ `-f`: minimum number of reads for samples to filter out
  - _option_ `--unique`: keep only one sample per host (most reads / features
  - _option_ `--update`: update sample names to get rid of Qiita-prep info
  (e.g. from `10317.000048372.84675` to `10317.000048372`)

Output:    
  - _option_ `-b`: Biom file containing fetched and filtered data
  - _option_ `-o`: Output metadata for the samples which data could be fetched

## Example with data fetching

This command:
```
 Xclusion_criteria \
    -m Xclusion_criteria/tests/metadata/md.tsv \
    -c Xclusion_criteria/examples/criteria_nonempty_output.yml \
    -p Xclusion_criteria/examples/plot.yml \
    -in Xclusion_criteria/tests/output/md_out.tsv \
    -v Xclusion_criteria/tests/output/md_viz.html \
    --fetch \
    -o Xclusion_criteria/tests/output/md_fetch_metadata.tsv \
    -b Xclusion_criteria/tests/output/md_fetch_data.biom \
```

Prints out:
```
- read input metadata... Done.
- get yml content, i.e. all inclusion/exclusion criteria...
Problems encountered during criteria parsing:
[Warning] Subset values for variable age_cat not in table
 - teen
 - baby
- infer dtypes... Done.
- get the numerical and categorical metadata variables... Done.
- apply filtering criteria to subset the metadata... Done.
- write the metadata for criteria-included samples... Done.
- check there are min 3 categorical and 2 numerical variables...
  [numerical] age_years (n=16/16)
  ...
  [numerical] weight_kg (n=16/16)

  [categorical] acne_medication (n=1: No:15)
  ...
  [categorical] whole_grain_frequency (n=2: Never:2,Occasional:1)
- build the three-panel criteria-based filtering figure...
 --> 3 passed "numerical" variables that are not numerical:
        * vioscreen_micromacro__added_sugars__by_total_sugars__in_g
        * vioscreen_micromacro__energy_in_kcal
        * vioscreen_micromacro__alcohol_in_g
Start making the chart (html) figure
   * make filtering figure... Done
 - get numeric melted table... 
 - get categorical melted table... 
 - merge numeric and categorical tables... 
   * make scatter figure... Done
   * make barplots figure...Done
 - Write figure... Done: Xclusion_criteria/tests/output/md_viz.html
```



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
  -v, --o-visualization TEXT    Output metadata explorer for the included
                                samples only.

  -r, --p-random INTEGER        Reduce visualization to the passed number of
                                (random) samples.  [default: 100]

  --fetch / --no-fetch          Run Xrbfetch (third-party) to get features
                                data.  [default: False]

  -o, --o-metadata-file TEXT    [if --fetch] Path to the output metadata table
                                file. (Default = add _fetched_#s.tsv).

  -b, --o-biom-file TEXT        [if --fetch] Path to the output biom table
                                file. (Default = add _fetched_#s.biom).

  -x, --p-redbiom-context TEXT  [if --fetch] Redbiom context for fetching 16S
                                data from Qiita.  [default: Deblur-
                                Illumina-16S-V4-150nt-780653]

  -s, --p-bloom-sequences TEXT  [if --fetch] Fasta file containing the
                                sequences known to bloom in fecal samples
                                (defaults to 'newblooms.all.fasta' file from
                                Xrbfetch package's folder 'resources').

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

  --version                     Show the version and exit.
  --help                        Show this message and exit.

```



### Bug Reports

contact `flejzerowicz@health.ucsd.edu`