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

RESOURCES = pkg_resources.resource_filename('Xclusion_criteria', 'resources')


def xclusion_criteria(
        m_metadata_file: str,
        i_criteria: str,
        i_plot_groups: str,
        o_included: str,
        o_excluded: str,
        o_visualization: str,
        random_samples: bool) -> None:
    """Main script for running the inclusion/exclusion
     criteria-based filtering on a metadata table.

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
    random_samples : bool
        Whether to reduce visualization to 100 random samples or not.

    """

    nulls = [x.strip() for x in open('%s/nulls.txt' % RESOURCES).readlines()]
    metadata = read_meta_pd(m_metadata_file)
    messages = []

    # get yml content, i.e. all inclusion/exclusion criteria.
    criteria = get_criteria(i_criteria, metadata, nulls, messages)
    if not criteria:
        print('No single criteria found: check input path / content\nExiting')
        sys.exit(1)
    # show yml criteria file formatting errors
    if messages:
        print('Problems encountered during criteria parsing:')
        for message in messages:
            print(message)
        messages = []

    # infer dtypes
    dtypes = get_dtypes(metadata, nulls)

    # get the numerical and categorical metadata variables
    numerical, categorical = [], []
    split_variables_types(dtypes, numerical, categorical)

    # Check there's min 3 categorical and 2 numerical variables
    num_cat_bool, num_cat_message = check_num_cat_lists(numerical, categorical)
    # show categorical/numerical variables concern
    if num_cat_bool:
        print(num_cat_message)
        print('! Not enough categorical/numerical variables -> producing a figure !')

    # Apply filtering criteria to subset the metadata
    # -> get filtering flowchart and metadata for criteria-included samples
    flowcharts, included = apply_criteria(metadata, criteria, numerical, messages)
    if messages:
        print('Problems encountered during application of criteria:')
        for message in messages:
            print(message)

    # write the metadata for criteria-included samples
    included.reset_index().to_csv(o_included, index=False, sep='\t')

    # write the metadata for criteria-excluded samples if requested
    if o_excluded:
        excluded = metadata.loc[[x for x in metadata.index if x not in included.index],:].copy()
        excluded.reset_index().to_csv(o_excluded, index=False, sep='\t')

    if not num_cat_bool:
        # Build the three-panel criteria-based filtering figure
        make_visualizations(
            included, i_plot_groups, o_visualization,
            numerical, categorical, flowcharts, random_samples)
