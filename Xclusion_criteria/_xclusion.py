# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pkg_resources

from Xclusion_criteria._xclusion_md import read_meta_pd
from Xclusion_criteria._xclusion_dtypes import get_dtypes, split_variables_types
from Xclusion_criteria._xclusion_crits import get_criteria, apply_criteria
from Xclusion_criteria._xclusion_plot import make_visualizations, show_flowchart

RESOURCES = pkg_resources.resource_filename('Xclusion_criteria', 'resources')


def xclusion_criteria(
        m_metadata_file: str,
        p_criterion: tuple,
        i_criteria: str,
        o_excluded: str,
        o_included: str,
        i_plot_groups: str,
        o_visualization: str) -> None:
    """
    Main script for running inclusion/exclusion criteria on a metadata table.

    Parameters
    ----------
    m_metadata_file : str
        Path to metadata file on which to apply included/exclusion criteria.
    p_criterion : tuple
        Inclusion/exclusion criteria to apply directly passed from command line.
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
    """
    nulls = [x.strip() for x in open('%s/nulls.txt' % RESOURCES).readlines()]

    metadata = read_meta_pd(m_metadata_file)
    criteria = get_criteria(p_criterion, i_criteria, metadata, nulls)

    dtypes = get_dtypes(metadata, nulls)
    numerical, categorical = split_variables_types(dtypes, criteria)

    flowchart, flowchart2, included = apply_criteria(metadata, criteria, list(categorical))
    included.reset_index().to_csv(o_included, index=False, sep='\t')
    show_flowchart(list(flowchart))

    excluded = metadata.loc[[x for x in metadata.index if x not in included.index],:].copy()
    excluded.reset_index().to_csv(o_excluded, index=False, sep='\t')

    make_visualizations(included, i_plot_groups, o_visualization,
                        list(numerical), list(categorical), list(flowchart2))