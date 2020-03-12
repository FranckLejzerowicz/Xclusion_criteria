# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import pkg_resources

from Xclusion_criteria._xclusion_io import read_meta_pd
from Xclusion_criteria._xclusion_dtypes import get_dtypes, split_variables_types, check_num_cat_lists
from Xclusion_criteria._xclusion_crits import get_criteria, apply_criteria
from Xclusion_criteria._xclusion_plot import make_visualizations
from Xclusion_criteria._xclusion_data import fetch_redbiom

RESOURCES = pkg_resources.resource_filename('Xclusion_criteria', 'resources')


def xclusion_criteria(
        m_metadata_file: str,
        i_criteria: str,
        o_excluded: str,
        o_included: str,
        i_plot_groups: str,
        o_visualization: str,
        p_redbiom_context: str,
        p_bloom_sequences: str,
        unique: bool,
        fetch: bool) -> None:
    """
    Main script for running inclusion/exclusion criteria on a metadata table.

    Parameters
    ----------
    m_metadata_file : str
        Path to metadata file on which to apply included/exclusion criteria.
    i_criteria: str
        Path to yml config file for the different inclusion/exclusion criteria to apply.
    o_excluded : str
        Path to output metadata for the excluded samples only.
    o_included : str
        Path to output metadata for the included samples only.
    i_plot_groups : str
        Path to yml config file for the different groups to visualize.
    o_visualization : str
        Path to output visualization for the included samples only.
    p_redbiom_context : str
        Redbiom context for fetching 16S data from Qiita.
    p_bloom_sequences : str
        Fasta file containing the sequences known to bloom in fecal samples.
    unique : bool
        Whether to keep a unique sample per host or not.
    fetch : bool
        Whether to get the 16S data from RedBiom (and apply microbiome filters) or not.
    """
    nulls = [x.strip() for x in open('%s/nulls.txt' % RESOURCES).readlines()]

    metadata = read_meta_pd(m_metadata_file)

    messages, numerical, categorical = [], [], []
    criteria = get_criteria(i_criteria, metadata, nulls, messages)

    dtypes = get_dtypes(metadata, nulls)
    split_variables_types(dtypes, criteria, numerical, categorical)
    if check_num_cat_lists(numerical, categorical, messages):
        print('Exiting')
        sys.exit(1)

    flowcharts, included = apply_criteria(metadata, criteria, numerical, messages)
    included.reset_index().to_csv(o_included, index=False, sep='\t')

    excluded = metadata.loc[[x for x in metadata.index if x not in included.index],:].copy()
    excluded.reset_index().to_csv(o_excluded, index=False, sep='\t')

    make_visualizations(included, i_plot_groups, o_visualization,
                        numerical, categorical, flowcharts)

    if fetch:
        fetch_redbiom(included, o_included, p_redbiom_context, p_bloom_sequences, unique)