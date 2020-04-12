# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import yaml
import subprocess
from os.path import splitext

# import something for reading qiime2 metadata
import pandas as pd
from os.path import isfile


def read_i_criteria(i_criteria: str) -> dict:
    """Read the yaml criteria file.

    Parameters
    ----------
    i_criteria: str
        Path to yml config file for the different
        inclusion/exclusion criteria to apply.
    Returns
    -------
    parsed_criteria : dict
        Key     = variable,indicator.
        Value   = list of factors to use for filtering.
    """
    parsed_criteria = {}
    if i_criteria and isfile(i_criteria):
        with open(i_criteria) as handle:
            parsed_criteria = yaml.load(handle, Loader=yaml.FullLoader)
    return parsed_criteria


def read_meta_pd(metadata_file: str) -> pd.DataFrame:
    """
    Read metadata with first column as index.

    Parameters
    ----------
    metadata_file : str
        Path to metadata file on which to apply included/exclusion criteria.

    Returns
    -------
    metadata : pd.DataFrame
        Metadata table.
    """
    with open(metadata_file) as f:
        for line in f:
            break
    header = line.strip()
    for sep in ['\t', ';', ',']:
        if len(header.split(sep))>1 and len(header.split(sep)) == (header.count(sep)+1):
            first_col = line.split(sep)[0]
            break
    else:
        print('no separator found among: "<tab>", ",", ";"\nExiting')
        sys.exit(1)
    meta_pd = pd.read_csv(metadata_file, header=0, sep=sep,
                          dtype={first_col: str}, low_memory=False)
    meta_pd.rename(columns={first_col: 'sample_name'}, inplace=True)
    meta_pd.set_index('sample_name', inplace=True)
    meta_pd.columns = [x.lower() for x in meta_pd.columns]
    # remove NaN only columns
    meta_pd = meta_pd.loc[:,~meta_pd.isna().all()]
    return meta_pd


def fetch_data(
        o_included: str,
        flowcharts: dict,
        o_metadata_file: str,
        o_biom_file: str,
        p_redbiom_context: str,
        p_bloom_sequences: str,
        p_reads_filter: int,
        unique: bool,
        update: bool,
        dim: bool) -> pd.DataFrame:
    """

    Parameters
    ----------
    o_included : str
        Path to output metadata for the included samples only.
    flowcharts : dict
        Steps of the workflow with samples counts (simpler representation).
    o_metadata_file : str
        [if --fetch] Path to the output metadata table file.
    o_biom_file : str
        [if --fetch] Path to the output biom table file.
    p_redbiom_context : str
        [if --fetch] Redbiom context for fetching 16S data from Qiita.
    p_bloom_sequences : str
        [if --fetch] Fasta file containing the sequences known
        to bloom in fecal samples.
    p_reads_filter : int
        [if --fetch] Minimum number of reads per sample.
    unique : bool
        [if --fetch] Whether to keep a unique sample per host or not.
    update : bool
        [if --fetch] Update the sample names to remove Qiita-prep info.
    dim : bool
        [if --fetch] Whether to add the number of samples in the final
        biom file name before extension or not.

    Returns
    -------
    included : pd.DataFrame
        Metadata for the included samples only.
    """
    cmd = 'Xrbfetch'
    cmd += ' -m %s' % o_included
    if o_metadata_file:
        o_meta = o_metadata_file
    else:
        o_meta = '%s_fetched.tsv' % splitext(o_included)[0]
    cmd += ' -o %s' % o_meta
    if o_biom_file:
        cmd += ' -b %s' % o_biom_file
    else:
        cmd += ' -b %s_fetched.biom' % splitext(o_included)[0]
    if p_bloom_sequences:
        cmd += ' -s %s' % p_bloom_sequences
    cmd += ' -r %s' % p_redbiom_context
    cmd += ' -f %s' % p_reads_filter
    if unique:
        cmd += ' --unique'
    if update:
        cmd += ' --update'
    if dim:
        cmd += ' --dim'
    cmd += ' --force'
    cmd += ' --no-simple'
    print('- fetch on redbiom:')
    redbiom_fetching = subprocess.getoutput(cmd).split('\n')
    print('Done.')

    flowcharts['data'] = []
    print(redbiom_fetching)
    for step in redbiom_fetching:
        step_line = step.strip()
        if step_line.startswith('- Load biom table...'):
            print('1', step_line)
            n = step_line.split()[6]
            flowcharts['data'].append(['Fetch', n, 'redbiom', p_redbiom_context, None])
        elif step_line.startswith('- filter blooms...'):
            print('2', step_line)
            n = step_line.split()[5]
            flowcharts['data'].append(['Filter blooms', n, None, None, None])
        elif step_line.startswith('- Filter biom for best sample...'):
            print('3', step_line)
            n = step_line.split()[8]
            flowcharts['data'].append(['Solve redbiom ambiguous', n, 'most reads', '...or... ', 'most features'])
        elif step_line.startswith('- Merge reads and features counts to metadata...'):
            print('4', step_line)
            n = step_line.split()[10]
            flowcharts['data'].append(['Metadata merge', n, None, None, None])
        elif step_line.startswith('- Filter biom for min'):
            print('5', step_line)
            f = step_line.split()[5]
            n = step_line.split()[11]
            flowcharts['data'].append(['Filter reads', n, 'min %s' % f, None])
        elif step_line.startswith('* Keep the best host_subject_id per sample...'):
            print('6', step_line)
            n = step_line.split()[9]
            flowcharts['data'].append(['One per host', n, None, None, None])
        elif step_line.startswith('* Keep the best working_sample_name per sample...'):
            print('7', step_line)
            n = step_line.split()[9]
            flowcharts['data'].append(['One per sample ID', n, None, None, None])

    if redbiom_fetching[-3].startswith(' - Write files:'):
        included = read_meta_pd(redbiom_fetching[-2].split()[-1])
        return included
    else:
        print('nothing fetched: check command:\n%s\nExiting...' % cmd)
        sys.exit(1)


def parse_plot_groups(i_plot_groups: str) -> dict:
    """
    Get the groups to plots for each barplots and scatters.

    Parameters
    ----------
    i_plot_groups : str
        Path to yml config file for the different groups to visualize.

    Returns
    -------
    plot_groups : dict
        Groups (values) for barplots and scatters (keys).
    """
    plot_groups = {}
    if i_plot_groups and isfile(i_plot_groups):
        with open(i_plot_groups) as handle:
            plot_groups.update(yaml.load(handle, Loader=yaml.FullLoader))

    for num_cat in ['categorical', 'numerical']:
        if num_cat in plot_groups:
            if not isinstance(plot_groups[num_cat], list):
                print('%s variables provided in "%s" must be in a list (see docs)' % (num_cat, i_plot_groups))
                sys.exit(1)
            plot_groups[num_cat] = [x.lower() for x in plot_groups[num_cat]]

    return plot_groups
