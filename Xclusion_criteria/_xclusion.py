# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import pkg_resources
from os.path import splitext

from Xclusion_criteria._xclusion_io import read_meta_pd
from Xclusion_criteria._xclusion_dtypes import get_dtypes, split_variables_types, check_num_cat_lists
from Xclusion_criteria._xclusion_crits import get_criteria, apply_criteria
from Xclusion_criteria._xclusion_plot import make_visualizations
from Xclusion_criteria._xclusion_fetch import fetch_redbiom

RESOURCES = pkg_resources.resource_filename('Xclusion_criteria', 'resources')


def xclusion_criteria(
        m_metadata_file: str,
        i_criteria: str,
        i_plot_groups: str,
        o_included: str,
        o_excluded: str,
        o_visualization: str,
        fetch: bool,
        p_redbiom_context: str,
        p_bloom_sequences: str,
        p_reads_filter: int,
        unique: bool,
        update: bool,
        dim: bool,
        verbose: bool) -> None:
    """
    Main script for running inclusion/exclusion criteria on a metadata table.

    Parameters
    ----------
    m_metadata_file : str
        Path to metadata file on which to apply included/exclusion criteria.
    i_criteria: str
        Path to yml config file for the different inclusion/exclusion criteria to apply.
    i_plot_groups : str
        Path to yml config file for the different groups to visualize.
    o_included : str
        Path to output metadata for the included samples only.
    o_excluded : str
        Path to output metadata for the excluded samples only.
    o_visualization : str
        Path to output visualization for the included samples only.
    fetch : bool
        Whether to get the 16S data from RedBiom (and apply microbiome filters) or not.
    p_redbiom_context : str
        Redbiom context for fetching 16S data from Qiita.
    p_bloom_sequences : str
        Fasta file containing the sequences known to bloom in fecal samples.
    p_reads_filter : int
        Minimum number of reads per sample.
    unique : bool
        Whether to keep a unique sample per host or not.
    update : bool
        Update the sample names to remove Qiita-prep info.
    dim : bool
        Whether to add the number of samples in the final biom file name before extension or not.
    verbose : bool
        Whether to show missing, non-fetched samples and duplicates or not.
    """
    nulls = [x.strip() for x in open('%s/nulls.txt' % RESOURCES).readlines()]

    metadata = read_meta_pd(m_metadata_file)

    messages, numerical, categorical = [], [], []
    criteria = get_criteria(i_criteria, metadata, nulls, messages)
    if not criteria:
        print('No single criteria found: check input path / content\nExiting')
        sys.exit(1)
    if messages:
        print('Problems encountered during criteria parsing:')
        for message in messages:
            print('; '.join(message))
        messages = []

    dtypes = get_dtypes(metadata, nulls)
    split_variables_types(dtypes, criteria, numerical, categorical)
    num_cat_bool, num_cat_message = check_num_cat_lists(numerical, categorical, messages)
    if num_cat_bool:
        print(num_cat_message)
        print('  -> Not producing a figure')

    flowcharts, included = apply_criteria(metadata, criteria, numerical, messages)
    if messages:
        print('Problems encountered during application of criteria:')
        for message in messages:
            print(message)
    included.reset_index().to_csv(o_included, index=False, sep='\t')

    excluded = metadata.loc[[x for x in metadata.index if x not in included.index],:].copy()
    excluded.reset_index().to_csv(o_excluded, index=False, sep='\t')

    if not num_cat_bool:
        make_visualizations(included, i_plot_groups, o_visualization,
                            numerical, categorical, flowcharts)
    if fetch:
        fetch_redbiom(o_included, p_redbiom_context, p_bloom_sequences,
                      p_reads_filter, unique, update, dim, verbose)